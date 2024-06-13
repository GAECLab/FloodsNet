import os

import numpy as np
import rasterio as rio


def calc_ndwi(s2_path: str, dt_set: str, s2_name: str, out_dir: str, profile):
    """
        s2_path should point to the reprojected s2 saved in the output directory.

        Calculate NDWI for Sentinel-2 images.
        NDWI = (Green - NIR) / (Green + NIR)

        Return NDWI and source EPSG and UTM EPSG
    """
    # generate path for reprojected S2 image in the output directory
    out_path = os.path.join(out_dir, '_'.join([s2_name, 'NDWI.tif']))
    if os.path.exists(out_path):
        print(f'{out_path} already exists.')
        return
    with rio.open(s2_path, 'r') as src:
        b3 = src.read(3).astype(int)  # bands index starting with 1. Band 3 = Green
        b8 = src.read(8).astype(int)  # Band 8 = Near Infra Red
        ndwi = _get_ndwi_formula(b3, b8)
    # write NDWI to the output directory
    profile.update(
        dtype='int16',
        count=1,
        compress='lzw',
        interleave='band',
        tiled=True,
    )
    with rio.open(out_path, 'w', **profile) as dst:
        dst.write(np.array(ndwi * 10000).astype('int16'), 1)
        dst.set_band_description(1, 'NDWI')

    print(f'{out_path} saved.')
    return


def _get_ndwi_formula(b3, b8):
    b3_b8_dif = np.subtract(b3, b8, out=np.zeros(b3.shape, dtype=int))
    b3_b8_sum = np.add(b3, b8, out=np.zeros(b3.shape, dtype=int))
    return np.divide(
        b3_b8_dif,
        b3_b8_sum,
        out=np.zeros(b3.shape, dtype=float),
        where=b3_b8_sum != 0,
    )
