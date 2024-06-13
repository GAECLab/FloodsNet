# Run with the below per data set:
# python -m floodsnet -dt=world_floods
# python -m floodsnet -dt=sen1_floods11
# python -m floodsnet -dt=usgs
# python -m floodsnet -dt=unosat
# if not using the default folders, pls see cli.py for how to specify
# your folders; for example,
# python -m floodsnet -dt=unosat --generated_path='path/to/img downloads/gdrive folder'
# for example:
# python -m floodsnet -dt=unosat --generated_path='/Volumes/GoogleDrive/My Drive/projects'

import os
from glob import glob
from pathlib import Path

import ee
import geopandas as gpd

from .calculate_classes import calc_classes
from .calculate_features import calc_ndwi
from .cli import parse_flood_training_data_args
from .gee_sentinel1_download import download_s1_imgs
from .gee_sentinel2_download import download_s2_imgs
from .geetasks import check_on_tasks_in_queue, wait_for_local_sync
from .get_imgs import (get_ground_truth,
                       get_s2_imgs,
                       get_s1_imgs,
                       get_jrc_imgs,
                       get_img_date_bbox,
                       get_metadata)
from .paths import dataset_paths, get_s2_jrc_s1_indexes, setup_dirs
from .s2_functions import reproj_rename_s2, resample_to_s2
from .seasonal_water_jrc import download_seasonal_jrc_imgs
from .tools import gdal_wait, img_rename, rename_from_dict
from .unosat_functions import (get_flood_layers_from_unosat_gdbs,
                               validate_date,
                               rasterize_shp)

args = parse_flood_training_data_args()
generated_img_path = args.generated_path
print("generated_img_path is ", generated_img_path)


