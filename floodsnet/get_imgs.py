import datetime
import json
import os
from glob import glob
from pathlib import Path
from typing import Union
from typing_extensions import deprecated

import ee

from .cli import parse_flood_training_data_args
from .usgs_floods import get_usgs_img_date_bbox

args = parse_flood_training_data_args()
DOWNLOADED_IMG_PATH = args.path
GENERATED_IMG_PATH = args.generated_path
print("GENERATED_IMG_PATH is ", GENERATED_IMG_PATH)
GENERATED_IMG_PATH = Path(GENERATED_IMG_PATH) / 'global_flood_training' / 'data'

# WorldFloods paths
WORLD_FLOODS_S2_IMGS_PATH = Path(DOWNLOADED_IMG_PATH) / 'WorldFloods' / 'downloaded' / '*/S2/*.tif'
WORLD_FLOODS_GROUND_TRUTH = Path(DOWNLOADED_IMG_PATH) / 'WorldFloods' / 'downloaded' / '*/gt/*.tif'
WORLD_FLOODS_METADATA = Path(DOWNLOADED_IMG_PATH) / 'WorldFloods' / 'downloaded' / '*/meta'

WORLD_FLOODS_GENERATED = Path(GENERATED_IMG_PATH) / 'WorldFloods' / 'generated'
WORLD_FLOODS_RESAMPLED = Path(WORLD_FLOODS_GENERATED) / 'resampled'

WORLD_FLOODS_SEASONAL_JRC_GENERATED = Path(WORLD_FLOODS_GENERATED) / 'JRC_WORLDFLOODS' / '*.tif'
WORLD_FLOODS_S1_IMGS_PATH_GENERATED = Path(WORLD_FLOODS_GENERATED) / 'S1_WORLDFLOODS' / '*.tif'

#Sen1Floods11 paths
# first 5 come from dataset
SEN1_FLOODS11_S2_IMGS_PATH = Path(DOWNLOADED_IMG_PATH) / 'Sen1Floods11' / 'downloaded' / '*/data/flood_events/HandLabeled/S2Hand/*.tif'
SEN1_FLOODS11_GROUND_TRUTH = Path(DOWNLOADED_IMG_PATH) / 'Sen1Floods11' / 'downloaded' / '*/data/flood_events/HandLabeled/LabelHand/*.tif'
SEN1_FLOODS11_JRC = Path(DOWNLOADED_IMG_PATH) / 'Sen1Floods11' / 'downloaded' / 'JRC_WORLDFLOODS' / '*.tif'
SEN1_FLOODS11_S1 = Path(DOWNLOADED_IMG_PATH) / 'Sen1Floods11' / 'downloaded' / '*/data/flood_events/HandLabeled/S1Hand/*.tif'
SEN1_FLOODS11_METADATA = Path(DOWNLOADED_IMG_PATH) / 'Sen1Floods11' / 'downloaded' / '*/catalog/sen1floods11_hand_labeled_source/*/'

SEN1_FLOODS11_GENERATED = Path(GENERATED_IMG_PATH) / 'Sen1Floods11' / 'generated'
SEN1_FLOODS11_RESAMPLED = Path(SEN1_FLOODS11_GENERATED) / 'resampled'

# from GEE
SEN1_FLOODS11_S1_IMGS_PATH_GENERATED = Path(SEN1_FLOODS11_GENERATED) / 'S1_SEN1FLOODS11/*.tif'
SEN1_FLOODS11_SEASONAL_JRC_GENERATED = Path(SEN1_FLOODS11_GENERATED) / 'JRC_SEN1FLOODS11' / '*.tif'

