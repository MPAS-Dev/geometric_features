#!/usr/bin/env python

import numpy
import csv
from netCDF4 import Dataset

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import skfmm

def getBoundinBox(mask):
  xIndices = numpy.nonzero(numpy.amax(mask,axis=0))[0]
  yIndices = numpy.nonzero(numpy.amax(mask,axis=1))[0]
  return (xIndices[0],xIndices[-1]+1,yIndices[0],yIndices[-1]+1)


shelfDistanceFileName = 'Bedmap2_ice_shelf_distance.nc'
shelfNumberFileName = 'Bedmap2_ice_shelf_numbers.nc'
outFileName = 'iceshelves.geojson'
namesFileName = 'ice_shelf_lat_lon.csv'
basinNumberFileName = 'Bedmap2_grid_basin_numbers.nc'

names = []
with open(namesFileName) as csvfile:
  csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
  first = True
  for row in csvreader:
    if(first):
      # skip the first row
      first = False
      continue
    names.append(row[0])
    index = len(names)-1

inFile = Dataset(shelfDistanceFileName,'r')
X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]
inFile.close()

inFile = Dataset(shelfNumberFileName,'r')
namedIceShelfNumbers = inFile.variables['namedIceShelfNumber'][:,:]+1
inFile.close()


(ny,nx) = X.shape

dx = 1e3
extent = [-dx*0.5*(nx+1),dx*0.5*(nx+1),dx*0.5*(ny+1),-dx*0.5*(ny+1)]

shelfCount = numpy.amax(namedIceShelfNumbers)+1

inFile = Dataset(basinNumberFileName,'r')
basinNumbers = inFile.variables['basinNumbers'][:,:]
inFile.close()

basinCount = numpy.amax(basinNumbers)+1

overlapField = namedIceShelfNumbers+shelfCount*(basinNumbers)
overlapField *= basinNumbers > 0
overlapField *= namedIceShelfNumbers > 0

overlaps = numpy.unique(overlapField)
overlapBasins = overlaps/shelfCount
overlapShelves = numpy.mod(overlaps,shelfCount)

overlapCount = len(overlaps)

overlapMap = -1*numpy.ones(shelfCount*basinCount)
for overlapIndex in range(overlapCount):
  overlapMap[overlaps[overlapIndex]] = overlapIndex

overlapField = overlapMap[overlapField]

# initialize extended overlap field to zeros
extendedOverlapField = numpy.zeros((ny,nx),int)
# initialize min. distance to shelf to infinity
distanceToOverlap = 1e30*numpy.ones((ny,nx))

for basinNumber in range(1,basinCount):
  # find shelf numbers of shelves that overlap with this basin
  overlapIndices = numpy.nonzero(overlapBasins == basinNumber)[0]

  basinMask = basinNumbers == basinNumber
  (xMin,xMax,yMin,yMax) = getBoundinBox(basinMask)
  localBasinMask = basinMask[yMin:yMax,xMin:xMax]
  localOverlap = overlapField[yMin:yMax,xMin:xMax]
  # for each overlap in this basin
  for overlapIndex in overlapIndices:
    shelfNumber = overlapShelves[overlapIndex]
    # find the distance from the overlap to all points in the basin
    phi = 1.0 - 2.0*(localOverlap == overlapIndex)
    distance = skfmm.distance(phi)
    # update shelf numbers and min distance based on distance to shelf
    mask = numpy.logical_and(localBasinMask, distance < distanceToOverlap[yMin:yMax,xMin:xMax])
    distanceToOverlap[yMin:yMax,xMin:xMax][mask] = distance[mask]
    extendedOverlapField[yMin:yMax,xMin:xMax][mask] = overlapIndex

outFileName = 'extendedOverlaps.nc'
outFile = Dataset(outFileName,'w')

outFile.createDimension('x',nx)
outFile.createDimension('y',ny)
outFile.createDimension('overlapCount',overlapCount)
var = outFile.createVariable('extendedOverlapField','i4',('y','x'))
var[:,:] = extendedOverlapField

var = outFile.createVariable('overlapBasins','i4',('overlapCount'))
var[:] = overlapBasins

var = outFile.createVariable('overlapShelves','i4',('overlapCount'))
var[:] = overlapShelves

outFile.close()


#plt.figure(1)
#plt.imshow(extendedOverlapField, extent=extent, interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.figure(2)
#plt.imshow(extendedOverlapField*(namedIceShelfNumbers > 0), extent=extent, interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.figure(3)
#plt.imshow(overlapField, extent=extent, interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.figure(4)
#plt.imshow(distanceToOverlap*(distanceToOverlap != 1e30), extent=extent, interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.show()
