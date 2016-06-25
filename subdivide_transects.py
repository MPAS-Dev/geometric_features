#!/usr/bin/env python

"""
This script takes a file containing one or more feature definitions,
pointed to by the -f flag and a flag -m indicating the maximum length of
segments of transects in degrees.  Segments of transects (LineStrings)
that are longer than the maximum are subdivided into an integer number
of subsegments so the minimum is reached. The resulting features are placed
in (or appended to) features.geojson.
"""

import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features

import os.path

import shapely.geometry
import shapely.ops
import numpy

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file",
                    help="Single feature with transects to be subdivided", metavar="FILE1",
                    required=True)
parser.add_argument("-m", "--max_degrees", dest="max_degrees", type=float, default=1.0,
                    help="Maximum degrees between points on a transect after subdivision",
                    metavar="SUBDIV", required=False)

args = parser.parse_args()


out_file_name = "features.geojson"

features = defaultdict(list)

if os.path.exists(out_file_name):
    try:
        with open(out_file_name) as f:
            appended_file = json.load(f)
            for feature in appended_file['features']:
                features['features'].append(feature)
            del appended_file
    except:
        pass

features = defaultdict(list)

try:
    with open(args.feature_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        features['features'].append(feature)

    del feature_file
except:
    print "Error parsing geojson file: %s"%(args.feature_file)
    raise


for feature in features['features']:
    name = feature['properties']['name']
    geomType = feature['geometry']['type']
    if geomType.lower() != 'linestring':
        continue
    inShape = shapely.geometry.shape(feature['geometry'])
    inCoords = inShape.coords
    segmentCount = len(inCoords)-1
    outCoords = [inCoords[0]]
    subdivided = False

    for segIndex in range(segmentCount):
        p0 = inCoords[segIndex]
        p1 = inCoords[segIndex+1]
        length = numpy.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)
        subCount = int(numpy.ceil(length/args.max_degrees))
        print subCount
        if subCount== 1:
          outCoords.append(p1)
        else:
          subdivided = True
          x = numpy.linspace(p0[0],p1[0],subCount)
          y = numpy.linspace(p0[1],p1[1],subCount)
          for subIndex in range(1,subCount):
            outCoords.append([x[subIndex],y[subIndex]])

    if subdivided:
        outShape = shapely.geometry.LineString(outCoords)
        feature['geometry'] = shapely.geometry.mapping(outShape)


out_file = open(out_file_name, 'w')
out_file.write('{"type": "FeatureCollection",\n')
out_file.write(' "groupName": "enterNameHere",\n')
out_file.write(' "features":\n')
out_file.write('\t[\n')
write_all_features(features, out_file, '\t\t')
out_file.write('\n')
out_file.write('\t]\n')
out_file.write('}\n')

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
