#!/usr/bin/env python

import shapely
import numpy
import xarray
import os
import matplotlib.pyplot as plt
import pyproj
import zipfile
import shutil

from geometric_features import GeometricFeatures, FeatureCollection
from geometric_features.feature_collection import _round_coords

from geometric_features.download import download_files
from geometric_features.utils import write_feature_names_and_tags


def bedmap2_bin_to_netcdf(outFileName):

    if os.path.exists(outFileName):
        return

    fields = ['bed', 'surface', 'thickness', 'coverage', 'rockmask',
              'grounded_bed_uncertainty', 'icemask_grounded_and_shelves']

    allExist = True
    for field in fields:
        fileName = f'bedmap2/bedmap2_bin/bedmap2_{field}.flt'
        if not os.path.exists(fileName):
            allExist = False
            break

    if not allExist:
        # download
        baseURL = 'https://secure.antarctica.ac.uk/data/bedmap2'
        fileNames = ['bedmap2_bin.zip']

        download_files(fileNames, baseURL, 'bedmap2')

        print('Decompressing Bedmap2 data...')
        # unzip
        with zipfile.ZipFile('bedmap2/bedmap2_bin.zip', 'r') as f:
            f.extractall('bedmap2/')
        print('  Done.')

    print('Converting Bedmap2 to NetCDF...')
    ds = xarray.Dataset()
    x = numpy.linspace(-3333000., 3333000., 6667)
    y = x
    ds['x'] = ('x', x)
    ds.x.attrs['units'] = 'meters'
    ds['y'] = ('y', y)
    ds.y.attrs['units'] = 'meters'
    ds.attrs['Grid'] = "Datum = WGS84, earth_radius = 6378137., " \
                       "earth_eccentricity = 0.081819190842621, " \
                       "falseeasting = -3333000., " \
                       "falsenorthing = -3333000., " \
                       "standard_parallel = -71., central_meridien = 0, " \
                       "EPSG=3031"
    ds.attrs['proj'] = "+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0 +k=1 " \
                       "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
    ds.attrs['proj4'] = "+init=epsg:3031"

    # Antarctic stereographic
    inProj = pyproj.Proj(init='epsg:3031')
    # lon/lat
    outProj = pyproj.Proj(init='epsg:4326')
    X, Y = numpy.meshgrid(x, y)
    Lon, Lat = pyproj.transform(inProj, outProj, X, Y)

    ds['lon'] = (('y', 'x'), Lon)
    ds.lon.attrs['units'] = 'degrees east'
    ds['lat'] = (('y', 'x'), Lat)
    ds.lat.attrs['units'] = 'degrees north'

    # add Bedmap2 data
    for fieldName in fields:
        fileName = f'bedmap2/bedmap2_bin/bedmap2_{fieldName}.flt'
        with open(fileName, 'r') as f:
            field = numpy.fromfile(f, dtype=numpy.float32).reshape(6667, 6667)
            # flip the y axis
            field = field[::-1, :]
            # switch invalid values to be NaN (as expected by xarray)
            field[field == -9999.] = numpy.nan
        if fieldName == 'rockmask':
            # rock mask is zero where rock and -9999 (now NaN) elsewhere
            field = numpy.array(numpy.isfinite(field), numpy.float32)
        if fieldName == 'icemask_grounded_and_shelves':
            # split into separate grounded and floating masks
            ds['icemask_grounded'] = \
                (('y', 'x'), numpy.array(field == 0, numpy.float32))
            ds['icemask_shelves'] = \
                (('y', 'x'), numpy.array(field == 1, numpy.float32))
            ds['open_ocean_mask'] = \
                (('y', 'x'), numpy.array(numpy.isnan(field), numpy.float32))
        else:
            ds[fieldName] = (('y', 'x'), field)

    ds.to_netcdf(outFileName)
    print('  Done.')


