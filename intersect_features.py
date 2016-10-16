#!/usr/bin/env python
"""
This script takes a file containing one or more feature definitions,
indicated by the -f flag, and a second set of one or more intersecting feature
definition, pointed to with the -i flag.  The resulting feature definitions
are the intersection of the original feature definitions with the all of the
intersecting features (i.e. the intersection of the intersecting features).
The resulting features are placed in (or appended to) the output file indicated
with the -o flag (features.geojson by default).

Authors: Xylar Asay-Davis
Last Modified: 10/16/2016
"""

import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features
from utils.feature_test_utils import feature_already_exists

import os.path

import shapely.geometry
import shapely.ops

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file",
                    help="Feature file to be intersected", metavar="FILE1",
                    required=True)
parser.add_argument("-i", "--intersection_file", dest="intersection_file",
                    help="Feature file with features whose intersection with"
                    "those in feature_file should be retained",
                    metavar="FILE2", required=True)
parser.add_argument("-g", "--groupName", dest="groupName",
                    help="Group name for output features",
                    metavar="GROUPNAME", default="enterGroupName")
parser.add_argument("-o", "--output", dest="output_file_name",
                    help="Output file name",
                    metavar="PATH", default="features.geojson")

args = parser.parse_args()


out_file_name = args.output_file_name

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

featuresToIntersect = defaultdict(list)

try:
    with open(args.feature_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        featuresToIntersect['features'].append(feature)

    del feature_file
except:
    print "Error parsing geojson file: %s" % (args.feature_file)
    raise

intersectionShape = None
try:
    with open(args.intersection_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        shape = shapely.geometry.shape(feature['geometry'])
        if intersectionShape is None:
            intersectionShape = shape
        else:
            intersectionShape = shape.intersection(intersectionShape)

    del feature_file
except:
    print "Error parsing geojson file: %s" % (args.mask_file)
    raise

for feature in featuresToIntersect['features']:
    name = feature['properties']['name']
    if feature_already_exists(features, feature):
        print "Warning: feature %s already in features.geojson.  " \
            "Skipping..." % name
        continue
    featureShape = shapely.geometry.shape(feature['geometry'])
    if featureShape.intersects(intersectionShape):
        print "%s has been intersected." % name
        featureShape = featureShape.intersection(intersectionShape)
        assert(not featureShape.is_empty)
        feature['geometry'] = shapely.geometry.mapping(featureShape)
        features['features'].append(feature)
    else:
        print "Warning: feature %s has no intersection with features in %s." \
            "Skipping..." % (name, args.intersection_file)

features['groupName'] = args.groupName

write_all_features(features, out_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
