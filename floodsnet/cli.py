import argparse
from pathlib import Path

DOWNLOADED_IMG_PATH = Path('data/flood_training_datasets').resolve()
HLS_LAND_TILE_PATH = Path('data/hls_land_tiles.json').resolve()
OUT_DIR = Path('data/open_source_training').resolve()
# GENERATED_IMG_PATH needs to be a gdrive forlder for Google Earth Engine to dwl
GENERATED_IMG_PATH = Path('/Volumes/GoogleDrive/My Drive/projects/InProgress').resolve()


def parse_flood_training_data_args():
    """Parse the expected command-line arguments for .py."""
    parser = argparse.ArgumentParser(description='Formats flood training datasets.')

    parser.add_argument('-dt', '--dt_set', type=str,
                        default='all',
                        help='The dataset to be processed. Default is all datasets.'
                             'options are world_floods, sen1_floods11, unosat, usgs')
    parser.add_argument('-o', '--out_dir', type=Path,
                        default=OUT_DIR,
                        help='Output directory where files will be saved.')
    parser.add_argument('-p', '--path',
                        default=DOWNLOADED_IMG_PATH,
                        help='Path where the flood training datasets have been downloaded')
    parser.add_argument('-gp', '--generated_path',
                        default=GENERATED_IMG_PATH,
                        help='Path where the generated data for flood training have been downloaded')
    parser.add_argument('-s2p', '--s2_tile_path',
                        default=HLS_LAND_TILE_PATH,
                        help='Path where the the hls/s2 land tiles are located')

    return parser.parse_args()
