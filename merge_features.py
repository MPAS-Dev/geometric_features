#!/usr/bin/env python
"""
This script has two modes of usage:
1. To create a new file (features.geojson) containing one or more features that
are pointed to using the -f or -d flags.

2. To append one or more features on an already existing features.geojson file,
again defined by the -f and -d flags.

The usage mode is automatically detected for you, depending on if the
output file exists or not before calling this script.  The output file
is pointed to using the -o flag (features.geojson by default).

When using this script, you can optionally give a list of tags in a semicolon
delimited list (e.g. "tag1;tag2;tag3"). Features are only added to
features.geojson if their tags property contains all of the tags listed on the
input line.

Authors: Douglas Jacobsen, Xylar Asay-Davis
Last Modified: 10/16/2016
"""

import os
import json
import argparse
import fnmatch
from collections import defaultdict
from utils.feature_write_utils import write_all_features
from utils.feature_test_utils import match_tag_list, feature_already_exists

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file", help="Single feature file to append to features.geojson", metavar="FILE")
parser.add_argument("-d", "--features_directory", dest="features_dir", help="Directory containing multiple feature files, each will be appended to features.geojson", metavar="PATH")
parser.add_argument("-t", "--tags", dest="tags", help="Semicolon separated list of tags to match features against.", metavar='"TAG1;TAG2;TAG3"')
parser.add_argument("-o", "--output", dest="output_file_name", help="Output file, e.g., features.geojson.", metavar="PATH", default="features.geojson")

args = parser.parse_args()

if not args.feature_file and not args.features_dir:
    parser.error('Either a feature file (-f) or a feature directory (-d) is required.')

if args.features_dir:
    if not os.path.exists(args.features_dir):
        parser.error('The path %s does not exist.'%(args.features_dir))

if args.feature_file:
    if not os.path.exists(args.feature_file):
        parser.error('The file %s does not exist.'%(args.feature_file))

master_tag_list = []
if args.tags:
    for tag in args.tags.split(';'):
        master_tag_list.append(tag)

file_to_append = args.output_file_name
all_features = defaultdict(list)

new_file = True
first_feature = True
if os.path.exists(file_to_append):
    new_file = False
    try:
        with open(file_to_append) as f:
            appended_file = json.load(f)
            for feature in appended_file['features']:
                all_features['features'].append(feature)
            del appended_file
    except:
        new_file = True

if args.feature_file:
    try:
        with open(args.feature_file) as f:
            feature_file = json.load(f)

            for feature in feature_file['features']:
                if match_tag_list(feature, master_tag_list):
                    if not feature_already_exists(all_features, feature):
                        all_features['features'].append(feature)

            del feature_file
    except:
        print "Error parsing geojson file: %s"%(args.feature_file)

if args.features_dir:
    paths = []
    for (dirpath, dirnames, filenames) in os.walk(args.features_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, '*.geojson'):
                paths.append('%s/%s'%(dirpath, filename))

    for path in sorted(paths):
        try:
            with open('%s'%(path), 'r') as f:
                feature_file = json.load(f)
                for feature in feature_file['features']:
                    if match_tag_list(feature, master_tag_list):
                        if not feature_already_exists(all_features, feature):
                            all_features['features'].append(feature)
                del feature_file
        except:
            print "Error parsing geojson file: %s"%(path)
    del paths

write_all_features(all_features, file_to_append, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
