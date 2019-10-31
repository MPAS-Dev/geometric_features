#!/usr/bin/env python

import shapely
import numpy
import xarray
import os
import matplotlib.pyplot as plt
import pyproj
import gzip
import shutil
import tempfile

from geometric_features import GeometricFeatures, FeatureCollection
from geometric_features.feature_collection import _round_coords

from geometric_features.download import download_files
from geometric_features.utils import write_feature_names_and_tags


def get_longest_contour(contourValue, author):

    def stereo_to_lon_lat(x, y):
        return pyproj.transform(inProj, outProj, x, y)

    bathymetryFileName = 'IBCAO_V3_500m_SM.grd.gz'
    if not os.path.exists(bathymetryFileName):
        print('Downloading IBCAO bathymetry data...')
        # download
        baseURL = 'https://www.ngdc.noaa.gov/mgg/bathymetry/arctic/grids/version3_0'

        download_files([bathymetryFileName], baseURL, './')

    print('Decompressing and reading IBCAO bathymetry data...')
    infile = gzip.open(bathymetryFileName, 'rb')
    tmp = tempfile.NamedTemporaryFile(delete=False)
    shutil.copyfileobj(infile, tmp)
    infile.close()
    tmp.close()
    ds = xarray.open_dataset(tmp.name)
    os.unlink(tmp.name)

    x = ds.x.values
    y = ds.y.values
    z = ds.z.values
    z[(x==numpy.amin(x)) | (x==numpy.amax(x)) |
      (y==numpy.amin(y)) | (y==numpy.amax(y))] = 0.0
    # plot contours
    plt.figure()
    cs = plt.contour(x, y, z, (contourValue,))
    paths = cs.collections[0].get_paths()

    pathLengths = [len(paths[i]) for i in range(len(paths))]
    iLongest = numpy.argmax(pathLengths)

    p = paths[iLongest]
    v = p.vertices
    x = v[:, 0]
    y = v[:, 1]

    # Arctic stereographic
    inProj = pyproj.Proj(init='epsg:3995')
    # lon/lat
    outProj = pyproj.Proj(init='epsg:4326')
    lon, lat = pyproj.transform(inProj, outProj, x, y)

    poly = shapely.geometry.Polygon([(i[0], i[1]) for i in zip(x, y)])
    ##
    #x, y = poly.exterior.xy
    #plt.figure()
    #plt.plot(x, y)
    #plt.show()
    ##

    epsilon = 1e-14
    maxY = numpy.amax(y)
    wedge = shapely.geometry.Polygon([(epsilon, maxY),
                                      (epsilon**2, epsilon),
                                      (0, epsilon),
                                      (-epsilon**2, epsilon),
                                      (-epsilon, maxY),
                                      (epsilon, maxY)])

    difference = poly.difference(wedge)

    difference = shapely.ops.transform(stereo_to_lon_lat, difference)

    fc = FeatureCollection()

    geometry = shapely.geometry.mapping(difference)
    # get rid of the wedge again by rounding the coordinates
    geometry['coordinates'] = _round_coords(geometry['coordinates'])

    fc.add_feature(
        {"type": "Feature",
         "properties": {"name": "Contour {}".format(contourValue),
                        "author": author,
                        "object": 'region',
                        "component": 'ocean'},
         "geometry": geometry})

    return fc


def make_rectangle(lon0, lon1, lat0, lat1, name, author, tags):
    fc = FeatureCollection()

    fc.add_feature(
        {"type": "Feature",
         "properties": {"name": name,
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": tags},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[lon0, lat0],
                              [lon1, lat0],
                              [lon1, lat1],
                              [lon0, lat1],
                              [lon0, lat0]]]}})
    return fc


def main():
    author = 'Milena Veneziani'
    arcticTags = 'Arctic_Ocean;Arctic;Arctic_Basin'
    proshTags = 'Arctic;Proshutinsky'

    # make a geometric features object that knows about the geometric data
    # cache up a couple of directories
    gf = GeometricFeatures('../../geometric_data')

    fc = FeatureCollection()

    # Combine old Barentsz_Sea and White_Sea into new Barents Sea 
    # feature (Barentsz_Sea and White_Sea features will be removed)
    fcBS = gf.read('ocean', 'region', ['Barentsz Sea'])
    fcBS.merge(gf.read('ocean', 'region', ['White Sea']))
    fcBS = fcBS.combine('Barents Sea')
    fcBS.to_geojson('BarentsSea.geojson')
    fc = fcBS
    props = fc.features[0]['properties']
    props['tags'] = 'Barents_Sea;Arctic;Arctic_Basin'

    # Include Kara Sea
    fcKara = gf.read('ocean', 'region', ['Kara Sea'])
    fc.merge(fcKara)

    # Define triangle between Greenland Sea and Arctic_Ocean
    # (north of Fram Strait) that is not part of any of the
    # currently defined Arctic features
    fc_tmp = gf.read('ocean', 'region', ['Arctic Ocean'])
    fc_tmp.merge(gf.read('ocean', 'region', ['Lincoln Sea']))
    fc_tmp.merge(fcBS)
    fcArctic = make_rectangle(lon0=-36., lon1=20., lat0=86., lat1=79.,
        name='North of Fram Strait', author=author, tags=arcticTags)
    fcArctic = fcArctic.difference(fc_tmp)

    # Define full Arctic *but* Barents and Kara Seas
    fcArctic.merge(gf.read('ocean', 'region', ['Arctic Ocean']))
    fcArctic.merge(gf.read('ocean', 'region', ['Laptev Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['East Siberian Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['Chukchi Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['Beaufort Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['Lincoln Sea']))
    fcArctic = fcArctic.combine('Arctic Ocean')
    fcArctic.to_geojson('ArcticOcean.geojson')
    #fc.merge(fcArctic)

    # Define Beaufort Gyre region
    fcContour300 = get_longest_contour(contourValue=-300., author=author)
    fcBG_firstTry = make_rectangle(lon0=-170., lon1=-130., lat0=70.5, lat1=80.5,
        name='Beaufort Gyre', author=author, tags='Beaufort_Gyre;Arctic;Arctic_Basin')
    fcBG = fcBG_firstTry.difference(fcContour300)
    fcBG = fcBG_firstTry.difference(fcBG)
    fcBG.to_geojson('BeaufortGyre.geojson')
    fc.merge(fcBG)

    # Define Chukchi Sea (MASIE region #2)
    fcChukchi = make_rectangle(lon0=-156.65, lon1=-180., lat0=65.37, lat1=80.,
        name='Chukchi Sea', author=author, tags='Chukchi_Sea;Arctic;Arctic_Basin')
    fcChukchi.to_geojson('ChukchiSea.geojson')
    fc.merge(fcChukchi)

    # "split" these features into individual files in the geometric data cache
    #gf.split(fc)

    # update the database of feature names and tags
    #write_feature_names_and_tags(gf.cacheLocation)
    # move the resulting file into place
    #shutil.copyfile('features_and_tags.json',
    #                '../../geometric_features/features_and_tags.json')


if __name__ == '__main__':
    main()