def main():
    # initialize Google Earth Engine
    ee.Initialize()
    # get paths to various input sources
    args = parse_flood_training_data_args()
    dt_set = args.dt_set
    out_dir = args.out_dir

    # if output directory does not exist, create it
    os.makedirs(out_dir, exist_ok=True)

    rename_dict = {}

    if dt_set != 'all':
        dt_set_lst = [dt_set]
    else:
        dt_set_lst = ['world_floods', 'sen1_floods11', 'usgs', 'unosat']

    for dt_set in dt_set_lst:
        print(f'Starting {dt_set} processing.')
        # check for or make all needed dirs
        setup_dirs(generated_img_path, dt_set)
        dataset_paths_dict = dataset_paths(dt_set, generated_img_path)
        s1_img_path = dataset_paths_dict['s1']
        s2_img_path = dataset_paths_dict['s2']
        jrc_img_path = dataset_paths_dict['jrc']
        resampled_img_path = dataset_paths_dict['resampled']

        if dt_set == 'unosat':
            unosat_lst = get_ground_truth(dt_set)
            hls_tiles = gpd.read_file(args.s2_tile_path)
            # loop through all geodatabases
            flood_lst = get_flood_layers_from_unosat_gdbs(unosat_lst)
            # for each flood, clip to S2 tile size, download S2, rasterize GT
            print("checking interactively ", "flood_lst is ", flood_lst)
            for gdb, flood_layer in flood_lst:
                gdf = gpd.read_file(gdb, layer=flood_layer)
                gdf_union = gdf.unary_union
                flood_date = validate_date(gdf['Sensor_Date'].unique()[0], flood_layer)
                start_date, end_date, aoi = get_img_date_bbox(dt_set=dt_set, plus_days=4,
                                                              fl=flood_date,
                                                              shp=gdf_union)
                date_info = start_date.replace('-', '')
                # workaround to avoid having long `description`s sent to GEE (which won't accept more than 100 chars)
                gt_name_orig = '_'.join([Path(gdb).stem, flood_layer])
                gt_name = img_rename(gt_name_orig)
                print(f'--- --- --- renaming gt_name --- --- ---\nfrom: {gt_name_orig}\nto: {gt_name}\n')
                rename_dict[gt_name] = gt_name_orig

                del gdf
                # # if no s2 images for any of the overlapping folder OR no overlap, check GEE for S2 images
                # # get JRC images from GEE
                # clip multipoly-union to HLS tiles
                flood_hls = gpd.clip(hls_tiles, gdf_union)
                # make list of s2 image names (there can be multiple S2 images)
                # loop through s2 names, download if not already downloaded
                for i in range(len(flood_hls)):
                    flood = flood_hls.iloc[[i]]
                    aoi = list(flood.bounds.values)[0]
                    bounds = ee.Geometry.BBox(aoi[0], aoi[1], aoi[2], aoi[3])
                    tile = flood.identifier.values[0]
                    s2_dwnld_path_lst = glob(f'{s2_img_path}/{gt_name}*_T{tile}_S2*.tif')
                    print("1st s2_dwnld_path_lst:", s2_dwnld_path_lst)
                    if len(s2_dwnld_path_lst) == 0:
                        task_lst, n_s2_imgs, file_name_lst = download_s2_imgs(start_date, end_date, bounds,
                                                                              dt_set=dt_set, img_name=gt_name,
                                                                              hls_tiles=flood)
                        s2_dwnld_path_lst = [f'{s2_img_path}/{file_name}.tif' for file_name in file_name_lst]
                        
                    else:
                        # file_name_lst = []
                        task_lst = []
                        n_s2_imgs = 1
                    s1_dwnld_path_lst = glob(f'{s1_img_path}/{gt_name}_*_{tile}_S1*.tif')
                    print("1st s1_dwnld_path_lst:", s1_dwnld_path_lst)
                    if len(s1_dwnld_path_lst) == 0:
                        # HANDLE S1
                        task_lst2, n_s1_imgs, file_name_lst2 = download_s1_imgs(date_start=start_date, 
                                                                                date_end=end_date,
                                                                                bounds=bounds,
                                                                                dt_set=dt_set,
                                                                                img_name=gt_name,
                                                                                tile=tile)
                        s1_dwnld_path_lst = [f'{s1_img_path}/{file_name}.tif' for file_name in file_name_lst2]
                    else:
                        # file_name_lst2 = []
                        task_lst2 = []
                        n_s1_imgs = 1
                    # file_name_lst.extend(file_name_lst)
                    task_lst.extend(task_lst2)
                    n_s2_imgs += n_s1_imgs
                    # START wait for download
                    if n_s2_imgs == 0:
                        print(f'No S2/S1 image for {gt_name} {tile}')
                    else:
                        # add gee tasks to list
                        # download seasonal jrc from GEE
                        jrc_out_path = glob(f'{jrc_img_path}/{gt_name}_*_{tile}_Seasonal_JRC*.tif')
                        if len(jrc_out_path) == 0:
                            task, jrc_out_path, jrc_date = download_seasonal_jrc_imgs(start_date, flood,
                                                                                      dt_set=dt_set,
                                                                                      img_name=gt_name,
                                                                                      tile=tile, monthly=False)
                        # some floods have multiple s2 tasks if the flooded area is very large
                            task_lst.append(task)
                            jrc_out_path = [str(Path(jrc_img_path).parent / (jrc_out_path + '.tif'))]

                        else:
                            jrc_date = jrc_out_path[0].split('_')[-4]

                        check_on_tasks_in_queue(task_lst)

                        print('')
                        file_name_lst = s2_dwnld_path_lst + s1_dwnld_path_lst + jrc_out_path

                        print(file_name_lst)
                        for dwnld_path in file_name_lst:
                            wait_for_local_sync(dwnld_path)
                            gdal_wait(dwnld_path)

                        print("2nd s2_dwnld_path_lst ", s2_dwnld_path_lst)
                        
                        s2_dwnld_path_lst = glob(f'{s2_img_path}/{gt_name}*_T{tile}_S2*.tif')
                        print("3rd s2_dwnld_path_lst:", s2_dwnld_path_lst)

                        print("2nd s1_dwnld_path_lst ", s1_dwnld_path_lst)
                        
                        s1_dwnld_path_lst = glob(f'{s1_img_path}/{gt_name}_*_{tile}_S1*.tif')
                        print("3rd s1_dwnld_path_lst:", s1_dwnld_path_lst)

                        print(f'{out_dir}/unosat_{gt_name}_*_S2.tif')
                        
                        if len(s2_dwnld_path_lst) > 0:
                            # REPROJECT
                            s2_outpath, profile = reproj_rename_s2(img_path=s2_dwnld_path_lst,
                                                                   dt_set=dt_set,
                                                                   gt_name=gt_name,
                                                                   out_dir=out_dir,
                                                                   sat='S2',
                                                                   generated_img_path=generated_img_path,
                                                                   tile=tile)
                            
                            s2_dwnld_path_lst = glob(f'{out_dir}/unosat_{gt_name}_*_{tile}_S2.tif')
                            print("4th s2_dwnld_path_lst:", s2_dwnld_path_lst)

                            # reproject and calculate ndwi for each s2 image
                            for s2_path in s2_dwnld_path_lst:
                                s2_name = Path(s2_path).stem.replace("_S2", "")
                                # CALCULATE NDWI for each s2 image
                                calc_ndwi(s2_path=s2_outpath, dt_set=dt_set, s2_name=s2_name, out_dir=out_dir,
                                          profile=profile)

                            # REPROJECT S1 to S2 OR get S1 profile if no S2
                            for s1_path in s1_dwnld_path_lst:
                                s1_out_path = resample_to_s2(in_path=s1_path, s2_path=s2_path, gt_name=gt_name,
                                                             out_dir=out_dir, tag='S1', dt_set=dt_set,
                                                             generated_img_path=generated_img_path)
                            s_path = s2_dwnld_path_lst[0]

                        elif len(s1_dwnld_path_lst) > 0:
                            s1_outpath, profile = reproj_rename_s2(img_path=s1_dwnld_path_lst,
                                                                   dt_set=dt_set,
                                                                   gt_name=gt_name,
                                                                   out_dir=out_dir,
                                                                   sat='S1',
                                                                   generated_img_path=generated_img_path,
                                                                   tile=tile)
                            s1_dwnld_path_lst = glob(f'{out_dir}/unosat_{gt_name}_*_{tile}_S1.tif')
                            print("4th s1_dwnld_path_lst ", s1_dwnld_path_lst)
                            s_path = s1_dwnld_path_lst[0]
                            print("s_path ", s_path)
                        # as long as we have either an S1 or S2 image,
                        # resample GT and JRC and save to main output directory
                        if len(s2_dwnld_path_lst) != 0 or len(s1_dwnld_path_lst) != 0:
                            # RASTERIZE GT
                            print('s_path ', s_path)
                            gt_resamp_path = rasterize_shp(flood_shp=flood, out_dir=resampled_img_path, gt_name=gt_name,
                                                           s2_path=s_path, date_info=date_info)
                            print("done with rasterize_shp")
                            # resample JRC to s2 profile
                            jrc_out_path = f'{jrc_img_path}/{gt_name}_{jrc_date}_{tile}_Seasonal_JRC.tif'
                            print("jrc_out_path ", jrc_out_path)
                            jrc_resamp_path = resample_to_s2(in_path=jrc_out_path, s2_path=s_path,
                                                             gt_name='_'.join([gt_name, date_info, tile]),
                                                             tag='JRC', dt_set=dt_set, out_dir=out_dir,
                                                             generated_img_path=generated_img_path)

                            # CLASSIFY IMAGE
                            calc_classes(dt_set=dt_set, s2_name='_'.join([gt_name, date_info, tile]),
                                         out_dir=out_dir, profile=profile,
                                         gt_path=gt_resamp_path, jrc_path=jrc_resamp_path)

                rename_from_dict(out_dir, rename_dict, tiles=None)

        else:
            gt_fl_paths, gt_names = get_ground_truth(dt_set)
            s2_fl_paths, s2_names = get_s2_imgs(dt_set)  # empty for usgs
            s1_fl_paths, s1_names = get_s1_imgs(dt_set)  # empty for WF, Sen1Floods11, usgs
            jrc_fl_paths, jrc_names = get_jrc_imgs(dt_set)  # empty for WF, usgs

            s2_missing, jrc_missing, s1_missing = get_s2_jrc_s1_indexes(gt_names, s2_names, jrc_names, s1_names,
                                                                        check_miss=True)

            gee_tasks = []
            s2_dwnld_path_lst = []
            s1_dwnld_path_lst = []
            jrc_dwnld_path_lst = []

            for name in gt_names:
                print('name', name)
                print('s2_missing', s2_missing)
                if name in s2_missing + s1_missing + jrc_missing:
                    # get metadata file
                    meta_fl = get_metadata(dt_set, name)
                    # get date and bounds
                    # by default, end_date is start_date + 1
                    start_date, end_date, aoi = get_img_date_bbox(dt_set, meta_fl)
                    if name in s2_missing:
                        # download s2 from GEE, gee task list, nr of s2 imgs to dwl
                        task_lst, n_s2_imgs, file_name_lst = download_s2_imgs(start_date, end_date, aoi, 
                                                                              dt_set=dt_set, img_name=name)
                        s2_dwnld_path_lst.extend([f'{s2_img_path}/{file_name}.tif' for file_name in file_name_lst])
                        print('s2_dwnld_path_lst: ', s2_dwnld_path_lst)
                        print(type(task_lst))
                        print(task_lst)
                        # add gee tasks to list
                        # some floods have multiple s2 tasks if the flooded area is very large
                        gee_tasks.extend(task_lst)
                    if name in jrc_missing:
                        # download seasonal jrc from GEE                    
                        print('before ', name)
                        task, jrc_out_path, jrc_date = download_seasonal_jrc_imgs(start_date, aoi, dt_set=dt_set, 
                                                                                  img_name=name, monthly=False)
                        jrc_dwnld_path_lst.extend([f'{jrc_img_path}/{Path(jrc_out_path).name}.tif'])
                        print('jrc_dwnld_path_lst: ', jrc_dwnld_path_lst)
                        gee_tasks.append(task)
                    if name in s1_missing:
                        # download s1 from GEE
                        task_lst, n_s1_imgs, file_name_lst2 = download_s1_imgs(date_start=start_date, 
                                                                               date_end=end_date,
                                                                               bounds=aoi,
                                                                               dt_set=dt_set,
                                                                               img_name=name)
                        s1_dwnld_path_lst.extend([f'{s1_img_path}/{file_name}.tif' for file_name in file_name_lst2])
                        print('s1_dwnld_path_lst: ', s1_dwnld_path_lst)
                        print('task_lst empty?', task_lst)
                        gee_tasks.extend(task_lst)
                        # add gee tasks to list
                        # some floods have multiple s1 tasks if the flooded area is very large
                
    # might need to handle if we don't need to download anything...     
            print('entering check_on_tasks_in_queue(gee_tasks)')
            check_on_tasks_in_queue(gee_tasks)

            print('')
            file_name_lst = s2_dwnld_path_lst + s1_dwnld_path_lst + jrc_dwnld_path_lst

            print(file_name_lst)
            for dwnld_path in file_name_lst:
                wait_for_local_sync(dwnld_path)
                gdal_wait(dwnld_path)

            gt_fl_paths, gt_names = get_ground_truth(dt_set)
            s2_fl_paths, s2_names = get_s2_imgs(dt_set)
            s1_fl_paths, s1_names = get_s1_imgs(dt_set)
            jrc_fl_paths, jrc_names = get_jrc_imgs(dt_set)

            s2_idx, jrc_idx, s1_idx = get_s2_jrc_s1_indexes(gt_names, s2_names, jrc_names, s1_names)

            for i in range(len(gt_fl_paths)):

                print(f'{gt_names[i]}')
                gt_name = gt_names[i]
                s2_lst = [s2_fl_i for s2_fl_i in s2_fl_paths if gt_name in s2_fl_i]
                print(f's2_lst: {len(s2_lst)}')
                s1_lst = [s1_fl_i for s1_fl_i in s1_fl_paths if gt_name in s1_fl_i]
                print(f's1_lst: {len(s1_lst)}\n')
                if len(s2_lst) > 1:  # if there are more than 1 files per gt_name so (1), (2) etc.
                    # reproject with merge
                    print("reprojecting with merge, s2_lst ", len(s2_lst), s2_lst)
                    s_outpath, profile = reproj_rename_s2(img_path=s2_lst.copy(), 
                                                          dt_set=dt_set,
                                                          gt_name=gt_name,
                                                          out_dir=out_dir,
                                                          sat='S2',
                                                          generated_img_path=generated_img_path)

                elif len(s2_lst) == 1:
                    # REPROJECT
                    s_outpath, profile = reproj_rename_s2(img_path=s2_lst[0], 
                                                          dt_set=dt_set,
                                                          gt_name=gt_name,
                                                          out_dir=out_dir,
                                                          sat='S2',
                                                          generated_img_path=generated_img_path)
                    
                elif len(s1_lst) > 0:  # no s2 images, at least 1 s1
                    # REPROJECT / GET S1 PROFILE
                    s_outpath, profile = reproj_rename_s2(img_path=s1_lst.copy(), 
                                                          dt_set=dt_set, 
                                                          gt_name=gt_name,
                                                          out_dir=out_dir, 
                                                          sat='S1',
                                                          generated_img_path=generated_img_path)
                else:  # no s2 or s1
                    print(f"no s2 or s1 images for {gt_name}\n")
                    continue
                
                if len(s2_lst) != 0:
                    s2_dwnld_path_lst = glob(f'{out_dir}/{dt_set}_{gt_name}*S2.tif')
                    print("s2_dwnld_path_lst:", s2_dwnld_path_lst)
                    # reproject and calculate ndwi for each s2 image
                    for s2_path in s2_dwnld_path_lst:
                        s2_name = Path(s2_path).stem.replace("_S2", "")
                        print(f's2_path: {s2_path}')
                        print(f's2_name: {s2_name}')
                        # CALCULATE NDWI
                        calc_ndwi(s2_path=s_outpath, 
                                  dt_set=dt_set,
                                  s2_name=s2_name,
                                  out_dir=out_dir,
                                  profile=profile)
                    
                    if len(s1_lst) != 0:
                        for s1_path in s1_lst:
                            # resample s1 to s2 profile 
                            s1_resamp_path = resample_to_s2(in_path=s1_path, 
                                                            s2_path=s_outpath, 
                                                            gt_name=gt_name,
                                                            out_dir=out_dir, 
                                                            tag='S1', 
                                                            dt_set=dt_set,
                                                            generated_img_path=generated_img_path)
                            print('s1_resamp_path: ', s1_resamp_path)
                    else:
                        print(f'No S1 images for {gt_name}')

                # resample gt to s2 profile (if needed)
                gt_resamp_path = resample_to_s2(in_path=gt_fl_paths[i], 
                                                s2_path=s_outpath, 
                                                gt_name=gt_name, 
                                                tag='GT',
                                                out_dir=out_dir,
                                                dt_set=dt_set,
                                                generated_img_path=generated_img_path)

                # resample JRC to s2 profile
                jrc_resamp_path = resample_to_s2(in_path=jrc_fl_paths[jrc_idx[i]], out_dir=out_dir,
                                                 s2_path=s_outpath, gt_name=gt_name,
                                                 tag='JRC', dt_set=dt_set,
                                                 generated_img_path=generated_img_path)

                # CLASSIFY IMAGE
                calc_classes(dt_set=dt_set, s2_name=gt_name, out_dir=out_dir, profile=profile, 
                             gt_path=gt_resamp_path, jrc_path=jrc_resamp_path)



if __name__ == '__main__':
    main()
