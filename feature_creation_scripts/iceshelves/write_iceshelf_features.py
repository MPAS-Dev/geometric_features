#!/usr/bin/env python

import numpy
import json
import csv
from netCDF4 import Dataset
from shapely.geometry import Polygon, mapping, shape
from descartes import PolygonPatch

import matplotlib.pyplot as plt
import matplotlib.patches
import matplotlib.colors

import os

from mpl_toolkits.basemap import interp

from skimage import measure

import scipy.misc

import skfmm

from polar import fromPolar

from utils.feature_write_utils import write_all_features

import gc

overlapsFileName = 'extendedOverlaps.nc'
shelfDistanceFileName = 'Bedmap2_ice_shelf_distance.nc'
namesFileName = 'ice_shelf_lat_lon.csv'
basinFileName = 'Antarctic_Basins.geojson'
outFileName = 'iceshelves_before_fix.geojson'

shelfNames = []
with open(namesFileName) as csvfile:
  csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
  first = True
  for row in csvreader:
    if(first):
      # skip the first row
      first = False
      continue
    shelfNames.append(row[0])
    index = len(shelfNames)-1

with open(basinFileName) as f:
  basinData = json.load(f)

basinFeatures = basinData['features']

inFile = Dataset(shelfDistanceFileName,'r')
X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]
inFile.close()

(ny,nx) = X.shape

dx = 1e3
extent = [-dx*0.5*(nx+1),dx*0.5*(nx+1),dx*0.5*(ny+1),-dx*0.5*(ny+1)]


inFile = Dataset(overlapsFileName,'r')
extendedOverlapField = inFile.variables['extendedOverlapField'][:,:]
overlapBasins = inFile.variables['overlapBasins'][:]
overlapShelves = inFile.variables['overlapShelves'][:]
inFile.close()

overlapCount = len(overlapBasins)
print overlapCount


shelfOverlapCount = numpy.zeros(len(shelfNames))
for overlapIndex in range(1,overlapCount):
  shelfNumber = overlapShelves[overlapIndex]-1
  shelfOverlapCount[shelfNumber] += 1

tags = []
overlapNames = []
shelfOverlapIndices = numpy.zeros(len(shelfNames))
for overlapIndex in range(1,overlapCount):
  shelfNumber = overlapShelves[overlapIndex]-1
  shelfName = shelfNames[shelfNumber].replace(" ","_").replace("/","_")
  if(shelfOverlapCount[shelfNumber] == 1):
    name = shelfName
  else:
    name = '%s_%i'%(shelfName,shelfOverlapIndices[shelfNumber]+1)
  overlapNames.append(name)
  shelfOverlapIndices[shelfNumber] += 1
  featureTags = shelfName

  basinNumber = overlapBasins[overlapIndex]
  for featureIndex in range(len(basinFeatures)):
    basinFeature = basinFeatures[featureIndex]
    basinName = basinFeature['properties']['name']
    if(basinName == 'Antarctica_IMBIE%i'%basinNumber):
      break
  featureTags = '%s;%s;%s'%(featureTags,basinName,basinFeature['properties']['tags'])
  tags.append(featureTags)

  #print overlapNames[overlapIndex-1], basinNumber, featureTags


features = {'features': []}

# for each overlap
for overlapIndex in range(1,overlapCount):
  # create a feature
  feature = {}
  # add properties
  feature['properties'] = {}
  feature['properties']['name'] = overlapNames[overlapIndex-1]
  feature['properties']['component'] = 'iceshelves'
  feature['properties']['tags'] = tags[overlapIndex-1]
  feature['properties']['author'] = 'Xylar Asay-Davis'
  feature['properties']['object'] = 'region'

  # add geometry
  feature['geometry'] = {}


  # get a mask for this overlap
  mask = 1.0*(extendedOverlapField == overlapIndex)
  # do a contour plot of overlap == 0.5
  fig = plt.figure(1)
  cs = plt.contour(X,Y,mask,[0.5])
  # extract the contour as paths
  paths = cs.collections[0].get_paths()


  print overlapIndex, overlapNames[overlapIndex-1], len(paths)

  # convert the paths to lat/lon
  for index in range(len(paths)):
    paths[index].vertices = fromPolar(paths[index].vertices)

  # extract the contour as a polygon or multipolygon
  if(len(paths) == 1):
    # create a Polygon
    feature['geometry']['type'] = 'Polygon'
    feature['geometry']['coordinates'] = [paths[0].vertices.tolist()]
  else:
    # create a MultiPolygon
    feature['geometry']['type'] = 'MultiPolygon'
    polys = []
    for index in range(len(paths)):
      polys.append([paths[index].vertices.tolist()])
    feature['geometry']['coordinates'] = polys


  feature_name = feature['properties']['name']
  component = feature['properties']['component']
  object_type = feature['properties']['object']

  features['features'].append(feature)

  del cs, paths
  fig.clf()
  plt.close()
  gc.collect()

if os.path.exists(outFileName):
    os.remove(outFileName)
write_all_features(features, outFileName, indent=4)
