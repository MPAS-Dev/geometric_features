from netCDF4 import Dataset
import numpy
from matplotlib import pyplot
from matplotlib import _cntr as cntr

from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

from utils.feature_write_utils import write_all_features


import skfmm

from scipy.ndimage.filters import gaussian_filter

from mpl_toolkits.basemap import interp as basemap_interp

"""
This script takes as input the Bedmap2 topography data produced by the
bedmap2_to_netcdf.py script.  It produces the feature file
AntarcticIceCoverage.geojson containing two features:
1) AntarcticIceCoverage contains all grounded or floating ice in Antarctica
as well as all bare bedrock above sea level lying south of 60S
2) AntarcticGroundedIceCoverage contains all grounded ice in Antarctica
as well as all bare bedrock above sea level lying south of 60S

The script also produces images of the signed distance functions (both smoothed
and unsmoothed) used in creating the contours that define these regions as
a sanity check.

The resulting feature file can be split with:
./split_features.py -f AntarcticIceCoverage.geojson
to place the features within the subfolder for the bedamp2 component.
"""

def extract_geometry(mask):
    def add_antemeridian(inIndex, outIndex):
        # this segment crosses the x axis (prime meridian or antemeridian)
        frac = (-x0)/(x1-x0)
        yMid = (1.-frac)*ys[inIndex] + frac*ys[inIndex+1]
        if yMid > 0:
            # segment crosses the prime meridian, so that's fine
            return

        # segment crosses the antemeridian
        # break it into 6 segments, including the south pole
        if x0 < x1:
            newLon = [-180., -180., 0., 180., 180.]
        else:
            newLon = [180., 180., 0., -180., -180.]

        latMid = (1.-frac)*lats[outIndex] + frac*lats[outIndex+1]
        newLat = [latMid, -90, -90., -90, latMid]
        for i in range(5):
            lons.insert(outIndex+1,newLon[i])
            lats.insert(outIndex+1,newLat[i])
            outIndex += 1

        print(x0, x1, frac)
        print(ys[inIndex], ys[inIndex+1], yMid)
        print(lats[outIndex-5:outIndex+2], latMid)
        print(lons[outIndex-5:outIndex+2])
        pyplot.figure(1)
        pyplot.plot(xs,ys)
        pyplot.figure(2)
        pyplot.plot(lons,lats)
        pyplot.show()


    floatMask = numpy.zeros(mask.shape)
    floatMask[1:-1,1:-1] = numpy.array(mask[1:-1,1:-1],float)
    floatMask = 2.*floatMask - 1.

    distance = skfmm.distance(floatMask)
    print(name, 'distance', numpy.amin(distance), numpy.amax(distance))
    pyplot.imsave('%s_distance.png'%name, distance, vmin=-1., vmax=1.,origin='lower')

    # smooth it a little
    distance = gaussian_filter(distance, sigma = 0.5)
    print(name, 'distance smoothed', numpy.amin(distance), numpy.amax(distance))
    pyplot.imsave('%s_distance_smoothed.png'%name, distance, vmin=-1., vmax=1., origin='lower')

    contourObj = cntr.Cntr(X,Y,distance)

    contours = contourObj.trace(0.)

    vertexLists = contours[0:len(contours)/2]

    polys = []
    for v in vertexLists:
        xs = v[:,0]
        ys = v[:,1]
        lons = list(numpy.arctan2(xs,ys)*180./numpy.pi) # avoid seam
        lats = list(basemap_interp(Lat,x,y,xs,ys))


        inIndex = 0
        outIndex = 0
        while(inIndex < len(xs)-1):
            x0 = xs[inIndex]
            x1 = xs[inIndex+1]
            if (x0 >= 0) != (x1 >= 0):
                add_antemeridian(inIndex, outIndex)

            inIndex += 1
            outIndex += 1

        poly = Polygon([(i[0], i[1]) for i in zip(lons,lats)])
        if poly.is_valid:
            polys.append(poly)
        else:
            print(f"invalid shape with {v.shape[0]:d} vertices")

    return mapping(unary_union(polys))

inFile = Dataset('bedmap2.nc')

Lon = inFile.variables['lon'][:,:]
Lat = inFile.variables['lat'][:,:]
x = inFile.variables['x'][:]
y = inFile.variables['y'][:]
(X,Y) = numpy.meshgrid(x,y)
iceMask = inFile.variables['openOceanMask'][:,:] == 0
groundedMask = numpy.logical_or(inFile.variables['groundedIceMask'][:,:] == 1,
                                inFile.variables['bareBedrockMask'][:,:] == 1)
bed = inFile.variables['bed'][:,:]

bedMask = numpy.logical_and(bed > 0., bed.mask == False)

iceMask = numpy.logical_or(iceMask,bedMask)
groundedMask = numpy.logical_or(groundedMask,bedMask)

# flood fill to remove lakes

masks = {}
masks['AntarcticIceCoverage'] = iceMask
masks['AntarcticGroundedIceCoverage'] = groundedMask
features_file = {}
features_file['features'] = []
for name in masks:

    properties = {}
    properties['name'] = name
    properties['component'] = 'bedmap2'
    properties['author'] = 'https://www.bas.ac.uk/project/bedmap-2/'
    properties['object'] = 'region'
    properties['tags'] = ''
    feature = {}
    feature['properties'] = properties
    feature['geometry'] = extract_geometry(masks[name])
    features_file['features'].append(feature)

out_file_name = "AntarcticIceCoverage.geojson"

write_all_features(features_file, out_file_name, indend=4)
