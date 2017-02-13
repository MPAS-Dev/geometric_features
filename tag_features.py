#!/usr/bin/env python

"""
This script takes a file containing a collection of one or more feature
definitions, that is pointed to by the -f flag and a tag name pointed to by
the -t flag.  The tag is added to each feature (if that feature does not
already have that tag.  Results are written to the file pointed to with
the -o flag (features.geojson by default).

Author: Xylar Asay-Davis
Last Modified: 9/29/2016
"""

import os.path
import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features


parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file",
                    help="Features collection file to be tagged",
                    metavar="FILE", required=True)
parser.add_argument("-t", "--tag", dest="tag",
                    help="Tag to add to all features",
                    metavar="TAG", required=True)
parser.add_argument("-r", "--remove", dest="remove", action='store_true',
                    help="Use this flag to signal removing a tag instead of "
                    "adding")
parser.add_argument("-o", "--output", dest="output_file_name",
                    help="Output file, e.g., features.geojson.",
                    metavar="PATH", default="features.geojson")

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

try:
    filePointer = open(args.feature_file, 'r')
except IOError:
    print "Error: file {} does not exist".format(args.feature_file)
    raise

appended_file = json.load(filePointer)
for feature in appended_file['features']:
    try:
        feature_tags = feature['properties']['tags']
    except KeyError:
        feature_tags = ''
    feature_tag_list = feature_tags.split(';')
    if args.remove:
        if args.tag in feature_tag_list:
            feature_tag_list.remove(args.tag)
        feature['properties']['tags'] = ';'.join(feature_tag_list)
    else:
        if args.tag not in feature_tag_list:
            if(feature_tags == ''):
                feature['properties']['tags'] = args.tag
            else:
                feature['properties']['tags'] = '{};{}'.format(feature_tags,
                                                               args.tag)

    all_features['features'].append(feature)

write_all_features(all_features, out_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