# USGS paths
USGS_FLOOD_TRAINING_GROUND_TRUTH = Path(DOWNLOADED_IMG_PATH) / 'USGS_FloodTraining' / 'downloaded' / 'RasterData_and_Metadata/*.tif'
USGS_GENERATED = Path(GENERATED_IMG_PATH) / 'usgs' / 'generated'
USGS_RESAMPLED = Path(USGS_GENERATED) / 'resampled'
USGS_FLOOD_TRAINING_GROUND_TRUTH_RESAMP = Path(USGS_RESAMPLED) / '*GT.tif'
# s2
USGS_FLOOD_TRAINING_S2_IMGS_PATH = Path(USGS_GENERATED) / 'S2_usgs' / '*.tif'
# jrc
USGS_FLOOD_TRAINING_JRC = Path(USGS_GENERATED) / 'JRC_usgs' / '*.tif'
USGS_FLOOD_TRAINING_JRC_RESAMP = Path(USGS_RESAMPLED) / '*JRC.tif'
# s1
USGS_FLOOD_TRAINING_S1 = Path(USGS_GENERATED) / 'S1_usgs' / '*.tif'
USGS_FLOOD_TRAINING_S1_RESAMP = Path(USGS_RESAMPLED) / '*S1.tif'
# meta dir
USGS_FLOOD_TRAINING_METADATA = Path(DOWNLOADED_IMG_PATH) / 'USGS_FloodTraining' / 'downloaded' / 'RasterData_and_Metadata'

# UNOSAT paths
UNOSAT_GROUND_TRUTH = Path(DOWNLOADED_IMG_PATH) / 'UNOSAT_SAR/downloaded/*gdb'

UNOSAT_GENERATED = Path(GENERATED_IMG_PATH) / 'unosat' / 'generated'
UNOSAT_RESAMPLED = Path(UNOSAT_GENERATED) / 'resampled'
# gt
UNOSAT_GROUND_TRUTH_RESAMP = Path(UNOSAT_RESAMPLED) / '*GT.tif'
# s2
UNOSAT_S2_IMGS_PATH = Path(UNOSAT_GENERATED) / 'S2_unosat'
# jrc
UNOSAT_SEASONAL_JRC = Path(UNOSAT_GENERATED) / 'JRC_unosat' 
UNOSAT_SEASONAL_JRC_RESAMP = Path(UNOSAT_RESAMPLED) / '*JRC.tif'
# s1
UNOSAT_S1_IMGS_PATH = Path(UNOSAT_GENERATED) / 'S1_unosat'
UNOSAT_S1_IMGS_PATH_RESAMP = Path(UNOSAT_RESAMPLED) / '*S1.tif'


# FOR ALL DATASETS #####
def get_ground_truth(dt_set: str, out_dir=''):
    if dt_set == 'world_floods':
        wf_gt_lst = glob(str(WORLD_FLOODS_GROUND_TRUTH))
        wf_gt_lst = [gt for gt in wf_gt_lst if '/train/' not in gt]
        wf_gt_names = [Path(i).stem for i in wf_gt_lst]
        return wf_gt_lst, wf_gt_names
    elif dt_set == 'sen1_floods11':
        s1f11_label_lst = glob(str(SEN1_FLOODS11_GROUND_TRUTH))
        s1f11_label_lst.sort()
        s1f11_label_flood_id_lst = ['_'.join(Path(i).stem.split('_')[:2]) for i in s1f11_label_lst]
        return s1f11_label_lst, s1f11_label_flood_id_lst
    elif dt_set == 'usgs':
        usgs_gt_lst = glob(str(USGS_FLOOD_TRAINING_GROUND_TRUTH))
        usgs_gt_lst.sort()
        usgs_gt_names = [os.path.basename(i)[:8] for i in usgs_gt_lst]
        return usgs_gt_lst, usgs_gt_names
    elif dt_set == 'unosat':
        if len(out_dir) > 0:
            unosat_gt_lst = glob(f'{out_dir}/unosat*GT.tif')
            unosat_gt_names = [Path(i).stem for i in unosat_gt_lst]
            return unosat_gt_lst, unosat_gt_names
        else:
            unosat_gt_lst = glob(str(UNOSAT_GROUND_TRUTH))
            unosat_gt_lst.sort()
            return unosat_gt_lst


def get_s2_imgs(dt_set: str):
    if dt_set == 'world_floods':
        wf_s2_lst = glob(str(WORLD_FLOODS_S2_IMGS_PATH))
        wf_s2_names = [Path(i).stem for i in wf_s2_lst]
        return wf_s2_lst, wf_s2_names
    elif dt_set == 'sen1_floods11':
        s1f11_s2_lst = glob(str(SEN1_FLOODS11_S2_IMGS_PATH))
        s1f11_s2_lst.sort()
        s1f11_s2_flood_id_lst = ['_'.join(Path(i).stem.split('_')[:2]) for i in s1f11_s2_lst]
        return s1f11_s2_lst, s1f11_s2_flood_id_lst
    elif dt_set == 'usgs':
        usgs_s2_lst = glob(str(USGS_FLOOD_TRAINING_S2_IMGS_PATH))
        usgs_s2_names = [Path(i).stem[:8] for i in usgs_s2_lst]
        return usgs_s2_lst, usgs_s2_names
    elif dt_set == 'unosat':
        unosat_s2_lst = glob(str(UNOSAT_S2_IMGS_PATH))
        unosat_s2_names = [Path(i).stem[:-45] + Path(i).stem[-12:-7] for i in unosat_s2_lst]
        return unosat_s2_lst, unosat_s2_names


