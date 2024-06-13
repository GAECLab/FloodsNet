# -*- coding: utf-8 -*-
"""
Code related to Sentinel-2 images.

"""
import os
import warnings
from pathlib import Path
from typing import Union

import numpy as np
import rasterio as rio
import rasterio.shutil
from osgeo import gdal

from .paths import dataset_paths
from .tools import compress_tiff, gdal_warp_compressed, gdal_set_descriptions, get_tiff_interleave
from .unosat_functions import get_utm_epsg_from_bounds


def _get_rio_profile(out_path: Union[str, Path]):
    with rio.open(out_path, 'r') as dst:
        profile = dst.profile
    return profile


def _check_img_outpath(dt_set: str, gt_name: str, out_dir: str, sat: str, img_id: str, tile: str):
    # generate path for reprojected S2 image in the output directory
    if (dt_set == 'world_floods') or (dt_set == 'sen1_floods11' and sat == 'S2'):
        out_path = os.path.join(out_dir, '_'.join([dt_set, gt_name, f'{sat}.tif']))
    elif dt_set == 'unosat':
        out_path = os.path.join(out_dir, '_'.join([dt_set, gt_name, img_id, tile, f'{sat}.tif']))
    else:
        out_path = os.path.join(out_dir, '_'.join([dt_set, gt_name, img_id, f'{sat}.tif']))

    if os.path.exists(out_path):
        print(f'{out_path} already exists.')
        profile = _get_rio_profile(out_path)
        return out_path, [profile]
    else:
        return out_path, []


def _castdown_dtype(ds):
    dtypes = np.unique(ds.dtypes)
    assert len(dtypes) == 1
    if dtypes[0] == 'int32':
        target_dtype = 'int16'
    elif dtypes[0] == 'float64':
        target_dtype = 'float32'
    else:
        target_dtype = dtypes[0]
        warnings.warn(f'Expected dtype int32 or float64 but got {dtypes[0]}.')
    return target_dtype


def _reproj_merge(img_lst: list, out_dir: Union[Path, str], gt_name: str, dt_set: str, sat: str,
                  generated_img_path: Union[Path, str], tile: str = ''):
    '''
        Reprojects, merges, renames, and saves S2 or S1 images in a list
        Returns path of saved images
    '''
    print("img_path is a list. dt_set is:", dt_set)
    print("img_lst: ", img_lst)

    dataset_paths_dict = dataset_paths(dt_set, generated_img_path)
    reproj_base_path = dataset_paths_dict['reprojected']

    id_count = 0
    while len(img_lst) > 0:
        if sat == 'S2':
            img_id = '_'.join(Path(img_lst[0]).stem.split('_')[-4:-2])
        else:  # sat == 'S1'
            img_id = '_'.join(Path(img_lst[0]).stem.split('_')[-5:-1])

        # generate path for reprojected S2 image in the output directory
        out_path, profile_lst = _check_img_outpath(dt_set, gt_name, out_dir, sat, img_id, tile)

        # get all the images with the same img_id
        img_id_lst = [img for img in img_lst if img_id in img]
        print('img_id:', img_id)
        print('img_id_lst:', img_id_lst)

        # if out_path does not exit
        if not os.path.exists(out_path):
            print('outpath does NOT exist')
            # if there is more than 1 image (s1 or s2) with the same ID (image date, processing date, and VV/VH and ASC/DESC for s1)
            if len(img_id_lst) > 1:
                print('len(img_id_lst)')
                # reproj and merge
                vrt_lst = [0] * len(img_id_lst)
                vrt_lst_lzw = [0] * len(img_id_lst)
                for i in range(len(img_id_lst)):
                    reproj_path = str(reproj_base_path / Path(img_id_lst[i]).name)
                    with rio.open(img_id_lst[i]) as src:
                        if i == 0 and id_count == 0:
                            destCRS = src.crs
                            profile_outpath = out_path
                        if i == 0:
                            vrt_lst[i] = reproj_path
                            gdal_warp_compressed(reproj_path,
                                                 img_id_lst[i], format='GTiff',
                                                 xRes=10, yRes=10, outputType=gdal.GDT_UInt16)
                        else:
                            srcCRS = src.crs
                    if i > 0:
                        # reproject
                        gdal_warp_compressed(reproj_path,
                                             img_id_lst[i], format='GTiff', srcSRS=srcCRS, dstSRS=destCRS,
                                             xRes=10, yRes=10, outputType=gdal.GDT_UInt16)

                        vrt_lst[i] = reproj_path
                # merge
                vrt_path = f'/vsimem/{gt_name}.vrt'
                vrt = gdal.BuildVRT(vrt_path, vrt_lst, srcNodata=0)
                vrt = None
                compress_tiff(vrt_path, out_path,
                              interleave=get_tiff_interleave(img_id_lst[0]))
                gdal_set_descriptions(out_path, copy_from=img_id_lst[0])

            else:
                print('len(img_id_lst) <=1')
                # bc we had to dwnld from gee, it's already in utm and we don't need to reproject
                with rio.open(img_id_lst[0]) as src:
                    if id_count == 0:
                        destCRS = src.crs
                        profile_outpath = out_path

                    cast_to = _castdown_dtype(src)
                    profile = src.profile.copy()
                    profile.update(
                        dtype=cast_to,
                        compress='lzw',
                        interleave='band',
                        tiled=True,
                    )
                    with rio.open(out_path, 'w', **profile) as dst:
                        # arr = src.read()
                        # if 'float' in src.meta['dtype'] and 'int' in cast_to:
                        #     if sat == 'S1':
                        #         arr *= 10
                        #     else:  # sat == 'S2'
                        #         arr *= 10000
                        #
                        # dst.write(arr.astype(cast_to))
                        dst.write(src.read().astype(cast_to))
                        dst.descriptions = src.descriptions
        else:
            print('outpath does exist')
            if id_count == 0:
                with rio.open(out_path) as src:
                    destCRS = src.crs
                    profile_outpath = out_path

        for img in img_id_lst:
            img_lst.remove(img)
        print('len img_lst: ', len(img_lst))
        id_count += 1

    return profile_outpath


