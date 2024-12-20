#!/usr/bin/env python

import csv
import shutil

import matplotlib.pyplot as plt

from geometric_features import FeatureCollection, GeometricFeatures
from geometric_features.utils import write_feature_names_and_tags


def main():
    author = 'Milena Veneziani'

    # make a geometric features object that knows about the geometric data
    # cache up a couple of directories
    gf = GeometricFeatures(cacheLocation='../../geometric_data')

    fc = FeatureCollection()

    # ********* OSNAP array West *********

    # Read in OSNAP West lon,lat
    OSNAPwestLonLat = csv.reader(open('./OSNAParrayWest20210322.csv', 'r'))
    # Skip 4 header lines
    next(OSNAPwestLonLat, None)
    next(OSNAPwestLonLat, None)
    next(OSNAPwestLonLat, None)
    next(OSNAPwestLonLat, None)
    coords = []
    for line in OSNAPwestLonLat:
        coords.append([float(line[0]), float(line[1])])

    feature = {}
    feature['type'] = 'Feature'
    feature['properties'] = {}
    feature['properties']['name'] = 'OSNAP section West'
    feature['properties']['tags'] = 'arctic_sections'
    feature['properties']['object'] = 'transect'
    feature['properties']['component'] = 'ocean'
    feature['properties']['author'] = author
    feature['geometry'] = {}
    feature['geometry']['type'] = 'LineString'
    feature['geometry']['coordinates'] = coords
    fcOW = FeatureCollection([feature])
    fcOW.plot(projection='northpole')
    fc.merge(fcOW)

    # ********* OSNAP array East *********

    # Read in OSNAP East lon,lat
    OSNAPeastLonLat = csv.reader(open('./OSNAParrayEast20210322.csv', 'r'))
    # Skip 4 header lines
    next(OSNAPeastLonLat, None)
    next(OSNAPeastLonLat, None)
    next(OSNAPeastLonLat, None)
    next(OSNAPeastLonLat, None)
    coords = []
    for line in OSNAPeastLonLat:
        coords.append([float(line[0]), float(line[1])])

    feature = {}
    feature['type'] = 'Feature'
    feature['properties'] = {}
    feature['properties']['name'] = 'OSNAP section East'
    feature['properties']['tags'] = 'arctic_sections'
    feature['properties']['object'] = 'transect'
    feature['properties']['component'] = 'ocean'
    feature['properties']['author'] = author
    feature['geometry'] = {}
    feature['geometry']['type'] = 'LineString'
    feature['geometry']['coordinates'] = coords
    fcOE = FeatureCollection([feature])
    fcOE.plot(projection='northpole')
    fc.merge(fcOE)

    # "split" these features into individual files in the geometric data cache
    gf.split(fc)

    # update the database of feature names and tags
    write_feature_names_and_tags(gf.cacheLocation)
    # move the resulting file into place
    shutil.copyfile('features_and_tags.json',
                    '../../geometric_features/features_and_tags.json')

    plt.show()


if __name__ == '__main__':
    main()