def get_s1_imgs(dt_set: str):
    if dt_set == 'world_floods':
        wf_s1_lst = glob(str(WORLD_FLOODS_S1_IMGS_PATH_GENERATED))
        wf_s1_names_lst = [Path(i).stem for i in wf_s1_lst]
        wf_s1_names = list({'_'.join(i.split('_')[:-4]) for i in wf_s1_names_lst})
        return wf_s1_lst, wf_s1_names
    elif dt_set == 'sen1_floods11':
        s1f11_s1_lst = glob(str(SEN1_FLOODS11_S1)) + glob(str(SEN1_FLOODS11_S1_IMGS_PATH_GENERATED))
        s1f11_s1_lst.sort()
        s1f11_s1_flood_id_lst = ['_'.join(Path(i).stem.split('_')[:2]) for i in s1f11_s1_lst]
        return s1f11_s1_lst, s1f11_s1_flood_id_lst
    elif dt_set == 'usgs':
        usgs_s1_lst = glob(str(USGS_FLOOD_TRAINING_S1))
        usgs_s1_lst.sort()
        usgs_s1_names = [os.path.basename(i)[:8] for i in usgs_s1_lst]
        return usgs_s1_lst, usgs_s1_names
    elif dt_set == 'unosat':
        unosat_s2_lst = glob(str(UNOSAT_S1_IMGS_PATH))
        unosat_s2_names = [os.path.basename(i)[:-7] for i in unosat_s2_lst]
        return unosat_s2_lst, unosat_s2_names


def _get_jrc_imgs_usgs_unosat(dt_set, int_place: int):
    usgs_jrc_lst = glob(str(dt_set))
    usgs_jrc_names = [Path(i).stem[:int_place] for i in usgs_jrc_lst]
    return usgs_jrc_lst, usgs_jrc_names


def get_jrc_imgs(dt_set: str):
    if dt_set == 'world_floods':
        wf_jrc_lst = glob(str(WORLD_FLOODS_SEASONAL_JRC_GENERATED))
        wf_jrc_name_lst = [Path(i).stem for i in wf_jrc_lst]
        wf_jrc_names = ['_'.join(i.split('_')[:-3]) for i in wf_jrc_name_lst]
        return wf_jrc_lst, wf_jrc_names
    elif dt_set == 'sen1_floods11':
        s1f11_jrc_lst = glob(str(SEN1_FLOODS11_JRC)) + glob(str(SEN1_FLOODS11_SEASONAL_JRC_GENERATED))
        s1f11_jrc_lst.sort()
        s1f11_jrc_flood_id_lst = ['_'.join(Path(i).stem.split('_')[:2]) for i in s1f11_jrc_lst]
        return s1f11_jrc_lst, s1f11_jrc_flood_id_lst
    elif dt_set == 'usgs':
        return _get_jrc_imgs_usgs_unosat(USGS_FLOOD_TRAINING_JRC, 8)
    elif dt_set == 'unosat':
        return _get_jrc_imgs_usgs_unosat(UNOSAT_SEASONAL_JRC_RESAMP, -15)


def get_metadata(dt_set: str, flood_name: str):
    if dt_set == 'world_floods':
        return glob(os.path.join(WORLD_FLOODS_METADATA, f'{flood_name}.json'))[0]
    elif dt_set == 'sen1_floods11':
        return glob(os.path.join(SEN1_FLOODS11_METADATA, f'{flood_name}.json'))[0]
    elif dt_set == 'usgs':
        return glob(os.path.join(USGS_FLOOD_TRAINING_METADATA, f'{flood_name}.tif.xml'))[0]


