# FloodsNet
FloodsNet is an open source, machine learning-ready remote sensing dataset for flood mapping. It compiles data from several open flood data repositories and global flood events around the globe.

The FloodsNet data set consists of 4 freely available datasets, which it augments (e.g., if only Sentinel 1 was provided for a flood event it pulls out the corresponding Sentinel 2 data and vice versa) and harmonizes the freely available datasets (e.g., streamlining naming convention, reprojecting to a common projection, downloading similar additional data such as the permanent water layer). The datasets are documented in the table below.

| Source  | Area of Focus | Number of Images | Name of Dataset |
|---------| ------------- | ---------------- | --------------- |
| [Mateo-Garcia et al. 2021](https://www.nature.com/articles/s41598-021-86650-z)| 119 global flood events | 422 flood extent maps | WorldFloods |
| [Bonafilia et al. 2020](https://ieeexplore.ieee.org/document/9150760) | 11 global flood events | 4,831 chips of 512 x 512 10m pixels (446 hand labeled)| Sen1Floods11|
| [Sleeter et al. 2020](https://www.sciencebase.gov/catalog/item/5f95c679d34e074d1b7fe4d5) | 100 flood events |  | USGS_Floods |
| [Nemni et al. 2020](https://www.mdpi.com/2072-4292/12/16/2532/htm) | 15 global flood events | 7 geodatabases | UNOSAT_Floods |


All the data are provided as image chips of permanent water downloaded from the JRC ([Pekel et al. 2016](https://www.nature.com/articles/nature20584)), seasonal water, derived from the JRC layer and implementing the methods described in [Martinis et al. 2022](https://www.sciencedirect.com/science/article/abs/pii/S0034425722001912?via%3Dihub), with classes including permanent and seasonal water, flood, land, and clouds. 

For each image chip we provide all [Sentinel-2](https://sentinel.esa.int/web/sentinel/missions/sentinel-2) bands and [Sentinel-1](https://sentinel.esa.int/web/sentinel/missions/sentinel-1/) VV and VH data.

In the data subfolder is where the flood_training_datasets subfolder is - this is where all the flood data are being downloaded to (see below on how to download the data).

General file structure in the `data/flood_training_datasets` subfolder:  
[DATASET, e.g., WorldFloods, Sen1Floods11, USGS_FloodTraining, and UNOSAT_SAR]  
Each DATASET folder has a `downloaded` subfolder which comes from the original data source.

`GENERATED_IMG_PATH` is a Gdrive folder for data downloads from the Google Earth Engine (GEE).  
Structure in this folder is:  
`global_flood_training`/`data/`<name of dataset e.g., WorldFloods, Sen1Floods11, usgs, unosat>/`generated` - this includes data that are being downloaded from GEE, but changes the format a bit, adds missing data sets (e.g., S1 in the case of WorldFloods), SEASONALWATERJRC (from GEE),
and cloudprobability, when available. 

All the resulting data (made available via the Zenodo links) is outputted to the `open_source_training` data folder. 

## DOWNLOAD FLOODSNET DATA:

FloodsNet harmonized data are available on Zenodo. The DOIs are listed below:

* FloodsNet_0:      [10.5281/zenodo.11509627](https://zenodo.org/records/11509627?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjBiM2FjYmY3LTcwZDAtNGQ5NC04MGE4LWE1Mjk3ZmQzNmI2NCIsImRhdGEiOnt9LCJyYW5kb20iOiJkYmFlNmE5ODY5ZmFiZjBiMTgyOWFlNWFiMWUwZGY0OCJ9.dmhLRxevYD8_6OIVkrd_RRi4ojzQv89pNRuSLfDbYpmvm8fNB1HDoY30J9yW-_e4f5XaEKCOaCnfNc4__ipd6w)
* FloodsNet_1:      [10.5281/zenodo.11540601](https://zenodo.org/records/11540601?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjZmZjgyOWEzLWU2NTktNDYzMC1iZWM5LTQ1Mjg2NzE4ODU5YiIsImRhdGEiOnt9LCJyYW5kb20iOiI1MGE0MjRjMGE1MGJlOWZjNWRlOGE1NGQzYzM2NjJhNCJ9.C_6vrwXtSMEVWRIn6qSdt8ZxmKNdGt0MCTXdhe5p-RFJy0f5ZQQhqqIQmbjn2h43HWtoE1knxtCLFhCA_LO2qQ)
* FloodsNet_2:      [10.5281/zenodo.11549010](https://zenodo.org/records/11549010?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6ImI5NzI1NDU0LWZjYjEtNDM2NS04ZTc4LWY0ZTliNjhkMjhmMSIsImRhdGEiOnt9LCJyYW5kb20iOiI0NDcxYjk1M2E4ZDljYmU5NWFjMDYzNGU4YzA2Mjg4NCJ9.FS6-TYkYUFfxt_PbDUaRzZN5Y1L2k-1vzpceb8eEMPbHqHw7kXpCQo7jft2vkedmFDMHGPykEq8Q7CQQJwz6Fg)
* FloodsNet_3:      [10.5281/zenodo.11555668](https://zenodo.org/records/11555668?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjhkNzJkNzU5LTc3MzMtNGQyOC04NmJhLTRkYWUxYTBmMzU3NSIsImRhdGEiOnt9LCJyYW5kb20iOiI5Mzg0YzJlY2FkMWE5YmQ4YWIwZGQwOGY4Yjc0Y2YyZCJ9.QVj2B40c7aDVaAJqlR9-MJPSQHZwL3v6nQd311g16M-QOg0Jy6ykHWAnZemQfcvTSeGoFNJ24ih7GVNoMBqkNg)
* FloodsNet_4:      [10.5281/zenodo.11563108](https://zenodo.org/records/11563108?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjlmMjlkNzU3LTY1YzgtNDY5Ni05NjNhLTZlZWFkYWM3Mzk3YiIsImRhdGEiOnt9LCJyYW5kb20iOiJlYzAxMDU2ZDA3MjdkZDNlNDllNDJlMmJkYmYxNDAyYyJ9.aRjclJBlUSzx3m5G2bgdV9PSfFwaH6xk9xEhy4I89ov_Ik_ATJk06mKiWOdaqla-ExEkcjzpBzwRRcjRdkAhfg)
* FloodsNet_5:      [10.5281/zenodo.11584556](https://zenodo.org/records/11584556?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjJhNDJkNjk0LTEwNDItNGE5Ny05YjBjLTdhY2U0MWM1MWM3MSIsImRhdGEiOnt9LCJyYW5kb20iOiI2OGNjZjc5YTNlMjdjY2I2NjcyOWUxNzNlNWE0NGVhYSJ9.8o4oW6JJ3_778815zQdY-PNxjS3GykeanFqDWp8mKBQJNfkViORdlUkfiYrHNjQqmRLrWAQ1pAoZ4MRA3ET70w)
* FloodsNet_Code:   [10.5281/zenodo.11625676](https://zenodo.org/uploads/11625676?token=eyJhbGciOiJIUzUxMiJ9.eyJpZCI6IjAzZWExMTg0LWJiOWYtNGU4Yy05OTA5LWJkOGUwZjViOGJlMyIsImRhdGEiOnt9LCJyYW5kb20iOiI1NDRlMzkwMmU1ODhiMGRkYWU2ZGMxYWIzYzU3OWE3OCJ9.b7xHBTUX4n10cI2qyjIgo6uDfIbH5GgldX9s7cn2QWXHtiDIpN9Hpzhc7RJSikV0HixDDlTpQqDJeCNEuZK-5w)

## INDIVIDUAL DATASETS:

Details about the training data sets:

1. WorldFloods 

[Mateo-Garcia et al. 2021](https://www.nature.com/articles/s41598-021-86650-z) compiled the WorldFloods dataset of 119 globally verified flooding events that have occured between November 2015 and March 2019 consisting of 422 flood extent maps from disaster response organizations. These are human annotated/semi-automated flood maps that were tested on five independent locations around the globe. The dataset comprises pairs of Sentinel 2 images and flood extent maps.

We downloaded the WorldFloods data from the test and val folders only (i.e., not the train folder data) from this [link](https://tinyurl.com/worldfloods). Table 1 in the [Scientific Reports paper](https://doi.org/10.1038/s41598-021-86650-z) shows the number of flood events and flood maps derived as validation and test data, namely 6 and 5 flood events, with 6 and 11 flood maps respectively.

The downloaded folder structure for the WorldFloods dataset:

* `S2` subfolders have the 10m 13-bands of S2 data stacks (not saved as separate bands)

* `PERMANENTWATERJRC` has the JRC data: 
    * jrc value : classification -- `{0: no data, 1: not water, 2: seasonal water, 3: permanent water}` from here: 
    https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_3_YearlyHistory?hl=en#bands
    * we count `{2 : seasonal water}` as floods at the moment
    * They used the JRC yearly permanent water data product available on Google Earth Engine, JRC Yearly History dataset, seasonal data are classified as seasonal if the pixel is classified as water for fewer months than the number of valid observed months per year. So this seasonality class does not let us know which season the pixel is covered in water or not.
    Read pg 6 here: https://storage.googleapis.com/global-surface-water/downloads_ancillary/DataUsersGuidev2.pdf for more info on how seasonality was computed: it's computed per year, permanent is 12 months of water, anything lower is seasonal 

* `GT` (GroundTruth) has the mapped floods as tifs by putting together cloud from cloud probability maps,
          water is floodmaps and JRC (I think either if flood/hydro in floodmaps or classes 2 or 3 in
          permanentjrc):
    * gt 'encoding_values' : classification -- `{0: 'invalid', 1: 'land', 2: 'water', 3: 'cloud'}`

* `floodmaps` has the flood polygons in a shp from the Emergency Management Services Rapid Activations (EMSR)
    * EMSR codes map to specific disaster events, including floods link <a href=https://emergency.copernicus.eu/mapping/list-of-activations-rapid> here </a>
    
They generated flood maps from the EMSR data (`/floodmaps`) and a cloud mask using either a GEE cloud mask for newer S2 images or the `s2cloudless` model from the `sentinel-hub` (`/cloudprob` or `/cloud_prob_edited`). They used the JRC data as a permanent water mask (`/PERMANENTWATERJRC`). They combined data from `/floodmaps`, `/cloudprob`, `/PERMANENTWATERJRC`, to generate the ground truth images (`/gt`).

The `meta` directory has JSON files with information about the satellite date, number of invalid S2 pixels, number of S2 pixels that are cloud, number of S2 pixels that were water, number of S2 pixels that were land, number of S2 pixels were flooded water, number of S2 pixels that were permanent water, and more.

In our new `seasonal_water_jrc.py`, we are getting a much more specific version of seasonality by following the idea of [Martinis et al., 2022](https://www.sciencedirect.com/science/article/abs/pii/S0034425722001912?via%3Dihub) where we look at the JRC Monthly History dataset from the past 2 years (and the 3 months in that season for each year, in our fully seasonal version). Here, we are classifying "water" where the pixel has been classified as water 100% of the time (for the monthly version) or 67% of the time (for the seasonal version). In this case, we are not distinguishing between seasonal and permanent water, because we will use them in the same way in relation to the ground truth and image assessment of a flood - we will say that this is not flood water because it is seasonal/permanent during this time of the year in this region.


2. Sen1Floods11

[Bonafilia et al. 2020](https://ieeexplore.ieee.org/document/9150760) developed and made freely available the Sen1Floods11 dataset, which consists of classified permanent water and flood water as well as raw Sentinel-1 imagery for 11 flood events. The dataset comprises 4,831 512x512 chips across 14 biomes, 357 ecoregions, and 6 continents. 

We downloaded all the data from [here](https://github.com/cloudtostreet/Sen1Floods11), using their recommended command line:
`gsutil -m rsync -r gs://sen1floods11`, after installing gsutils following the 'Installing from Tar or Zip archive' from Google Cloud [here](https://cloud.google.com/storage/docs/gsutil_install#alt-install).

The downloaded folder structure for the Sen1Floods11 dataset:

* `JRCWaterHand` has the JRC data:
    * jrc value : classification -- `{0 : NA, 1 : permanent water}`
        * They ignore seasonal/ephemeral/changing water classes
        * More accurately, they used the JRC transition layer, "which identifies 'permanent' water as pixels that were observed to have detected water presence at both the beginning (1984) and the end (2018) of the dataset" (Bonafilia et al., 2020)
* `LabelHand` = Ground truth hand labeled for validation
    * Hand label value : classification -- `{-1 : No data, 0 : non-water, 1 : water}`
        * 446 512x512 non-overlapping pixel chips from 11 flood events
        * Images with majority cloud cover, identified using a blue band reflectance threshold of < 0.2, were removed.
        * 75\% of chips used for hand labeling had > 0.02 km^2 of water and 25\% had <= 0.02 km^2
        * These images were hand labeled in GEE by trained remote sensing analysts
* `S2Hand` has the S2 data

All tifs labeled with `[COUNTRY NAME]`/`_[UNIQUE ID]`/`_[PARENT FOLDER NAME]`.tif

3. USGS_FloodTraining 

The dataset was developed to be input as training data for machine learning algorithms to generate flood maps across CONUS. 
The dataset is based on WorldView-2 and 3 from MAXAR. Data were labeled using “unsupervised classification for the initial spectral clustering, followed by expert-level manual interpretation and QA/QC peer review to finalize each labeled image”. Specifically for labeling, in a first step they used K-means clustering to perform an unsupervised classification into 20 classes. Analysts identified classes that represented water. If a class had water and non-water pixels, analysts either ran the unsupervised classification again only on the mixed class, or they manually interpretated pixels. 
Images have a spatial resolution of 1.65e-05x1.65e-05 degrees, which is approximately 2x2 meters. WorldView data range from 2015 to 2019.
WorldView source imagery was radiometrically corrected and projected and normalized for topographic relief. Images were labeled with 5 categories: water, not water, maybe water, clouds, and background/no data. There is no distinction between permanent water and episodic inundation (e.g., flood waters). 

Dataset is available at this [link](https://www.sciencebase.gov/catalog/item/5f95c679d34e074d1b7fe4d5). To download the dataset, download 
the 'RasterData_and_Metadata.zip' from the botttom of the page of the above link, unzip it and place it in the `data/` subfolder.

- USGS Flood Training Data  
    - Classified MAXAR WorldView images
        - Tif values: `{0: NA, 1: water, 2: not water, 3: maybe water, 4: clouds}`
        - XML: used to get WorldView image dates


4. UNOSAT dataset

This dataset was introduced in the paper by [Nemni et al. 2020](https://www.mdpi.com/2072-4292/12/16/2532/htm). The authors provide a link to their github page [here](https://github.com/UNITAR-UNOSAT/UNOSAT-AI-Based-Rapid-Mapping-Service).
We originally downloaded the data, which consisted of 7 geodatabases from this [link](http://floods.unosat.org/geoportal/catalog/main/home.page), but this link is no longer working. However, 6 geodatabases can be downloaded individually (FL20150703MMR from [here](https://data.humdata.org/dataset/geodata-of-flood-waters-over-western-rakhine-state-myanmar-july-15-2015), FL20170815BGD from [here](https://unosat.org/products/2534), FL20180501SOM from [here](https://unosat.org/products/2644), FL20180723LAO from [here](https://unosat.org/products/2654), FL20190715MMR from [here](https://unosat.org/products/2726), and TC20190312MOZ from [here](https://unosat.org/products/2699)) and those are the ones we used here as part of FloodsNet. 
The datasets provide 10 m S1 data (IW, Level-1 GRD, VV polarization, both ASC/DESC), and flood vector shapefiles, which were generated using a histogram-based method (threshold method) followed by extensive manual cleaning and visual inspection. The dataset used in the paper, UNOSAT, contains images of 15 flood events in East Africa and Southeast Asia. We downloaded several (7) geodatabases that differed in their data content. They are in the `UNOSAT_SAR/downloaded/zips`.


## HOW TO GET STARTED:

1. In a location of your choice, create a folder named `global_flood_training` and clone the FloodsNet repo there

2. Create the conda environment based on the yml file and using 
`conda env create --file=global_flood_training.yml`

3. Navigate to your `global_flood_training` folder and 
from Zenodo, and download the needed data from the three sources mentioned above (world_floods, sen1_floods11, usgs).

[please note that you can download the data available
in the data subfolder yourself by following the readme, all of 
these data are freely available, please note that while you can re-create 
the hls_land_tile.json, you are better off downloading it from [this](https://doi.org/10.5281/zenodo.8039173) Zenodo link]

4. So far the folder structure should be as follows:
* `global_flood_training`
    * floodsnet
    * data
      * flood_training_datasets
        * WorldFloods
        * Sen1Floods11
        * USGS_FloodTraining
        * UNOSAT_SAR
      * hls_land_tile.json
      * open_source_training - this will be created if it doen't exist 
    * .gitignore
    * global_flood_training.yml
    * README.md
    * requirements.txt
    * zenodo_how_to.md

5. You will also need to create a a gdrive folder for Google Earth Engine to download
files to, as per cli.py, this folder is the `GENERATED_IMG_PATH`.

6. If you get any errors with `ee.Initialize()`
with an error that looks like this:
`""Error 400 : invalid_request`
The version of the app you're using doesn't include the latest security features to keep you protected. 
Please make sure to download from a trusted source and update to the latest, most secure version. "", 
when trying `earthengine authenticate` 
you need to update the `conda update earthengine-api` (https://github.com/kvos/CoastSat/issues/293)
and try again. 

7. Run the code per dataset (-dt=world_floods, -dt=sen1_floods11, 
-dt=usgs, -dt=unosat):  
`python -m floodsnet -dt=unosat -gp=<'/Volumes/GoogleDrive/My Drive/projects'>`