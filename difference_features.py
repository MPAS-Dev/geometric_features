#!/usr/bin/env python

"""
This script takes a file containing one or more feature definitions, that is
pointed to by the -f flag and a second masking feature definition, pointed
to with the -m flag.  The masking features are masked out of (i.e. removed
from) the original feature definitions.  The resulting features are placed
in (or appended to) features.geojson.
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
                    help="Single feature file to be clipped", metavar="FILE1",
                    required=True)
parser.add_argument("-m", "--mask_file", dest="mask_file",
                    help="Single feature whose overlap with the first feature should be removed",
                    metavar="FILE2", required=True)

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

    if(add):
        if(masked):
            print "%s has been masked."%name
            feature['geometry'] = shapely.geometry.mapping(featureShape)
        features['features'].append(feature)
    else:
        print "%s has been removed."%name

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
