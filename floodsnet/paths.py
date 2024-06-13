# -*- coding: utf-8 -*-
"""
Auxiliary functions to define and handle paths.

"""
from pathlib import Path


def generated_data(root):
    """GENERATED_IMG_PATH"""
    return Path(root) / 'global_flood_training' / 'data'


def world_floods(data):
    """WORLD_FLOODS_GENERATED, WORLD_FLOODS_RESAMPLED, WORLD_FLOODS_REPROJECTED, WORLD_FLOODS_SEASONAL_JRC, and
    WORLD_FLOODS_S1_IMGS_PATH"""
    generated = generated_data(data) / 'WorldFloods' / 'generated'
    resampled = generated / 'resampled'
    reprojected = generated / 'reprojected'
    jrc = Path(generated) / 'JRC_WORLDFLOODS'
    s1 = Path(generated) / 'S1_WORLDFLOODS'
    return generated, resampled, reprojected, jrc, s1


def sen1floods11(data):
    """SEN1_FLOODS11_GENERATED, SEN1_FLOODS11_RESAMPLED, SEN1_FLOODS11_REPROJECTED, SEN1_FLOODS11_SEASONAL_JRC, and
    SEN1_FLOODS11_S1_IMGS_PATH"""
    generated = generated_data(data) / 'Sen1Floods11' / 'generated'
    resampled = generated / 'resampled'
    reprojected = generated / 'reprojected'
    jrc = generated / 'JRC_SEN1FLOODS11'
    s1 = generated / 'S1_SEN1FLOODS11'
    return generated, resampled, reprojected, jrc, s1


def usgs(data):
    """USGS_GENERATED, USGS_RESAMPLED, USGS_REPROJECTED, USGS_SEASONAL_JRC, USGS_S1_IMGS_PATH, and USGS_S2_IMGS_PATH"""
    generated = generated_data(data) / 'usgs' / 'generated'
    resampled = generated / 'resampled'
    reprojected = generated / 'reprojected'
    jrc = generated / 'JRC_usgs'
    s1 = generated / 'S1_usgs'
    s2 = generated / 'S2_usgs'
    return generated, resampled, reprojected, jrc, s1, s2


def unosat(data):
    """UNOSAT_GENERATED, UNOSAT_RESAMPLED, UNOSAT_REPROJECTED, UNOSAT_GROUND_TRUTH_RESAMP, UNOSAT_S2_IMGS_PATH,
    UNOSAT_SEASONAL_JRC, UNOSAT_SEASONAL_JRC_RESAMP, UNOSAT_S1_IMGS_PATH, and UNOSAT_S1_IMGS_PATH_RESAMP"""
    generated = generated_data(data) / 'unosat' / 'generated'
    resampled = generated / 'resampled'
    reprojected = generated / 'reprojected'
    gt = resampled / '*GT.tif'
    s2 = generated / 'S2_unosat'
    jrc = generated / 'JRC_unosat'
    jrc_resampled = resampled / '*JRC.tif'
    s1 = generated / 'S1_unosat'
    s1_resampled = resampled / '*S1.tif'
    return generated, resampled, reprojected, jrc, jrc_resampled, s1, s1_resampled, s2, gt


def dataset_paths(dataset, data_dir):
    paths_dict = {
        'generated': None,
        'resampled': None,
        'reprojected': None,
        'jrc': None,
        'jrc_resampled': None,
        's1': None,
        's1_resampled': None,
        's2': None,
        'gt': None,
    }
    if dataset == 'world_floods':
        paths = world_floods(data_dir)
    elif dataset == 'sen1_floods11':
        paths = sen1floods11(data_dir)
    elif dataset == 'usgs':
        paths = usgs(data_dir)
    elif dataset == 'unosat':
        paths = unosat(data_dir)
    else:
        raise ValueError(f'dataset {dataset} not valid.')

    paths_dict['generated'] = paths[0]
    paths_dict['resampled'] = paths[1]
    paths_dict['reprojected'] = paths[2]
    paths_dict['jrc'] = paths[3]
    paths_dict['s1'] = paths[4]

    if dataset == 'usgs':
        paths_dict['s2'] = paths[5]
    elif dataset == 'unosat':
        paths_dict['jrc_resampled'] = paths[4]
        paths_dict['s1'] = paths[5]
        paths_dict['s1_resampled'] = paths[6]
        paths_dict['s2'] = paths[7]
        paths_dict['gt'] = paths[8]

    return paths_dict


def _make_dirs(fld_seasonal_jrc: Path, fld_s1: Path, fld_resampled: Path, fld_reprojected: Path, fld_generated: Path,
               fld_s2=None):
    fld_seasonal_jrc.mkdir(parents=True, exist_ok=True)
    fld_s1.mkdir(parents=True, exist_ok=True)
    if fld_s2 is not None:
        fld_s2.mkdir(parents=True, exist_ok=True)
    if not fld_resampled.exists():
        fld_generated.mkdir(parents=True, exist_ok=True)
        fld_resampled.mkdir(parents=True, exist_ok=True)
    if not fld_reprojected.exists():
        fld_generated.mkdir(parents=True, exist_ok=True)
        fld_reprojected.mkdir(parents=True, exist_ok=True)


def setup_dirs(data, dt_set=str):
    """Checks for and creates directories for downloaded GEE images
    and resampled/reprojected images.
    """
    if dt_set == 'world_floods':
        generated, resampled, reprojected, jrc, s1 = world_floods(data)
        _make_dirs(jrc, s1, resampled, reprojected, generated)
    elif dt_set == 'sen1_floods11':
        generated, resampled, reprojected, jrc, s1 = sen1floods11(data)
        _make_dirs(jrc, s1, resampled, reprojected, generated)
    elif dt_set == 'usgs':
        generated, resampled, reprojected, jrc, s1, s2 = usgs(data)
        _make_dirs(jrc, s1, resampled, reprojected, generated, s2)
    elif dt_set == 'unosat':
        generated, resampled, reprojected, jrc, jrc_resampled, s1, s1_resampled, s2, gt = unosat(data)
        _make_dirs(jrc, s1, resampled, reprojected, generated, s2)


def _find_indexes(names, target_names):
    indexes = {}
    missing = []
    for idx, name in enumerate(names):
        if name in target_names:
            indexes[idx] = target_names.index(name)
        else:
            missing.append(name)
    return indexes, missing


def get_s2_jrc_s1_indexes(gt_names, s2_names, jrc_names, s1_names, check_miss=False):
    s2_idx, s2_missing = _find_indexes(gt_names, s2_names)
    jrc_idx, jrc_missing = _find_indexes(gt_names, jrc_names)
    s1_idx, s1_missing = _find_indexes(gt_names, s1_names)
    if check_miss:
        return s2_missing, jrc_missing, s1_missing
    else:
        return s2_idx, jrc_idx, s1_idx
