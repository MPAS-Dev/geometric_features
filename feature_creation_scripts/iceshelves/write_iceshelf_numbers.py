#!/usr/bin/env python

import numpy
import csv
from netCDF4 import Dataset

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import interp

from skimage import measure

import scipy.misc

import skfmm

from polar import toPolar

inFileName = 'Bedmap2_ice_shelf_distance.nc'
outFileName = 'Bedmap2_ice_shelf_numbers.nc'
namesFileName = 'ice_shelf_lat_lon.csv'

names = []
lats = []
lons = []
areas = []
with open(namesFileName) as csvfile:
  csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
  first = True
  for row in csvreader:
    if(first):
      # skip the first row
      first = False
      continue
    names.append(row[0])
    lats.append(float(row[1]))
    lons.append(float(row[2]))
    areas.append(float(row[3]))
    index = len(names)-1

namePoints = toPolar(numpy.array([lons,lats]).T)


inFile = Dataset(inFileName,'r')
iceShelfDistance = inFile.variables['iceShelfDistance'][:,:]
X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]
inFile.close()

(ny,nx) = X.shape

dx = 1e3
extent = [-dx*0.5*(nx+1),dx*0.5*(nx+1),dx*0.5*(ny+1),-dx*0.5*(ny+1)]

iceShelfMask = iceShelfDistance >= 0.0

basinImage = scipy.misc.imread('streamlines.png')
streamlines = 1.0 - numpy.array(basinImage[::-1,:,0],float)/255.

mask = streamlines > 0.0
iceShelfMask[mask] = 0

iceShelfNumbers = measure.label(iceShelfMask)

shelfCount = numpy.amax(iceShelfNumbers)+1

xMean = numpy.zeros(shelfCount)
yMean = numpy.zeros(shelfCount)

for shelfNumber in range(1,shelfCount):
  mask = iceShelfNumbers == shelfNumber
  xMean[shelfNumber] = numpy.mean(X[mask])
  yMean[shelfNumber] = numpy.mean(Y[mask])

shelfNumberOfNames = interp(iceShelfNumbers,X[0,:],Y[:,0],namePoints[:,0],namePoints[:,1],order=0)

# for named points that don't lie in a shelf, find the nearest one
nameIndices = numpy.nonzero(shelfNumberOfNames == 0)[0]
for nameIndex in nameIndices:
  shelfNumberOfNames[nameIndex] = numpy.argmin(numpy.sqrt((namePoints[nameIndex,0]-xMean)**2
                                                        + (namePoints[nameIndex,1]-yMean)**2))

closestNamedShelf = -1*numpy.ones((ny,nx),int)
minDistances = 1e30*numpy.ones((ny,nx))
shelfNameIndices = -1*numpy.ones(shelfCount,int)
for nameIndex in range(len(shelfNumberOfNames)):
  print nameIndex, '/', len(shelfNumberOfNames)
  # fill in the name indices of the shelves with names
  shelfNumber = shelfNumberOfNames[nameIndex]
  shelfNameIndices[shelfNumber] = nameIndex

  phi = 1.0 - 2.0*(iceShelfNumbers == shelfNumber)
  distance = skfmm.distance(phi)
  mask = distance < minDistances
  closestNamedShelf[mask] = nameIndex
  minDistances[mask] = distance[mask]

nameField = -1*numpy.ones((ny,nx),int)
for shelfNumber in range(1,shelfCount):
  if(shelfNameIndices[shelfNumber] < 0):
    # for shelves that don't have a name, find the nearest one
    nameIndex = interp(closestNamedShelf,X[0,:],Y[:,0],xMean[shelfNumber],yMean[shelfNumber],order=0)

    shelfNameIndices[shelfNumber] = nameIndex

  mask = iceShelfNumbers == shelfNumber
  nameField[mask] = shelfNameIndices[shelfNumber]


outFile = Dataset(outFileName,'w')

outFile.createDimension('x',nx)
outFile.createDimension('y',ny)
var = outFile.createVariable('namedIceShelfNumber','i4',('y','x'))
var[:,:] = nameField
outFile.close()

#plt.figure(1)
#plt.imshow(nameField, extent=extent, interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#for shelfNumber in range(1,shelfCount):
#  color = 'k'
#  plt.plot(xMean[shelfNumber],yMean[shelfNumber],'%s.'%color)
#  name = names[shelfNameIndices[shelfNumber]]
#  plt.text(xMean[shelfNumber],yMean[shelfNumber],
#    '%s %i %i'%(name,shelfNameIndices[shelfNumber],shelfNumber),
#    fontsize=8,color=color)
#plt.show()
