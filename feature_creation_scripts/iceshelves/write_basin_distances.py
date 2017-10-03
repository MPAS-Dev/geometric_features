#!/usr/bin/env python

import numpy
from netCDF4 import Dataset

import scipy.misc

import skfmm
import os

import matplotlib.pyplot as plt

def readBasinImage(name):
  basinImage = scipy.misc.imread('basins/%s.png'%name)
  data = 1.0 - numpy.array(basinImage[::-1,:,0],float)/255.
  return data


inFileName = 'Bedmap2_ice_shelf_distance.nc'

inFile = Dataset(inFileName,'r')

X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]

inFile.close()

(ny,nx) = X.shape

dx = 1e3

basinCount = 27
names = []
for index in range(basinCount):
  name = 'Antarctica_IMBIE%i'%(index+1)
  names.append(name)

#==============================================================================
# basinSum = numpy.zeros((ny,nx))
# for basinIndex in range(len(names)):
#   name = names[basinIndex]
#   print name
#   data = readBasinImage(name)
#   basinSum += data
#
# plt.figure(1)
# plt.imshow(basinSum)
# plt.colorbar()
# plt.gca().invert_yaxis()
# plt.show()
# exit()
#==============================================================================


outFileName = 'Bedmap2_grid_basin_distances.nc'
outFile = Dataset(outFileName,'w')

outFile.createDimension('x',nx)
outFile.createDimension('y',ny)
outFile.createDimension('basinCount',basinCount)
var = outFile.createVariable('distances','f8',('basinCount','y','x'))

os.makedirs('dist')

for basinIndex in range(len(names)):
  name = names[basinIndex]
  print name
  data = readBasinImage(name)
  distance = skfmm.distance(2.0*data-1.0,dx=dx)
  plt.figure(1)
  plt.imshow(distance)
  plt.colorbar()
  plt.gca().invert_yaxis()
  plt.savefig('dist/%s.png'%name)
  plt.close()
  var[basinIndex,:,:] = distance

outFile.close()



