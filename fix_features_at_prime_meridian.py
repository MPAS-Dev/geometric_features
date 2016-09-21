#!/usr/bin/env python

"""

This script is used to split features across the prime meridian.  The 
features should not cross the antimeridian (+/-180 lon), so the user should
call fix_features_at_antimeridian.py first if necessary before using this
tool.  The script reads from a single files containing the collection of 
features to be split at the prime meridian (the file can be 'features.geojson')
and produces a file 'features.geojson' where all features are made up of
polygons that do not cross the prime meridian.

The script makes use of the shapely library.

Author: Xylar Asay-Davis
Last Modified: 2/27/2016

"""

import os
import numpy
import json
import argparse
from utils.feature_write_utils import write_all_features

import shapely.geometry
import shapely.affinity


def splitGeometryCrossingPrimeMeridian(geometry):
    
    primeMeridian = shapely.geometry.LineString([(0.,-90.),(0.,90.)])
    featureShape = shapely.geometry.shape(geometry)

    if(not featureShape.intersects(primeMeridian)):
        return
  
    eastMask = shapely.geometry.Polygon([(0.,-90.),
                                         (180.,-90.),
                                         (180., 90.),
                                         (0., 90.),
                                         (0., -90.)])
                                        
    westMask = shapely.geometry.Polygon([(-180.,-90.),
                                         (0.,-90.),
                                         (0., 90.),
                                         (-180., 90.),
                                         (-180., -90.)])

    print "This feature crosses the prime merdian."
    print "  bounds before split:", featureShape.bounds

    westShape = featureShape.difference(eastMask)
    westShape = shapely.affinity.translate(westShape, 360., 0.)
    print "  bounds of western half:", westShape.bounds
    eastShape = featureShape.difference(westMask)
    print "  bounds of eastern half:", eastShape.bounds

    outShape = shapely.geometry.MultiPolygon([westShape,eastShape])

    print "  bounds after split:", outShape.bounds

    return shapely.geometry.mapping(outShape)


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--features_file", dest="features_file", help="File containing features to split at the antimeridian", metavar="FILE", required=True)
parser.add_argument("-o", "--output", dest="output_file_name", help="Output file, e.g., features.geojson.", metavar="PATH", default="features.geojson")


args = parser.parse_args()

if args.features_file:
    if not os.path.exists(args.features_file):
        parser.error('The file %s does not exist.'%(args.features_file))

with open(args.features_file) as f:
    features_file = json.load(f)

for feature in features_file['features']:
    print feature['properties']['name']

    geometry = feature['geometry']

    result = splitGeometryCrossingPrimeMeridian(geometry)
    if(result is not None):
        feature['geometry'] = result

write_all_features(features_file, args.output_file_name, indent=4)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
