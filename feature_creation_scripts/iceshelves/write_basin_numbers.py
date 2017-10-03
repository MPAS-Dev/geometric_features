#!/usr/bin/env python

import numpy
from netCDF4 import Dataset

import matplotlib.pyplot as plt


inFileName = 'Bedmap2_ice_shelf_distance.nc'
basinFileName = 'Bedmap2_grid_basin_distances.nc'

inFile = Dataset(inFileName,'r')

continentDistance = inFile.variables['continentDistance'][:,:]
X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]

inFile.close()

(ny,nx) = X.shape

dx = 1e3

inFile = Dataset(basinFileName,'r')

basinCount = len(inFile.dimensions['basinCount'])
distancesVar = inFile.variables['distances']
minDistance = 1e30*numpy.ones((ny,nx))
basinNumber = numpy.zeros((ny,nx),dtype=int)
for basinIndex in range(basinCount):
  print basinIndex
  basinDistance = distancesVar[basinIndex,:,:]
  mask = -basinDistance < minDistance
  minDistance[mask] = -basinDistance[mask]
  basinNumber[mask] = basinIndex+1
inFile.close()

mask = continentDistance < 0
basinNumber[mask] = 0
minDistance[mask] = 0.0

outFileName = 'Bedmap2_grid_basin_numbers.nc'
outFile = Dataset(outFileName,'w')

outFile.createDimension('x',nx)
outFile.createDimension('y',ny)
var = outFile.createVariable('basinNumbers','i4',('y','x'))
var[:,:] = basinNumber
var = outFile.createVariable('minDistance','f8',('y','x'))
var[:,:] = minDistance

outFile.close()



#plt.figure(1)
#plt.imshow(basinNumber)
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.figure(2)
#plt.imshow(minDistance)
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.show()
