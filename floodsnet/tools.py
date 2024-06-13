import re
import time
import warnings
from hashlib import sha256
from pathlib import Path

import pandas as pd
from osgeo import gdal
from osgeo import gdalconst

from .geetasks import check_gee_split


def gdal_is_valid(fp, print_err=False):
    """Checks if `fp` is  valid file as tested from gdal's checksum function. Not an infalible check, but it is
    quick and should capture most cases.
    Adapted from https://lists.osgeo.org/pipermail/gdal-dev/2013-November/037520.html
    """
    fp = str(fp)
    try:
        ds = gdal.Open(fp)
        for i in range(ds.RasterCount):
            ds.GetRasterBand(i + 1).Checksum()
    except RuntimeError:
        valid = False
        if print_err:
            print('GDAL error: ', gdal.GetLastErrorMsg())
    else:
        valid = True
    return valid


def gdal_wait(fp, wait=10, maxwait=600):
    """Waits until file `fp` becomes valid as tested from gdal's checksum function. Not an infalible check, but it is
    quick and should capture most cases. Waits for `wait` seconds between checks, up to a maximum of `maxwait` seconds.
    Assumes `fp` already exists on disk, otherwise stops execution.
    """
    gdal.UseExceptions()
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    slept = 0
    while not Path(fp).exists():
        print(f'This file does not exist yet: {fp} \nWill wait a bit (up to {maxwait} s).')
        gee_did_split, fps = check_gee_split(fp)
        if gee_did_split:
            print(f'It turns out GEE had split the download in {len(fps)} files! Checking these now: {fps}')
            fp = fps
            break
        time.sleep(wait)
        slept += wait
        if slept >= maxwait:
            raise FileNotFoundError(f'Waited too long ({maxwait} s) for this file to exist: {fp} \n'
                                    f'Cannot continue without it.')

    if not isinstance(fp, list):
        fp = [fp]

    for fpath in fp:
        if not gdal_is_valid(fpath):
            print(f'This file exists but it is not valid: {fpath} \n'
                  f'Will wait a bit (up to {maxwait} s) until it becomes valid.')
            while not gdal_is_valid(fpath):
                if slept >= maxwait:
                    warnings.warn(f'Waited too long ({maxwait} s) for this file to become valid: {fpath} \nMoving on.',
                                  RuntimeWarning)
                    break
                time.sleep(wait)
                slept += wait
            else:
                print(f'The file is valid now. Waited for {slept} s.')


def img_rename(imgname, cap=8):
    imgname = str(imgname)
    new_name = sha256(imgname.encode()).hexdigest()[:cap]
    return new_name


def replace_prefix(fp, old, new):
    fp = Path(fp)
    new_stem = fp.stem.replace(old, new)
    new_path = fp.parent / (new_stem + fp.suffix)
    return new_path


def exclude_tiles(flist, tiles):
    filtered = []
    for fp in flist:
        fp = Path(fp)
        stem = fp.stem
        tile = stem.split('_')[-2]
        if tile not in tiles:
            filtered.append(fp)
    return filtered


def batch_rename_prefix(fdir, old, new, tiles=None):
    fdir = Path(fdir)
    fpaths = fdir.glob('*.tif')
    if tiles is not None:
        fpaths = exclude_tiles(fpaths, tiles)
    for fp in fpaths:
        if old in fp.name:
            new_path = replace_prefix(fp, old, new)
            fp.rename(new_path)


def rename_from_dict(fdir, rename_dict, tiles=None):
    for old, new in rename_dict.items():
        batch_rename_prefix(fdir, old, new, tiles)


def get_info_key(fp, key, findn=1):
    finfo = gdal.Info(fp)
    ftype = re.findall(rf'({key}\s?=\s?\w+)', finfo)
    ftype = [f.split('=')[1].strip() for f in ftype]
    if findn != 'all':
        ftype = ftype[:findn]
    return ftype


def get_tiff_type(fp):
    """Uses gdalinfo to retrieve the data type within the dataset located in the `fp` path."""
    ftypes = pd.unique(get_info_key(fp, 'Type', 'all'))
    if len(ftypes) > 1:
        warnings.warn(f'The file {fp} has more than one data type: {ftypes}. Using only the first one ({ftypes[0]}).')
    return ftypes[0]


def get_tiff_interleave(fp):
    return get_info_key(fp, 'INTERLEAVE')[0]


def get_tiff_descriptions(fp):
    return get_info_key(fp, 'Description', 'all')


def compress_tiff(fp, outfp=None, ftype=None, compress_method='LZW', interleave='BAND'):
    """Compresses a tiff file. Defaults to LZW. ZSTD requires GDAL >= 2.3.
        Uses gdal_translate: https://gdal.org/programs/gdal_translate.html
        GeoTiff creation options: https://gdal.org/drivers/raster/gtiff.html#creation-options
        """
    fp = str(fp)
    outfp = str(outfp) if outfp is not None else fp[:-4] + '_zstd.tif'

    ftype = ftype if ftype is not None else get_tiff_type(fp)

    if 'float' in ftype.lower():
        predictor = 3
    else:
        predictor = 2

    translate_options = gdal.TranslateOptions(format='GTiff', strict=True,
                                              creationOptions=[
                                                  'TFW=NO',
                                                  # 'COMPRESS=ZSTD',
                                                  f'COMPRESS={compress_method}',
                                                  f'INTERLEAVE={interleave}',
                                                  'NUM_THREADS=ALL_CPUS',
                                                  f'PREDICTOR={predictor}',
                                                  'ZSTD_LEVEL=15',
                                                  'TILED=YES',
                                              ])

    ds = gdal.Translate(outfp, fp, options=translate_options)
    ds = None
    return outfp


def gdal_warp_compressed(out_path, in_path, interleave=None, **kwargs):
    vrt = f'/vsimem/{Path(out_path).stem}.vrt'
    g = gdal.Warp(vrt, in_path, **kwargs)
    interleave = interleave if interleave is not None else get_tiff_interleave(in_path)
    compress_tiff(vrt, out_path,
                  ftype=get_tiff_type(in_path),
                  interleave=interleave,
                  )
    g = None
    gdal.Unlink(vrt)
    return out_path


def gdal_set_descriptions(fp, descriptions=None, band=None, copy_from=None):
    """Adapted from: https://github.com/scottstanie/apertools/blob/master/apertools/sario.py
    """
    ds = gdal.Open(str(fp), gdalconst.GA_Update)
    if isinstance(band, int):
        bands = [band]
    else:
        bands = range(1, ds.RasterCount + 1)

    if isinstance(descriptions, str):
        descriptions = [descriptions] * len(bands)
    elif copy_from is not None:
        descriptions = get_tiff_descriptions(copy_from)
    else:
        descriptions = [f'Band {b}' for b in bands]

    for band_num, dd in zip(bands, descriptions):
        b = ds.GetRasterBand(band_num)
        b.SetDescription(dd)
        b = None
    ds = None
