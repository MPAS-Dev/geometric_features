#!/usr/bin/env python
"""
This script reads features from the input features file pointed to with the -f
flag, adds a group name given with the -g flag, and writes the features to the
same file.

Authors: Xylar Asay-Davis, Phillip J. Wolfram
Last Modified: 03/16/2017
"""

import os
import json
from collections import defaultdict
from utils.feature_write_utils import write_all_features
from utils.feature_test_utils import feature_already_exists


def write_group_name(feature_file, groupName): # {{{
    """

    Adds groupName property to a given feature file.



    Authors: Xylar Asay-Davis, Phillip J. Wolfram
    Last Modified: 03/16/2017
    """

    if not os.path.exists(feature_file):
        raise ValueError('File {} does not exist.'
                         .format(feature_file))

    all_features = defaultdict(list)

    with open(feature_file) as f:
        filevals = json.load(f)

        for feature in filevals['features']:
            if not feature_already_exists(all_features, feature):
                all_features['features'].append(feature)

    all_features['groupName'] = groupName

    write_all_features(all_features, feature_file, indent=4)

    return # }}}

if __name__ == "__main__":
    import argparse
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

    write_group_name(args.feature_file, args.groupName)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