def reproj_rename_s2(img_path: Union[str, list], dt_set: str, gt_name: str, out_dir: Union[str, Path],
                     sat: str, generated_img_path: Union[str, Path], tile: str = ''):
    """If the dataset already comes w S2 we just make sure they are in UTM, 10m,
    reproject, rename, and save S2 tif to the common naming convention
    saved to the local_out_dir folder.
    Return UTM profile for other rasters.
    """
    if not isinstance(img_path, list):
        if sat == 'S2':
            img_id = '_'.join(Path(img_path).stem.split('_')[-4:-2])
        else:  # sat == 'S1'
            img_id = '_'.join(Path(img_path).stem.split('_')[-5:-1])

        out_path, profile_lst = _check_img_outpath(dt_set, gt_name, out_dir, sat, img_id, tile)
        if len(profile_lst) != 0:
            return out_path, profile_lst[0]

        if dt_set not in ['usgs', 'unosat']:
            # Read in the original S2 image to get its current crs and calculate the UTM crs
            with rio.open(img_path) as src:
                lon = src.profile['transform'][2]
                src_epsg = src.crs
                dst_epsg = get_utm_epsg_from_bounds(src.bounds, src.crs)
            # use gdal.Warp to reproject the raster to the output directory
            gdal_warp_compressed(out_path, img_path,
                                 srcSRS=src_epsg, dstSRS=dst_epsg, xRes=10, yRes=10,
                                 outputType=gdal.GDT_Float32)
            gdal_set_descriptions(out_path, copy_from=img_path)

        else:  # dt_set is usgs or unosat, but img_path is not a list
            # bc we had to dwnld from gee, it's already in utm and we don't need to reproject
            with rio.open(img_path) as src:
                cast_to = _castdown_dtype(src)
                profile = src.profile.copy()
                profile.update(
                    dtype=cast_to,
                    compress='lzw',
                    interleave='band',
                    tiled=True,
                )
                with rio.open(out_path, 'w', **profile) as dst:
                    dst.write(src.read().astype(cast_to))
                    dst.descriptions = src.descriptions

    else:  # img_path is a list
        out_path = _reproj_merge(img_lst=img_path, out_dir=out_dir, gt_name=gt_name,
                                 dt_set=dt_set, sat=sat, generated_img_path=generated_img_path, tile=tile)

    profile = _get_rio_profile(out_path)
    profile['nodata'] = None
    print(f'{out_path} saved.')
    return out_path, profile


def resample_to_s2(in_path: str, s2_path: str, gt_name: str, out_dir: str, tag: str, dt_set: str,
                   generated_img_path: Union[str, Path]):
    # code smell: some of the above str can in fact be pathlib.Path
    """Resamples data to the S2 10x10m resolution."""
    # generate path for reprojected gt image in the output directory
    if tag == 'S1' and dt_set == 'sen1_floods11' and Path(in_path).stem.split('_')[-1] != 'S1':
        out_path = Path(out_dir) / f'{dt_set}_{Path(in_path).stem}_{tag}.tif'
    elif tag == 'S1':
        out_path = Path(out_dir) / f'{dt_set}_{Path(in_path).name}'
    else:
        dataset_paths_dict = dataset_paths(dt_set, generated_img_path)
        out_dir = dataset_paths_dict['resampled']
        out_path = Path(out_dir) / f'{gt_name}_resamp_{tag}.tif'

    if out_path.exists():
        print(f'{out_path} exists.')
    else:
        with rio.open(s2_path) as src:
            res = int(round(src.profile['transform'][0]))
            srs = str(src.profile['crs'])
            height_width = src.read(1).shape
            profile = src.profile
            bounds = src.bounds
        out_bounds = (bounds[0], bounds[1], bounds[2], bounds[3])
        gdal_warp_compressed(out_path, in_path,
                             dstSRS=srs, outputBounds=out_bounds,
                             xRes=res, yRes=res, height=height_width[0], width=height_width[1],
                             outputType=gdal.GDT_Float32)
        gdal_set_descriptions(out_path, copy_from=in_path)
        if tag == 'S1':
            print(f'{out_path} saved.')
    return out_path
