#!/usr/bin/env python

import numpy
from netCDF4 import Dataset

import skfmm

import matplotlib.pyplot as plt

import scipy.ndimage.morphology as morphology

inFileName = 'Bedmap2.nc'
inFile = Dataset(inFileName,'r')

mask = inFile.variables['bedmap2Mask'][:,:]
topg = inFile.variables['bed'][:,:]

inFile.close()

(ny,nx) = mask.shape

dx = 1e3

topgMask = numpy.logical_not(topg.mask)
continentMask = numpy.zeros(mask.shape, bool)
continentMask[topgMask] = numpy.logical_or(mask[topgMask] >= 0,
                                           topg[topgMask] > -800)

# remove lakes
continentMask = morphology.binary_fill_holes(continentMask)

# remove islands
invMask = numpy.logical_not(continentMask)
invMask[3333:, 3333] = False
invMask = morphology.binary_fill_holes(invMask)

continentMask2 = numpy.logical_not(invMask)
continentMask2[3333:, 3333] = continentMask[3333:, 3333]

continentDistance = skfmm.distance(2.0*continentMask2-1.0,dx=dx)

isShelf = numpy.logical_and(mask == 1,topg < 0.0)

isShelf = morphology.binary_fill_holes(isShelf)


xCenter = numpy.linspace(-dx*0.5*(nx),dx*0.5*(nx),nx)
yCenter = numpy.linspace(-dx*0.5*(ny),dx*0.5*(ny),ny)

(X,Y) = numpy.meshgrid(xCenter,yCenter)


distance = skfmm.distance(2.0*isShelf-1.0,dx=dx)

outFileName = 'Bedmap2_ice_shelf_distance.nc'
outFile = Dataset(outFileName,'w')

outFile.createDimension('x',nx)
outFile.createDimension('y',ny)

var = outFile.createVariable('iceShelfDistance','f8',('y','x'))
var[:,:] = distance
var = outFile.createVariable('continentDistance','f8',('y','x'))
var[:,:] = continentDistance
var = outFile.createVariable('X','f8',('y','x'))
var[:,:] = X
var = outFile.createVariable('Y','f8',('y','x'))
var[:,:] = Y

outFile.close()