def get_usgs_flood_training_ground_truth_resamp(usgs_path=USGS_FLOOD_TRAINING_GROUND_TRUTH_RESAMP):
    '''
        Get list of USGS ground truth images
    '''
    usgs_gt_lst = glob(usgs_path)
    usgs_gt_names = [os.path.basename(i)[:8] for i in usgs_gt_lst]
    return usgs_gt_lst, usgs_gt_names


def get_usgs_flood_training_jrc_resamp(usgs_path=USGS_FLOOD_TRAINING_JRC_RESAMP):
    '''
        Get list of USGS ground truth images
    '''
    usgs_jrc_lst = glob(usgs_path)
    usgs_jrc_names = [os.path.basename(i)[:8] for i in usgs_jrc_lst]
    return usgs_jrc_lst, usgs_jrc_names


@deprecated('Seems to be unused.')
def _open_meta_file2(fl: str, sat_date_key: str, plus_days=1, minus_days=0):
    with open(fl) as json_fl:  # open the meta file
        fl_dict = json.load(json_fl)
        if sat_date_key == "satellite date":
            main_date = fl_dict[sat_date_key][:10]
        elif sat_date_key == "properties":
            main_date = fl_dict[sat_date_key]['datetime'][:10]
        else:
            print('not sure what meta file key to read for min_date')
        aoi = ee.Geometry.BBox(fl_dict['bounds'][0], fl_dict['bounds'][1],
                               fl_dict['bounds'][2], fl_dict['bounds'][3])


def get_img_date_bbox(dt_set: str, fl=Union[str, list], plus_days=1, minus_days=0, shp=None):
    """Gets the date and bounds of the flood/sentinel 2 image for a specified dataset.
    Can change if we want more than 1 day after the image and zero minus days.
    """
    if dt_set == 'world_floods':
        with open(fl) as json_fl:  # open the meta file
            fl_dict = json.load(json_fl)
            main_date = fl_dict['satellite date'][:10]
            date = datetime.datetime.strptime(main_date, "%Y-%m-%d") - datetime.timedelta(days=minus_days)
            start_date = date.strftime("%Y-%m-%d")
            date = datetime.datetime.strptime(main_date, "%Y-%m-%d") + datetime.timedelta(days=plus_days)
            end_date = date.strftime("%Y-%m-%d")
            aoi = ee.Geometry.BBox(fl_dict['bounds'][0], fl_dict['bounds'][1],
                                   fl_dict['bounds'][2], fl_dict['bounds'][3])
    elif dt_set == 'sen1_floods11':
        with open(fl) as json_fl:
            fl_dict = json.load(json_fl)
            main_date = fl_dict['properties']['datetime'][:10]
            date = datetime.datetime.strptime(main_date, "%Y-%m-%d") - datetime.timedelta(days=minus_days)
            start_date = date.strftime("%Y-%m-%d")
            date = datetime.datetime.strptime(main_date, "%Y-%m-%d") + datetime.timedelta(days=plus_days)
            end_date = date.strftime("%Y-%m-%d")
            aoi = ee.Geometry.BBox(fl_dict['bbox'][0], fl_dict['bbox'][1],
                                   fl_dict['bbox'][2], fl_dict['bbox'][3])
    elif dt_set == 'usgs':
        yr, month, day, aoi = get_usgs_img_date_bbox(fl)
        main_date = '-'.join([yr, month, day])
        date = datetime.datetime.strptime(main_date, "%Y-%m-%d") - datetime.timedelta(days=minus_days)
        start_date = date.strftime("%Y-%m-%d")
        date = datetime.datetime.strptime(main_date, "%Y-%m-%d") + datetime.timedelta(days=plus_days)
        end_date = date.strftime("%Y-%m-%d")
    elif dt_set == 'unosat':
        if isinstance(fl, list):
            start_date, end_date = fl
        else:
            main_date = str(fl).split(' ')[0]
            date = datetime.datetime.strptime(main_date, "%Y-%m-%d") - datetime.timedelta(days=minus_days)
            start_date = date.strftime("%Y-%m-%d")
            date = datetime.datetime.strptime(main_date, "%Y-%m-%d") + datetime.timedelta(days=plus_days)
            end_date = date.strftime("%Y-%m-%d")
        aoi = ee.Geometry.BBox(shp.bounds[0], shp.bounds[1], shp.bounds[2], shp.bounds[3])
    else:
        raise ValueError(f'dt_set value not recognized: {dt_set}')
    return start_date, end_date, aoi
