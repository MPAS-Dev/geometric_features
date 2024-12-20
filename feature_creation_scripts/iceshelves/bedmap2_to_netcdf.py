#!/usr/bin/env python2

import numpy
from netCDF4 import Dataset
from progressbar import ETA, Bar, Percentage, ProgressBar

"""
This script converts the Bedmap2 binary dataset into a NetCDF file, including
longitude and latitude fields.  The Bedmap2 bindary dataset is available via
https://www.bas.ac.uk/project/bedmap-2/ and directly downloadable from
https://secure.antarctica.ac.uk/data/bedmap2/bedmap2_bin.zip

The Bedamp2 binary data is assumed to reside in the folder ./bedmap2_bin/.
This script produces the file bedmap2.nc in the current working directory.
"""

def readBedmap2Var(name, fillValue = -9999):
  field = numpy.fromfile('%s/bedmap2_%s.flt'%(inFolder,name),
               dtype = numpy.float32, count=nx*ny)
  field = field.reshape(nx,ny)
  field = field[::-1,:]
  if fillValue is not None:
      field = numpy.ma.masked_array(field, field == fillValue)

  return field

def addVariable(field, varName, outType):
    var = ncfile.createVariable(varName, outType, ('nx','ny'))
    var[:,:] = field
    print varName, numpy.amin(field), numpy.amax(field)


def makeBedmap2LonLat():
    projectionLat = -71.0*numpy.pi/180.0
    a = 6378137.0 # m  equatorial radius of the WGS84 ellipsoid according to Wikipedia
    f = 1/298.257223563 # oblateness of the WGS84 ellipsoid
    latToParametricLatFactor = numpy.sqrt(1.0 - (2*f - f**2)) # sqrt(1 - e^2)
    sinProjectionLat = numpy.sin(numpy.arctan(latToParametricLatFactor*numpy.tan(projectionLat)))

    # find the lon/lat of each bedmap2 point
    x = dx*(numpy.arange(nx)-0.5*(nx-1))
    y = dx*(numpy.arange(ny)-0.5*(ny-1))
    (X, Y) = numpy.meshgrid(x,y,indexing='ij')
    R = numpy.sqrt(X**2 + Y**2)
    Lon = numpy.arctan2(Y,X)*180./numpy.pi

    del X, Y

    stretch = 1.0

    iterCount = 30
    widgets = ['Computing latitudes: ', Percentage(), ' ', Bar(), ' ', ETA()]
    iterBar = ProgressBar(widgets=widgets, maxval=iterCount ).start()

    for iterIndex in range(iterCount):
        cosLat = stretch*R/a
        sinLat = -numpy.sqrt(1 - cosLat**2)
        stretch = (1.0 - sinLat)/(1.0 - sinProjectionLat)
        print "sinLat bounds:", numpy.amax(sinLat), numpy.amin(sinLat)
        print "stretch bounds:", numpy.amax(stretch), numpy.amin(stretch)
        iterBar.update(iterIndex+1)
    iterBar.finish()

    mask = cosLat != 0.0
    tanLat = sinLat[mask]/cosLat[mask]/latToParametricLatFactor
    Lat = -90.*numpy.ones(Lon.shape)
    Lat[mask] = numpy.arctan(tanLat)*180./numpy.pi

    return (x, y, Lon, Lat)

inFolder = './bedmap2_bin'
dx = 1e3 #m
nx = 6667
ny = 6667

ncfile = Dataset('Bedmap2.nc', 'w', format='NETCDF4')

ncfile.createDimension('nx',nx)
ncfile.createDimension('ny',ny)

iceThickness = readBedmap2Var('thickness')
surface = readBedmap2Var('surface')
draft = surface - iceThickness

addVariable(surface,'iceSurface','f4')
addVariable(iceThickness,'iceThickness','f4')
addVariable(draft,'iceDraft','f4')

del iceThickness, surface, draft

addVariable(readBedmap2Var('bed'),'bed','f4')

bedmap2Mask = readBedmap2Var('icemask_grounded_and_shelves', fillValue = None)

addVariable(bedmap2Mask,'bedmap2Mask','i4')

addVariable(numpy.array(bedmap2Mask < 0., int),'openOceanMask','i4')
addVariable(numpy.array(bedmap2Mask == 1., int),'floatingIceMask','i4')
bareBedrockMask = numpy.logical_not(readBedmap2Var('rockmask').mask)
groundedMask = numpy.logical_and(bedmap2Mask == 0., numpy.logical_not(bareBedrockMask))
addVariable(numpy.array(groundedMask,int),'groundedIceMask','i4')
addVariable(numpy.array(bareBedrockMask,int),'bareBedrockMask','i4')

(x, y, Lon, Lat) = makeBedmap2LonLat()

var = ncfile.createVariable('x', 'f4', ('nx',))
var[:] = x
var = ncfile.createVariable('y', 'f4', ('ny',))
var[:] = y
addVariable(Lon,'lon','f4')
addVariable(Lat,'lat','f4')


ncfile.close()