def get_longest_contour(contourValue, author):

    def stereo_to_lon_lat(x, y):
        return pyproj.transform(inProj, outProj, x, y)

    with xarray.open_dataset('bedmap2.nc') as ds:
        # the bed but not under grounded ice
        bed = xarray.where(ds.icemask_grounded > 0.5, 0., ds.bed).values
        x = ds.x.values
        y = ds.y.values

    # plot contours
    plt.figure()
    cs = plt.contour(x, y, bed, (contourValue,))
    paths = cs.collections[0].get_paths()

    pathLengths = [len(paths[i]) for i in range(len(paths))]
    iLongest = numpy.argmax(pathLengths)

    p = paths[iLongest]
    v = p.vertices
    x = v[:, 0]
    y = v[:, 1]

    # Antarctic stereographic
    inProj = pyproj.Proj(init='epsg:3031')
    # lon/lat
    outProj = pyproj.Proj(init='epsg:4326')

    poly = shapely.geometry.Polygon([(i[0], i[1]) for i in zip(x, y)])

    epsilon = 1e-14
    minY = numpy.amin(y)
    wedge = shapely.geometry.Polygon([(epsilon, minY),
                                      (epsilon**2, -epsilon),
                                      (0, epsilon),
                                      (-epsilon**2, -epsilon),
                                      (-epsilon, minY),
                                      (epsilon, minY)])

    difference = poly.difference(wedge)

    difference = shapely.ops.transform(stereo_to_lon_lat, difference)

    x, y = difference.exterior.xy

    plt.figure()
    plt.plot(x, y)

    fc = FeatureCollection()

    geometry = shapely.geometry.mapping(difference)
    # get rid of the wedge again by rounding the coordinates
    geometry['coordinates'] = _round_coords(geometry['coordinates'])

    fc.add_feature(
        {"type": "Feature",
         "properties": {"name": f"Contour {contourValue}",
                        "author": author,
                        "object": 'region',
                        "component": 'ocean'},
         "geometry": geometry})

    return fc


def make_polygon(lon_vector, lat_vector, name, author, tags):
    fc = FeatureCollection()

    coordinates_list = []
    for idx in range(len(lon_vector)):
        coordinates_pair = [lon_vector[idx], lat_vector[idx]]
        coordinates_list.append(coordinates_pair)
    coordinates_list.append(coordinates_list[0])

    fc.add_feature(
        {"type": "Feature",
         "properties": {"name": name,
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": tags,
                        "zmin": -1000.,
                        "zmax": -400.},
         "geometry": {
             "type": "Polygon",
             "coordinates": [coordinates_list]}})
    return fc


def make_rectangle(lon0, lon1, lat0, lat1, name, author, tags):
    fc = FeatureCollection()

    fc.add_feature(
        {"type": "Feature",
         "properties": {"name": name,
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": tags,
                        "zmin": -1000.,
                        "zmax": -400.},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[lon0, lat0],
                              [lon1, lat0],
                              [lon1, lat1],
                              [lon0, lat1],
                              [lon0, lat0]]]}})
    return fc


def split_feature(fc, fcContour):
    fcDeep = fc.difference(fcContour)

    props = fcDeep.features[0]['properties']
    props['name'] = props['name'] + ' Deep'
    props['tags'] = props['tags'] + ';Deep'
    props['zmin'] = -1000.
    props['zmax'] = -400.

    fcShelf = fc.difference(fcDeep)

    props = fcShelf.features[0]['properties']
    props['name'] = props['name'] + ' Shelf'
    props['tags'] = props['tags'] + ';Shelf'
    props['zmin'] = -1000.
    props['zmax'] = -200.

    fc.merge(fcDeep)
    fc.merge(fcShelf)

    return fc


def split_rectangle(lon0, lon1, lat0, lat1, name, author, tags, fcContour):
    fc = make_rectangle(lon0, lon1, lat0, lat1, name, author, tags)
    split_feature(fc, fcContour)
    return fc


