#!/use/bin/env python

"""
Utility funcitons for writing geojson files from a dictionary of features.

Authors: Douglas Jacobsen, Xylar Asay-Davis
Last Modified: 10/22/2016
"""

import json
import sys

from collections import OrderedDict


def write_all_features(features, out_file_name, indent=4,
                       defaultGroupName='enterGroupName'):  # {{{
    json.encoder.FLOAT_REPR = lambda o: format(o, 'f')

    for index in range(len(features['features'])):
        features['features'][index] = \
            _check_feature(features['features'][index])

    features['type'] = 'FeatureCollection'

    # Make the feature an ordered dictionary so type and groupName come before
    # features (easier to read)
    outFeatures = OrderedDict((('type', features['type']),))
    if 'groupName' in features.keys():
        outFeatures['groupName'] = features['groupName']
    elif defaultGroupName is not None:
        outFeatures['groupName'] = defaultGroupName

    # Add the rest (except features)
    for key in sorted(features):
        if key not in ['type', 'groupName', 'features']:
            outFeatures[key] = features[key]

    # features go last for readability
    outFeatures['features'] = features['features']

    out_file = open(out_file_name, 'w')

    json.dump(outFeatures, out_file, indent=indent)

    return outFeatures
# }}}


def _check_feature(feature):  # {{{

    # Set property values that need to be set...
    if 'name' not in feature['properties'].keys():
        print "There was an error getting the name property from a feature. " \
            "Exiting..."
        sys.exit(1)

    if 'component' not in feature['properties'].keys():
        print "Feature %s has an issue with the component property. " \
            "Exiting..." % (feature['properties']['name'])
        sys.exit(1)

    if 'author' not in feature['properties'].keys():
        feature['properties']['author'] = ""

    if 'tags' not in feature['properties'].keys():
        feature['properties']['tags'] = ""

    if 'type' not in feature['geometry'].keys():
        print "Feature %s has an issue with the geometry type. Exiting..." \
            % (feature['properties']['name'])
        sys.exit(1)

    feature_type = feature['geometry']['type']

    # Determine object property value based on feature type.
    if feature_type == "Polygon" or feature_type == "MultiPolygon":
        object_type = "region"
    elif feature_type == "LineString" or feature_type == "MultiLineString":
        object_type = "transect"
    elif feature_type == "Point" or feature_type == "MultiPoint":
        object_type = "point"
    else:
        raise ValueError("Unsupported feature type %s" % feature_type)

    feature['properties']['object'] = object_type

    # Make the properties an ordered dictionary so they can be sorted
    outProperties = OrderedDict(
            (('name', feature['properties']['name']),
             ('tags', feature['properties']['tags']),
             ('object', feature['properties']['object']),
             ('component', feature['properties']['component']),
             ('author', feature['properties']['author'])))
    for key in sorted(feature['properties']):
        if key not in outProperties.keys():
            outProperties[key] = feature['properties'][key]

    # Make the geometry an ordered dictionary so they can keep it in the
    # desired order
    outGeometry = OrderedDict(
        (('type', feature['geometry']['type']),
         ('coordinates', feature['geometry']['coordinates'])))
    for key in sorted(feature['geometry']):
        if key not in outGeometry.keys():
            outGeometry[key] = feature['geometry'][key]

    # Make the feature an ordered dictionary so properties come before geometry
    # (easier to read)
    outFeature = OrderedDict((('type', 'Feature'),
                             ('properties', outProperties)))
    # Add the rest
    for key in sorted(feature):
        if key not in ['geometry', 'type', 'properties']:
            outFeature[key] = feature[key]

    # geometry goes last for readability
    outFeature['geometry'] = outGeometry

    return outFeature

# }}}
