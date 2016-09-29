#!/usr/bin/env python

"""
This script takes a file containing one or more feature definitions, that is
pointed to by the -f flag.  Features in the input file are simplified
using the shapely library with a tolerance (in degrees lon/lat) given
by -t flag.  If the -t flag is omitted, the default tolerance is zero
(so that points will not be allowed ot move at all, but may still be
simplified).  The result are stored in (or appended to) the output
file pointed to with the -o flag (features.geojson by default).

Author: Xylar Asay-Davis
Last Modified: 9/29/2016
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
                    help="Feature file to be simplified", metavar="FILE",
                    required=True)
parser.add_argument("-t", "--tolerance", dest="tolerance", type=float, default=0.0,
                    help="A distance in deg lon/lat by which each point in a feature can be moved during simpification",
                    metavar="TOLERANCE")

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

featuresToSimplify = defaultdict(list)

try:
    with open(args.feature_file) as f:
        feature_file = json.load(f)

    for feature in feature_file['features']:
        featuresToSimplify['features'].append(feature)

    del feature_file
except:
    print "Error parsing geojson file: %s"%(args.feature_file)
    raise

for feature in featuresToSimplify['features']:
    name = feature['properties']['name']
    if feature_already_exists(features, feature):
        print "Warning: feature %s already in features.geojson.  Skipping..."%name
        continue
    featureShape = shapely.geometry.shape(feature['geometry'])
    simplifiedFeature = featureShape.simplify(args.tolerance)
    feature['geometry'] = shapely.geometry.mapping(simplifiedFeature)
    features['features'].append(feature)

write_all_features(features, out_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