def split_polygon(lon_vector, lat_vector, name, author, tags, fcContour):
    fc = make_polygon(lon_vector, lat_vector, name, author, tags)
    split_feature(fc, fcContour)
    return fc


def main():
    xylar = 'Xylar Asay-Davis'
    carolyn = 'Carolyn Begeman'
    timTags = 'Antarctic;Timmermann'
    orsiTags = 'Antarctic;Orsi'
    antTag = 'Antarctic'

    # make a geometric fieatures object that knows about the geometric data
    # cache up a couple of directories
    gf = GeometricFeatures('../../geometric_data')

    bedmap2_bin_to_netcdf('bedmap2.nc')

    fcContour700 = get_longest_contour(contourValue=-700., author=xylar)
    fcContour800 = get_longest_contour(contourValue=-800., author=xylar)

    fc = FeatureCollection()

    fcEW = split_polygon(
        lon_vector=[-20., -20., 10., 25., 25.],
        lat_vector=[-80., -60., -55., -55., -80.],
        name='Eastern Weddell Sea',
        author=xylar, tags=antTag, fcContour=fcContour800)

    fc.merge(fcEW)

    fcWW = split_polygon(
        lon_vector=[-100., -86., -63., -66., -60., -51., -20., -20.],
        lat_vector=[-81., -75., -73., -67., -64., -60., -60., -85.],
        name='Western Weddell Sea',
        author=carolyn, tags=antTag, fcContour=fcContour800)

    fc.merge(fcWW)

    # The Weddell feature is the sum of the Eastern and Western features before
    # splitting into shelf/deep

    fcWeddell = FeatureCollection()
    fcWeddell.features.append(fcEW.features[0])
    fcWeddell.features.append(fcWW.features[0])

    # now combine these into a single feature
    fcWeddell = fcWeddell.combine('Weddell Sea')
    props = fcWeddell.features[0]['properties']
    props['tags'] = antTag
    props['zmin'] = -1000.
    props['zmax'] = -400.

    split_feature(fcWeddell, fcContour800)

    fc.merge(fcWeddell)

    fc.merge(split_polygon(
        lon_vector=[-100., -86., -63., -66., -100.],
        lat_vector=[-81., -75., -73., -67., -67.],
        name='Bellingshausen Sea',
        author=carolyn, tags=antTag, fcContour=fcContour700))

    fc.merge(split_rectangle(
        lon0=-140., lon1=-100., lat0=-80., lat1=-67., name='Amundsen Sea',
        author=xylar, tags=timTags, fcContour=fcContour800))

    fc.merge(split_rectangle(
        lon0=-180., lon1=-140., lat0=-80., lat1=-67., name='Eastern Ross Sea',
        author=xylar, tags=timTags, fcContour=fcContour700))

    fc.merge(split_rectangle(
        lon0=160., lon1=180., lat0=-80., lat1=-67., name='Western Ross Sea',
        author=xylar, tags=timTags, fcContour=fcContour700))

    fc.merge(split_rectangle(
        lon0=25., lon1=160., lat0=-80., lat1=-62., name='East Antarctic Seas',
        author=xylar, tags=orsiTags, fcContour=fcContour800))

    fc.merge(make_rectangle(
        lon0=-180., lon1=180., lat0=-80., lat1=-60., name='Southern Ocean 60S',
        author=xylar, tags=timTags))

    fcSO = gf.read('ocean', 'region', ['Southern Ocean'])
    props = fcSO.features[0]['properties']
    props['zmin'] = -1000.
    props['zmax'] = -400.

    fc.merge(fcSO)

    fc.plot(projection='southpole')
    fc.to_geojson('antarctic_ocean_regions.geojson')

    # "split" these features into individual files in the geometric data cache
    gf.split(fc)

    # update the database of feature names and tags
    write_feature_names_and_tags(gf.cacheLocation)
    # move the resulting file into place
    shutil.copyfile('features_and_tags.json',
                    '../../geometric_features/features_and_tags.json')

    plt.show()


if __name__ == '__main__':
    main()
