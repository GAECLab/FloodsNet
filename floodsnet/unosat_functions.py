import os
import re
from pathlib import Path
from tempfile import TemporaryDirectory

import fiona
import geopandas as gpd
import numpy as np
from osgeo import gdal
from osgeo import ogr
from rasterio.crs import CRS
from shapely import Polygon
from typing_extensions import deprecated


def get_flood_layers_from_unosat_gdbs(unosat_lst):
    flood_lst = []
    for gdb in unosat_lst:
        layers = fiona.listlayers(gdb)
        # get a list of all floods from the layers in the gdb
        floods = [
            (gdb, fl) for fl in layers
            if (re.search('_Flood_', fl) and not re.search('Extent', fl)) or
            (re.search('_WaterExtent_', fl)) or
            (re.search('_CumulativeFloodWater', fl))
        ]
        flood_lst.extend(floods)
    return flood_lst


@deprecated('Seems to be unused.')
def save_flood_shapefiles(flood_hls, flood_layer):
    """Saves each flood split into HLS tiles.
        flood_hls : gpd.GeoPandasDataframe
    """
    for i in range(len(flood_hls)):
        tile = flood.identifier.values[0]
        flood = flood_hls.iloc[[i]]
        flood.to_file(f"../../UNOSAT_SAR/generated/shp/{flood_layer}_{tile}.shp", driver='ESRI Shapefile')
    return


@deprecated('Seems to be unused.')
def process_flood_layers(flood_lst, dt_set, hls_tiles):
    for gdb, flood_layer in flood_lst:
        gdf = gpd.read_file(gdb, layer=flood_layer)
        gdf_union = gdf.unary_union
        start_date, end_date, aoi = get_img_date_bbox(dt_set=dt_set, plus_days=4,
                                                      fl=gdf['Sensor_Date'].unique()[0],
                                                      shp=gdf_union)
        date_info = start_date.replace('-', '')
        gt_name = '_'.join([Path(gdb).stem, flood_layer])
        del gdf

        flood_hls = gpd.clip(hls_tiles, gdf_union)

        save_flood_shapefiles(flood_hls, flood_layer)


@deprecated('All usages have been replaced by get_utm_epsg_from_bounds')
def _get_utm_epsg(lon):
    '''
        Get the EPSG code for the UTM Zone based on input longitude.
    '''
    utm_zone = np.floor((lon + 180) / 6) + 1
    epsg = int(utm_zone + 32700) if lon < 0 else int(utm_zone + 32600)
    return CRS.from_string(f'EPSG:{epsg}')


def get_utm_epsg_from_bounds(bounds, crs):
    """
    Get the EPSG code for the UTM Zone based on an input bounding box.
    """
    bbox = Polygon([
        [bounds[0], bounds[1]],
        [bounds[2], bounds[1]],
        [bounds[2], bounds[3]],
        [bounds[0], bounds[3]]
    ])
    gs = gpd.GeoSeries(bbox, crs=crs)
    epgs = CRS.from_epsg(gs.estimate_utm_crs().to_epsg())
    return epgs


def rasterize_shp(flood_shp: gpd.GeoDataFrame, out_dir: str, gt_name: str, s2_path: str, date_info: str):
    tile = flood_shp.identifier.values[0]
    # START rasterize
    out_gt_path = f'{out_dir}/{gt_name}_{date_info}_{tile}_GT.tif'
    if not os.path.exists(out_gt_path):
        _rasterize_shp_layer(flood_shp, s2_path, out_gt_path)
    else:
        print(f'{out_gt_path} exists.')
    # END rasterize
    return out_gt_path


def _rasterize_shp_layer(flood_shp, s2_path, out_gt_path):
    s2_utm_crs = get_utm_epsg_from_bounds(flood_shp.bounds.values[0], flood_shp.crs)
    flood_reproj = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[flood_shp.geometry.values[0]]).to_crs(s2_utm_crs)
    # open the downloaded s2 image to use as a template
    dataSrc = gdal.Open(s2_path)
    temp_shp = '../temp.shp'
    flood_reproj.to_file(temp_shp)
    shp = ogr.Open(temp_shp)
    # with TemporaryDirectory() as tempdir:
    #     temp_shp = str(Path(tempdir) / 'temp.shp')
    #     flood_reproj.to_file(temp_shp)
    #     shp = ogr.Open(temp_shp)
    lyr = shp.GetLayer()
    driver = gdal.GetDriverByName('GTiff')

    dst_ds = driver.Create(
        out_gt_path,
        dataSrc.RasterXSize,
        dataSrc.RasterYSize,
        1,
        gdal.GDT_Byte,
        options=[
            'TFW=NO',
            # 'COMPRESS=ZSTD',
            f'COMPRESS=LZW',
            'NUM_THREADS=ALL_CPUS',
            f'PREDICTOR=2',
            # 'ZSTD_LEVEL=15',
            'TILED=YES',
        ])
    dst_ds.SetGeoTransform(dataSrc.GetGeoTransform())
    dst_ds.SetProjection(dataSrc.GetProjection())
    gdal.RasterizeLayer(dst_ds, [1], lyr, burn_values=[1])

    dst_ds, shp, lyr = None, None, None
    print(f'{out_gt_path} saved.')


def validate_date(dt, layer_name):
    """Checks if date `dt` is valid and if not tries to return a valid date.
    If the layer has `Cumulative` in its name, the date is assumed to be of the format StartDate_EndDay_LayerDesc,
    StartDate is of the format YYYYMMDD and it is returned as the start date of the flood event. EndDay is of the format
    DD and it is assumed to be the end day of the flood event, with same YYYYMM as the start date.
    """
    if dt is gpd.pd.NaT:
        if 'Cumulative' in layer_name:
            print(f'Layer {layer_name} does not have a valid sensor time. '
                  f'Deriving start and end dates from the layer name.')
            parts = layer_name.split('_')
            start = gpd.pd.to_datetime(parts[0]).strftime("%Y-%m-%d")
            # todo: handle cases where the end day is in the month following the start date
            end = gpd.pd.to_datetime(parts[0][:-2] + parts[1]).strftime("%Y-%m-%d")
            valid_date = [start, end]
        else:
            # todo: handle other layer types
            valid_date = dt
    else:
        valid_date = dt
    return valid_date
