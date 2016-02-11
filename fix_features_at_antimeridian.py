#!/usr/bin/env python

"""

This script is used to split features that cross the antimeridian (+/-180 lon).
The script reads from a single files containing the collection of features
to be split at the antimeridian (the file can be 'features.geojson') 
and produces a file 'features.geojson'where all features are made up of 
polygons that do not cross the antimeridian.

The code maps features into polar coordinates centered at the closest pole, 
which implicitly assumes that no segment of a feature will cover more than 
180 degrees longitude.  Segments within features that violate this assumption 
should be divided into sub-segments before calling this script.

The script makes use of the shapely library.

"""

import os
import numpy
import json
import argparse
from utils.feature_write_utils import write_all_features

import shapely.geometry
import shapely.ops

	
def splitGeometryCrossingAntimeridian(geometry):
	def toPolar(lon,lat):
		phi = numpy.pi/180.*lon
		radius = numpy.pi/180.*(90. - sign*lat)

		# nudge points at +/- 180 out of the way so they don't intersect the testing wedge
		phi = numpy.sign(phi)*numpy.where(numpy.abs(phi) > numpy.pi - 1.5*epsilon, numpy.pi - 1.5*epsilon, numpy.abs(phi))
		radius = numpy.where(radius < 1.5*epsilon, 1.5*epsilon, radius)
		
		
		x = radius*numpy.sin(phi)
		y = radius*numpy.cos(phi)
		if(isinstance(lon,list)):
			x = x.tolist()
			y = y.tolist()
		elif(isinstance(lon,tuple)):
			x = tuple(x)
			y = tuple(y)
						
		return (x,y)
	
	def fromPolar(x,y):
		radius = numpy.sqrt(numpy.array(x)**2+numpy.array(y)**2)
		phi = numpy.arctan2(x,y)

		# close up the tiny gap
		radius = numpy.where(radius < 2*epsilon, 0., radius)
		phi = numpy.sign(phi)*numpy.where(numpy.abs(phi) > numpy.pi - 2*epsilon, numpy.pi, numpy.abs(phi))
		
		lon = 180./numpy.pi*phi
		lat = sign*(90. - 180./numpy.pi*radius)
		
		
		if(isinstance(x,list)):
			lon = lon.tolist()
			lat = lat.tolist()
		elif(isinstance(x,tuple)):
			lon = tuple(lon)
			lat = tuple(lat)		
		return (lon,lat)
	
	epsilon = 1e-14
	antimeridianWedge = shapely.geometry.Polygon([(epsilon, -numpy.pi), 
																		(epsilon**2, -epsilon), 
																		(0, epsilon), 
																		(-epsilon**2, -epsilon), 
																		(-epsilon, -numpy.pi), 
																		(epsilon, -numpy.pi)])
	
	
	featureShape = shapely.geometry.shape(geometry)
	sign = 2.*(0.5*(featureShape.bounds[1] + featureShape.bounds[3]) >= 0.) - 1.
	polarShape = shapely.ops.transform(toPolar,featureShape)
	

	if(not polarShape.intersects(antimeridianWedge)):
		# this feature doesn't corss the antimeridian
		return

	print "This feature crosses the antimeridian"
	print "  bounds before split:", featureShape.bounds
		
	difference = polarShape.difference(antimeridianWedge)
	
	outShape = shapely.ops.transform(fromPolar,difference)
	
	print "  bounds after split:", outShape.bounds

	return shapely.geometry.mapping(outShape)


parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-f", "--features_file", dest="features_file", help="File containing features to split at the antimeridian", metavar="FILE", required=True)

args = parser.parse_args()

if args.features_file:
	if not os.path.exists(args.features_file):
		parser.error('The file %s does not exist.'%(args.features_file))

with open(args.features_file) as f:
	features_file = json.load(f)
	
for feature in features_file['features']:
	print feature['properties']['name']
	
	geometry = feature['geometry']
	
	result = splitGeometryCrossingAntimeridian(geometry)
	if(result is not None):
		feature['geometry'] = result

out_file_name = "features.geojson"

out_file = open(out_file_name, 'w')

out_file.write('{"type": "FeatureCollection",\n')
out_file.write(' "groupName": "enterNameHere",\n')
out_file.write(' "features":\n')
out_file.write('\t[\n')
write_all_features(features_file, out_file, '\t\t')
out_file.write('\n')
out_file.write('\t]\n')
out_file.write('}\n')

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
