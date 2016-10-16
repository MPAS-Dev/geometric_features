#!/usr/bin/env python
"""
This script takes a file containing one or more feature definitions, that is
pointed to by the -f flag and a second set of one or more masking feature
definition, pointed to with the -m flag.  The masking features are masked out
of (i.e. removed from) the original feature definitions.  The resulting
features are placed in (or appended to) the output file pointed to with the
-o flag (features.geojson by default).

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
                    help="Feature file to be clipped", metavar="FILE1",
                    required=True)
parser.add_argument("-m", "--mask_file", dest="mask_file",
                    help="Feature file with one or more features whose overlap "
                         "with features in feature_file should be removed",
                    metavar="FILE2", required=True)
parser.add_argument("-o", "--output", dest="output_file_name",
                    help="Output file, e.g., features.geojson.",
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

featuresToMask = defaultdict(list)

try:
    with open(args.feature_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        featuresToMask['features'].append(feature)

    del feature_file
except:
    print "Error parsing geojson file: %s"%(args.feature_file)
    raise

mask = defaultdict(list)
try:
    with open(args.mask_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        if not feature_already_exists(mask, feature):
            mask['features'].append(feature)

    del feature_file
except:
    print "Error parsing geojson file: %s"%(args.mask_file)
    raise


for feature in featuresToMask['features']:
    name = feature['properties']['name']
    if feature_already_exists(features, feature):
        print "Warning: feature %s already in features.geojson.  Skipping..."%name
        continue
    featureShape = shapely.geometry.shape(feature['geometry'])
    add = True
    masked = False
    for maskFeature in mask['features']:
        maskShape = shapely.geometry.shape(maskFeature['geometry'])
        if featureShape.intersects(maskShape):
            masked = True
            featureShape = featureShape.difference(maskShape)
            if featureShape.is_empty :
                add = False
                break
            else:
                print "Masked feature %s with mask %s"%(name,maskFeature['properties']['name'])

    if(add):
        if(masked):
            print "%s has been masked."%name
            feature['geometry'] = shapely.geometry.mapping(featureShape)
        features['features'].append(feature)
    else:
        print "%s has been removed."%name

write_all_features(features, out_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
