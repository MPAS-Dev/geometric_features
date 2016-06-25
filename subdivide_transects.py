#!/usr/bin/env python

"""
This script takes a file containing one or more feature definitions,
pointed to by the -f flag and a flag -m indicating the maximum length of
segments of transects in degrees.  Segments of transects (LineStrings
or MultiLineStrings) that are longer than the maximum are subdivided into an
integer number of subsegments so the minimum is reached. Results are written
to the file pointed to with the -o flag (features.geojson by default).

Author: Xylar Asay-Davis
Last Modified: 10/22/2016
"""

import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features
from utils.feature_test_utils import feature_already_exists

import os.path

import shapely.geometry
import shapely.ops
import numpy

def subdivide_LineString(inShape):
    inCoords = inShape.coords
    segmentCount = len(inCoords)-1
    outCoords = [inCoords[0]]
    subdivided = False

    for segIndex in range(segmentCount):
        p0 = inCoords[segIndex]
        p1 = inCoords[segIndex+1]
        length = numpy.sqrt((p1[0]-p0[0])**2 + (p1[1]-p0[1])**2)
        subCount = int(numpy.ceil(length/args.max_degrees))
        if subCount== 1:
          outCoords.append(p1)
        else:
          subdivided = True
          x = numpy.linspace(p0[0],p1[0],subCount)
          y = numpy.linspace(p0[1],p1[1],subCount)
          for subIndex in range(1,subCount):
            outCoords.append([x[subIndex],y[subIndex]])

    if subdivided:
        return shapely.geometry.LineString(outCoords)
    else:
        return inShape


parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file",
                    help="Single feature with transects to be subdivided", metavar="FILE1",
                    required=True)
parser.add_argument("-m", "--max_degrees", dest="max_degrees", type=float, default=1.0,
                    help="Maximum degrees between points on a transect after subdivision",
                    metavar="SUBDIV", required=False)
parser.add_argument("-o", "--output", dest="output_file_name",
                    help="Output file, e.g., features.geojson.", metavar="PATH",
                    default="features.geojson")

args = parser.parse_args()


out_file_name = args.output_file_name

all_features = defaultdict(list)

if os.path.exists(out_file_name):
    try:
        with open(out_file_name) as f:
            appended_file = json.load(f)
            for feature in appended_file['features']:
                all_features['features'].append(feature)
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
    if feature_already_exists(all_features, feature):
        continue
    name = feature['properties']['name']
    geomType = feature['geometry']['type']
    if geomType == 'LineString':
        inShape = shapely.geometry.shape(feature['geometry'])
        outShape = subdivide_LineString(inShape)
        feature['geometry'] = shapely.geometry.mapping(outShape)
    elif geomType == 'MultiLineString':
        inShape = shapely.geometry.shape(feature['geometry'])
        shapeList = []
        for lineString in inShape:
            shapeList.append(subdivide_LineString(lineString))
        outShape = shapely.ops.cascaded_union(shapeList)
        feature['geometry'] = shapely.geometry.mapping(outShape)

    all_features['features'].append(feature)


write_all_features(all_features, out_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
