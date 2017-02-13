#!/usr/bin/env python

"""
This script takes a file containing one or more feature definitions, pointed
to by the -f flag, and a new name for the combined feature, provided through
the -n flag.  The geometry of the feature definitions are combined into a
single feature definition, which is placed in (or appended to)
the file pointed to with the -o flag (features.geojson by default).

Author: Xylar Asay-Davis
Last Modified: 10/16/2016
"""

import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features

import os.path

import shapely.geometry
import shapely.ops

import sys


parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file",
                    help="feature file with features to be combined",
                    metavar="FILE",
                    required=True)
parser.add_argument("-n", "--new_feature_name", dest="new_feature_name",
                    help="The new name of the combined feature",
                    metavar="NAME", required=True)
parser.add_argument("-o", "--output", dest="output_file_name",
                    help="Output file, e.g., features.geojson.",
                    metavar="PATH", default="features.geojson")

args = parser.parse_args()


out_file_name = args.output_file_name

features = defaultdict(list)

featureExists = False

if os.path.exists(out_file_name):
    try:
        with open(out_file_name) as f:
            appended_file = json.load(f)
            for feature in appended_file['features']:
                if feature['properties']['name'] == args.new_feature_name:
                    featureExists = True
                features['features'].append(feature)
            del appended_file
    except:
        pass

if featureExists:
    print "Warning: feature {} already in {}.  Nothing to do.".format(
        args.new_feature_name, out_file_name)
    sys.exit(0)


featuresToCombine = defaultdict(list)

try:
    with open(args.feature_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        featuresToCombine['features'].append(feature)

    del feature_file
except:
    print "Error parsing geojson file: {}".format(args.feature_file)
    raise

featureShapes = []
authors = []
featureNames = []
for feature in featuresToCombine['features']:
    featureShapes.append(shapely.geometry.shape(feature['geometry']))
    authors.append(feature['properties']['author'])
    featureNames.append(feature['properties']['name'])

combinedShape = shapely.ops.cascaded_union(featureShapes)

feature = {}
feature['properties'] = {}
feature['properties']['name'] = args.new_feature_name
feature['properties']['component'] = \
    featuresToCombine['features'][0]['properties']['component']
feature['properties']['tags'] = ''
feature['properties']['author'] = '; '.join(list(set(authors)))
feature['properties']['constituents'] = '; '.join(list(set(featureNames)))
feature['geometry'] = shapely.geometry.mapping(combinedShape)
features['features'].append(feature)

if feature['geometry']['type'] == 'GeometryCollection':
    raise ValueError(
        "Error: combined geometry from {} is of type GeometryCollection.\n"
        "       Most likely cause is that multiple feature types (regions, \n"
        "       points and transects) are being cobined.".format(
            args.feature_file))

write_all_features(features, out_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
