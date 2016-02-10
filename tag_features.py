#!/usr/bin/env python

"""
This script takes a file containing a collection of one or more feature 
definitions, that is pointed to by the -f flag and a tag name pointed to by 
the -t flag.  The tag is added to each feature (if that feature does not 
already have that tag.  Results are written back to the same feature file.
"""

import os.path
import json
import argparse
from collections import defaultdict
from utils.feature_write_utils import write_all_features


parser = argparse.ArgumentParser(description=__doc__, 
                                 formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--feature_file", dest="feature_file", 
                    help="Features collection file to be tagged", metavar="FILE",
                    required=True)
parser.add_argument("-t", "--tag", dest="tag", help="Tag to add to all features", 
                    metavar="TAG", required=True)

args = parser.parse_args()


out_file_name = args.feature_file
all_features = defaultdict(list)

new_file = True
first_feature = True
if os.path.exists(out_file_name):
  new_file = False
  try:
    with open(out_file_name) as f:
      appended_file = json.load(f)
      for feature in appended_file['features']:
        try:
          feature_tags = feature['properties']['tags']
        except:
          feature_tags = ''
        feature_tag_list = feature_tags.split(';')
        if args.tag not in feature_tag_list:
          if(feature_tags == ''):
            feature['properties']['tags'] = args.tag
          else:
            feature['properties']['tags'] = '%s;%s'%(feature_tags,args.tag)
    
        all_features['features'].append(feature)
      del appended_file
  except:
    new_file = True

out_file = open(out_file_name, 'w')

out_file.write('{"type": "FeatureCollection",\n')
out_file.write(' "groupName": "enterNameHere",\n')
out_file.write(' "features":\n')
out_file.write('\t[\n')
write_all_features(all_features, out_file, '\t\t')
out_file.write('\n')
out_file.write('\t]\n')
out_file.write('}\n')

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
