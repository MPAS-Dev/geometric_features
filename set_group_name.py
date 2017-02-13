#!/usr/bin/env python
"""
This script reads features from the input features file pointed to with the -f
flag, adds a group name given with the -g flag, and writes the features to the
same file.

Authors: Xylar Asay-Davis
Last Modified: 10/16/2016
"""

import os
import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features
from utils.feature_test_utils import feature_already_exists

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file", required=True,
                    help="Input and output feature file where group name is to"
                    "be set", metavar="FILE")
parser.add_argument("-g", "--group", dest="groupName",
                    help="Feature group name", metavar="GROUPNAME",
                    required=True)

args = parser.parse_args()

if not os.path.exists(args.feature_file):
    parser.error('The file {} does not exist.'.format(args.feature_file))

all_features = defaultdict(list)

with open(args.feature_file) as f:
    feature_file = json.load(f)

    for feature in feature_file['features']:
        if not feature_already_exists(all_features, feature):
            all_features['features'].append(feature)

all_features['groupName'] = args.groupName

write_all_features(all_features, args.feature_file, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
