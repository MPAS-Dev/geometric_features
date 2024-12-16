#!/usr/bin/env python

import numpy
from netCDF4 import Dataset

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import interp

import scipy.ndimage.filters as filters

inFileName = 'Bedmap2_ice_shelf_distance.nc'
inFile = Dataset(inFileName,'r')
X = inFile.variables['X'][:,:]
Y = inFile.variables['Y'][:,:]
inFile.close()

velocityFileName = 'antarctica_ice_velocity_900m.nc'
inFile = Dataset(velocityFileName, 'r')
vx = inFile.variables['vx'][::-1,:]
vy = inFile.variables['vy'][::-1,:]
inFile.close()


(ny,nx) = vx.shape

dx = 9e2
xMin = -2800000.0
yMax = 2800000.0

x = xMin + dx*numpy.arange(nx)
y = yMax + dx*(numpy.arange(ny)-(ny-1))

maskValue=-1e34
Vx = interp(vx,x,y,X,Y,masked=maskValue)
Vx[Vx == maskValue] = 0.0
Vy = interp(vy,x,y,X,Y,masked=maskValue)
Vy[Vy == maskValue] = 0.0

mask = 1.0*numpy.logical_or(vx != 0, vy != 0)
Mask = interp(mask,x,y,X,Y,masked=maskValue)
Mask[Mask == maskValue] = 0.0

(ny,nx) = Vx.shape

filterSigma = 10.0

Vx = filters.gaussian_filter(Vx,filterSigma)
Vy = filters.gaussian_filter(Vy,filterSigma)
Mask = filters.gaussian_filter(Mask,filterSigma)

mask = Mask > 1e-6
Vx[mask] /= Mask[mask]
Vy[mask] /= Mask[mask]


outFileName = 'Bedmap2_grid_velocities.nc'
outFile = Dataset(outFileName,'w')

outFile.createDimension('x',nx)
outFile.createDimension('y',ny)
var = outFile.createVariable('vx','f8',('y','x'))
var[:,:] = Vx
var = outFile.createVariable('vy','f8',('y','x'))
var[:,:] = Vy

outFile.close()

#extent = [xMin,numpy.amax(x),yMax,numpy.amin(y)]

#extent = [numpy.amin(X),numpy.amax(X),numpy.amax(Y),numpy.amin(Y)]
#
#plt.figure()
#plt.imshow(Vx,extent=extent,interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.figure()
#plt.imshow(Vy,extent=extent,interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.figure()
#plt.imshow(Mask,extent=extent,interpolation='nearest')
#plt.colorbar()
#plt.gca().invert_yaxis()
#plt.show()
