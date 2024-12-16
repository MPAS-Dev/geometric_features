import numpy

def toPolar(points):
  lons = numpy.pi*points[:,0]/180.
  lats = numpy.pi*points[:,1]/180.
  projectionLat = -71.0*numpy.pi/180.0
  a = 6378137.0 # m  equatorial radius of the WGS84 ellipsoid according to Wikipedia
  f = 1/298.257223563 # oblateness of the WGS84 ellipsoid
  latToParametricLatFactor = numpy.sqrt(1.0 - (2*f - f**2)) # sqrt(1 - e^2)
  projectionLat = -71.0*numpy.pi/180.0
  sinProjectionLat = numpy.sin(numpy.arctan(latToParametricLatFactor*numpy.tan(projectionLat)))

  parametricLats = numpy.arctan(latToParametricLatFactor*numpy.tan(lats))
  sinParametricLats = numpy.sin(parametricLats)

  stretch = (1.0 - sinProjectionLat)/(1.0 - sinParametricLats)


  y = a*stretch*numpy.cos(parametricLats)*numpy.cos(lons)
  x = a*stretch*numpy.cos(parametricLats)*numpy.sin(lons)

  points[:,1] = y
  points[:,0] = x
  return points

def fromPolar(points):
  projectionLat = -71.0*numpy.pi/180.0
  a = 6378137.0 # m  equatorial radius of the WGS84 ellipsoid according to Wikipedia
  f = 1/298.257223563 # oblateness of the WGS84 ellipsoid
  latToParametricLatFactor = numpy.sqrt(1.0 - (2*f - f**2)) # sqrt(1 - e^2)
  projectionLat = -71.0*numpy.pi/180.0
  sinProjectionLat = numpy.sin(numpy.arctan(latToParametricLatFactor*numpy.tan(projectionLat)))


  Lons = 180.0/numpy.pi*numpy.arctan2(points[:,0],points[:,1])

  stretch = 1.0
  for iterIndex in range(10):
    cosParametricLats = stretch*numpy.sqrt(points[:,0]**2+points[:,1]**2)/a
    sinParametricLats = -numpy.sqrt(1.0 - cosParametricLats**2)
    stretch = (1.0 - sinParametricLats)/(1.0 - sinProjectionLat)
    #print iterIndex, numpy.amax(stretch)

  mask = cosParametricLats != 0
  Lats = -90.0*numpy.ones(Lons.shape)
  Lats[mask] = 180.0/numpy.pi*numpy.arctan(sinParametricLats[mask]/cosParametricLats[mask]/latToParametricLatFactor)

  points[:,0] = Lons
  points[:,1] = Lats

  return points