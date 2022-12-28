from __future__ import absolute_import, division, print_function, \
    unicode_literals

import glob
import json
from collections import OrderedDict
import os
import sys
import socket
import datetime


def write_feature_names_and_tags(cacheLocation='./geometry_data'):
    """
    Make a json file with all the available features and tags by component
    and object type, used to update the file when new geometric features are
    added to the repo

    Parameters
    ----------
    cacheLocation : str, optional
        The location of the geometric features cache
    """
    # Authors
    # -------
    # Xylar Asay-Davis
    outFileName = 'features_and_tags.json'
    fileNames = sorted(glob.glob('{}/*/*/*/*.geojson'.format(cacheLocation)))

    allFeaturesAndTags = OrderedDict()
    for fileName in fileNames:
        print(fileName)
        with open(fileName) as f:
            features = json.load(f)['features']
            feature = features[0]
            featureName = feature['properties']['name']
            componentName = feature['properties']['component']
            objectType = feature['properties']['object']
            tags = feature['properties']['tags'].split(';')
            if componentName not in allFeaturesAndTags:
                allFeaturesAndTags[componentName] = OrderedDict()
            if objectType not in allFeaturesAndTags[componentName]:
                allFeaturesAndTags[componentName][objectType] = OrderedDict()
            allFeaturesAndTags[componentName][objectType][featureName] = \
                tags

    outFile = open(outFileName, 'w')

    json.dump(allFeaturesAndTags, outFile, indent=2)


def provenance_command():
    """
    Get a string to use for provenance in each feature
    """
    # Authors
    # -------
    # Phillip J. Wolfram, Xylar Asay-Davis

    cwd = os.getcwd()
    user = os.getenv('USER')
    curtime = datetime.datetime.now().strftime('%m/%d/%y %H:%M')
    call = ' '.join(sys.argv)
    host = socket.gethostname()
    sep = ' : '
    provstr = sep.join([curtime,  host, user, cwd, call]) + ';'
    return provstr
