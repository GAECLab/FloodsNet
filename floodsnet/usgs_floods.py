import ee 
import xml.etree.ElementTree as ET


def get_usgs_img_date_bbox(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    caldate = root.findall('./dataqual/lineage/srcinfo/srctime/timeinfo/sngdate/caldate')[0].text
    year = caldate[:4]
    month = caldate[4:6]
    day = caldate[6:8]
    # get aoi bounds
    west = float(root.findall('./idinfo/spdom/bounding/westbc')[0].text)
    east = float(root.findall('./idinfo/spdom/bounding/eastbc')[0].text)
    north = float(root.findall('./idinfo/spdom/bounding/northbc')[0].text)
    south = float(root.findall('./idinfo/spdom/bounding/southbc')[0].text)
    # make aoi
    aoi = ee.Geometry.BBox(west, south, east, north)
    return year, month, day, aoi
