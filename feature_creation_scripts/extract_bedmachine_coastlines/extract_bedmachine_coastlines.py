#!/usr/bin/env python

import os
import xarray
import numpy
import pyproj
import matplotlib.pyplot as plt
from skimage import measure

from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

from geometric_features import FeatureCollection, GeometricFeatures, \
    read_feature_collection
from geometric_features.utils import write_feature_names_and_tags

import skfmm

from scipy.ndimage.filters import gaussian_filter
from scipy.interpolate import interp1d

"""
We do not have permission to automatically download or re-distribute the
BedMachine Antarctica topography.  To download the file, follow these
instructions:

Download the BedMachine topography
----------------------------------
1. Go to https://nsidc.org/data/nsidc-0756
2. Click on "Other Acces Options"
3. If you don't yet have an account, choose "You may register for an Earthdata Login"
4. Choose "Download Via HTTPS"
5. Under "1970.01.01" choose "BedMachineAntarctica_2019-11-05_v01.nc"

To run this script, create and activate a conda environment as follows:
conda create -y -n bedmachine python=3.7 numpy matplotlib cartopy shapely \
    requests progressbar2 xarray netcdf4 scipy scikit-fmm scikit-image pyproj
conda activate bedmachine
cp feature_creation_scripts/extract_bedmachine_coastlines/extract_bedmachine_coastlines.py .
./extract_bedmachine_coastlines.py

This script takes as input the BedMachine topography data.  It produces the
feature file AntarcticIceCoverage.geojson containing two features:
1) AntarcticIceCoverage contains all grounded or floating ice in Antarctica
as well as all bare bedrock above sea level lying south of 60S
2) AntarcticGroundedIceCoverage contains all grounded ice in Antarctica
as well as all bare bedrock above sea level lying south of 60S

The script also produces images of the signed distance functions (both smoothed
and unsmoothed) used in creating the contours that define these regions as
a sanity check.

The resulting feature file can be split with:
./split_features.py -f AntarcticIceCoverage.geojson
to place the features within the subfolder for the bedmachine component.

"""


def extract_geometry(mask):
    def add_antemeridian(iIn, iOut):
        # this segment crosses the x axis (prime meridian or antemeridian)
        frac = (-x0) / (x1 - x0)
        yMid = (1. - frac) * ys[iIn] + frac * ys[iIn + 1]
        if yMid > 0:
            # segment crosses the prime meridian, so that's fine
            return

        # segment crosses the antemeridian
        # break it into 6 segments, including the south pole
        if x0 < x1:
            newLon = [-180., -180., 0., 180., 180.]
        else:
            newLon = [180., 180., 0., -180., -180.]

        latMid = (1. - frac) * lats[iOut] + frac * lats[iOut + 1]
        newLat = [latMid, -90, -90., -90, latMid]
        for i in range(5):
            lons.insert(iOut + 1, newLon[i])
            lats.insert(iOut + 1, newLat[i])
            iOut += 1

        print(x0, x1, frac)
        print(ys[iIn], ys[iIn + 1], yMid)
        print(lats[iOut - 5:iOut + 2], latMid)
        print(lons[iOut - 5:iOut + 2])
        plt.figure(1)
        plt.plot(xs, ys)
        plt.figure(2)
        plt.plot(lons, lats)
        plt.show()

    floatMask = numpy.zeros(mask.shape)
    floatMask[1:-1, 1:-1] = numpy.array(mask[1:-1, 1:-1], float)
    floatMask = 2. * floatMask - 1.

    distance = skfmm.distance(floatMask)
    print(name, 'distance', numpy.amin(distance), numpy.amax(distance))
    plt.imsave('%s_distance.png' % name, distance, vmin=-1., vmax=1.,
               origin='lower')

    # smooth it a little
    distance = gaussian_filter(distance, sigma=0.5)
    print(name, 'distance smoothed', numpy.amin(distance), numpy.amax(distance))
    plt.imsave('%s_distance_smoothed.png' % name, distance, vmin=-1.,
               vmax=1., origin='lower')

    # extract contours and interpolate following
    # https://stackoverflow.com/a/55420612/7728169
    contours = measure.find_contours(distance, 0.0)

    xInterp = interp1d(numpy.arange(0, len(x)), x)
    yInterp = interp1d(numpy.arange(0, len(y)), y)

    polys = []
    for contour in contours:
        xs = xInterp(contour[:, 1])
        ys = yInterp(contour[:, 0])

        lons, lats = pyproj.transform(projection, lat_lon_projection, xs, ys)
        lons = lons.tolist()
        lats = lats.tolist()

        inIndex = 0
        outIndex = 0
        while inIndex < len(xs) - 1:
            x0 = xs[inIndex]
            x1 = xs[inIndex + 1]
            if (x0 >= 0) != (x1 >= 0):
                add_antemeridian(inIndex, outIndex)

            inIndex += 1
            outIndex += 1

        poly = Polygon([(i[0], i[1]) for i in zip(lons, lats)])
        if poly.is_valid:
            polys.append(poly)
        else:
            print("invalid shape with {} vertices".format(contour.shape[0]))

    return mapping(unary_union(polys))


out_file_name = "AntarcticIceCoverage.geojson"

if os.path.exists(out_file_name):
    fc = read_feature_collection(out_file_name)
else:
    inFileName = 'BedMachineAntarctica_2019-11-05_v01.nc'
    ds = xarray.open_dataset(inFileName)

    # reverse the y direction
    ds = ds.isel(y=slice(None, None, -1))

    projection = pyproj.Proj('+proj=stere +lat_ts=-71.0 +lat_0=-90 +lon_0=0.0 '
                             '+k_0=1.0 +x_0=0.0 +y_0=0.0 +ellps=WGS84')

    lat_lon_projection = pyproj.Proj(proj='latlong', datum='WGS84')

    x = ds.x.values
    y = ds.y.values

    topoTypeMask = ds.mask.values.astype(int)
    iceMask = topoTypeMask != 0
    groundedMask = numpy.logical_or(numpy.logical_or(topoTypeMask == 1,
                                                     topoTypeMask == 2),
                                    topoTypeMask == 4)

    bed = ds.bed.values

    bedMask = numpy.logical_or(bed > 0., numpy.isnan(bed))

    iceMask = numpy.logical_or(iceMask, bedMask)
    groundedMask = numpy.logical_or(groundedMask, bedMask)


    masks = dict()
    masks['AntarcticIceCoverage'] = iceMask
    masks['AntarcticGroundedIceCoverage'] = groundedMask
    fc = FeatureCollection()
    for name in masks:

        properties = dict()
        properties['name'] = name
        properties['component'] = 'bedmachine'
        properties['author'] = \
            'Morlighem et al. (2019) doi:10.1038/s41561-019-0510-8'
        properties['object'] = 'region'
        properties['tags'] = ''
        feature = dict()
        feature['properties'] = properties
        feature['geometry'] = extract_geometry(masks[name])
        fc.add_feature(feature)

    fc.to_geojson(out_file_name)

gf = GeometricFeatures(cacheLocation='./geometric_data')
gf.split(fc)
write_feature_names_and_tags(gf.cacheLocation)

os.rename('features_and_tags.json',
          'geometric_features/features_and_tags.json')
