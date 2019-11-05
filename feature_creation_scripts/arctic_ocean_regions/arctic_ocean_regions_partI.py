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

    # make a geometric features object that knows about the geometric data
    # cache up a couple of directories
    gf = GeometricFeatures(cacheLocation='../../geometric_data')

    fc = FeatureCollection()

    # ********* New Hudson Bay (modified feature) *********

    # Extract Foxe Basin from Northwestern Passages, and merge it
    # to old Hudson Bay feature. Also combine Hudson Strait with
    # Hudson Bay. Note that the created feature needs to be further
    # edited by hand to eliminate a seem, due to Foxe Basin not
    # completely aligning with one side of the old Hudson Bay feature
    # (and this feature is not fixed by the last step in this script
    # either).
    fcCAA = gf.read('ocean', 'region', ['Northwestern Passages'])
    fcbox1 = make_rectangle(lon0=-84.3, lon1=-71.7, lat0=67.1, lat1=70.75,
                            name='Foxe Basin Box 1', author=author,
                            tags='Hudson_Bay;Arctic;Atlantic_Basin')
    fcbox2 = make_rectangle(lon0=-86., lon1=-71.7, lat0=63.5, lat1=67.1,
                            name='Foxe Basin Box 2', author=author,
                            tags='Hudson_Bay;Arctic;Atlantic_Basin')
    fcFoxe_tmp = fcbox1.difference(fcCAA)
    fcFoxe_tmp = fcbox1.difference(fcFoxe_tmp)
    fcFoxe = fcbox2.difference(fcCAA)
    fcFoxe = fcbox2.difference(fcFoxe)
    fcFoxe.merge(fcFoxe_tmp)
    fcFoxe = fcFoxe.combine('Foxe Basin')
    fcHudson = gf.read('ocean', 'region', ['Hudson Bay'])
    fcHudson.merge(gf.read('ocean', 'region', ['Hudson Strait']))
    fcHudson.merge(fcFoxe)
    fcHudson = fcHudson.combine('Hudson Bay')
    props = fcHudson.features[0]['properties']
    props['tags'] = 'Hudson Bay;Arctic;Atlantic_Basin'
    props['author'] = author
    fc = fcHudson

    # ********* New Canadian Archipelago (modified feature) *********

    # Remove Foxe Basin from Northwestern Passages and make new
    # Canadian Archipelago feature
    fcCAA = fcCAA.difference(fcFoxe)
    props = fcCAA.features[0]['properties']
    props['name'] = 'Canadian Archipelago'
    props['tags'] = 'Canadian_Archipelago;Arctic;Atlantic_Basin'
    props['author'] = author
    fc.merge(fcCAA)

    # ********* New Barents Sea (modified feature) *********
    # NOTE: this is dependent on existence of *old* features;
    #       in particular, the Barentsz_Sea feature will
    #       be removed after this script is applied

    # Combine Barentsz_Sea and White_Sea into new Barents Sea feature
    fcBS = gf.read('ocean', 'region', ['Barentsz Sea'])
    fcBS.merge(gf.read('ocean', 'region', ['White Sea']))
    fcBS = fcBS.combine('Barents Sea')
    props = fcBS.features[0]['properties']
    props['tags'] = 'Barents_Sea;Arctic;Arctic_NSIDC;Arctic_Basin'
    props['author'] = author
    fc.merge(fcBS)

    # ********* Kara Sea (unchanged feature) *********

    fcKara = gf.read('ocean', 'region', ['Kara Sea'])
    props = fcKara.features[0]['properties']
    props['tags'] = 'Kara_Sea;Arctic;Arctic_NSIDC;Arctic_Basin'
    fc.merge(fcKara)

    # ********* New Arctic Ocean (modified feature) *********
    # NOTE: this is dependent on existence of *old* features;
    #       in particular, the Arctic_Ocean, Chukchi_Sea,
    #       East_Siberian_Sea, and Laptev_Sea features will
    #       be superseded after this script is applied

    # Define triangle between Greenland Sea and Arctic_Ocean
    # (north of Fram Strait) that is not part of any of the
    # currently defined Arctic features
    fc_tmp = gf.read('ocean', 'region', ['Arctic Ocean'])
    fc_tmp.merge(gf.read('ocean', 'region', ['Lincoln Sea']))
    fc_tmp.merge(fcBS)
    fcArctic = make_rectangle(lon0=-36., lon1=20., lat0=86., lat1=79.,
        name='North of Fram Strait', author=author, tags='Arctic_Basin')
    fcArctic = fcArctic.difference(fc_tmp)

    # Define full Arctic *but* Barents and Kara Seas
    fcArctic.merge(gf.read('ocean', 'region', ['Arctic Ocean']))
    fcArctic.merge(gf.read('ocean', 'region', ['Laptev Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['East Siberian Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['Chukchi Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['Beaufort Sea']))
    fcArctic.merge(gf.read('ocean', 'region', ['Lincoln Sea']))
    fcArctic = fcArctic.combine('Arctic Ocean')
    props = fcArctic.features[0]['properties']
    props['tags'] = 'Arctic_Ocean;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcArctic)

    # ********* Beaufort Gyre (entirely new feature) *********

    fcContour300 = get_longest_contour(contourValue=-300., author=author)
    fcBG_firstTry = make_rectangle(lon0=-170., lon1=-130., lat0=70.5, lat1=80.5,
                                   name='Beaufort Gyre', author=author,
                                   tags='Beaufort_Gyre;Arctic_Proshutinsky')
    fcBG = fcBG_firstTry.difference(fcContour300)
    fcBG = fcBG_firstTry.difference(fcBG)
    fc.merge(fcBG)

    # ********* New NSIDC Chukchi Sea (new feature) *********

    # Define Chukchi Sea as MASIE region #2 minus intersection with
    # Beaufort Gyre, and with Bering Strait transect as southern boundary
    fcChukchi = FeatureCollection()
    fcChukchi.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Chukchi Sea NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Chukchi_Sea_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[-167.15, 65.74],
                              [-168.01, 65.84],
                              [-168.62, 65.91],
                              [-169.43, 66.01],
                              [-170.24, 66.1],
                              [-180., 66.6],
                              [-180., 80.0],
                              [-156.48, 80.0],
                              [-156.65, 65.37],
                              [-167.15, 65.74]]]}})
    fcChukchi = fcChukchi.difference(fcBG)
    fc.merge(fcChukchi)

    # ********* Beaufort Gyre shelf (entirely new feature) *********

    # Define Beaufort Gyre shelf region, minus intersection with Chukchi Sea
    fcBGshelf_firstTry = make_rectangle(lon0=-170., lon1=-130.,
                                        lat0=68.0, lat1=80.5,
                                        name='Beaufort Gyre Shelf Box',
                                        author=author,
                                        tags='Beaufort_Gyre_Shelf;Arctic_Proshutinsky')
    fcBGshelf = fcBGshelf_firstTry.difference(fcContour300)
    fcBGshelf_secondTry = fcBGshelf_firstTry.difference(fcBG)
    fcBGshelf_secondTry = fcBGshelf_secondTry.difference(fcBGshelf)
    fcBGshelf.merge(fcBGshelf_secondTry)
    fcBGshelf = fcBGshelf.combine('Beaufort Gyre Shelf')
    fcBGshelf = fcBGshelf.difference(fcChukchi)
    props = fcBGshelf.features[0]['properties']
    props['name'] = 'Beaufort Gyre Shelf'
    props['author'] = author
    props['tags'] = 'Beaufort_Gyre_Shelf;Arctic_Proshutinsky'
    fc.merge(fcBGshelf)

    # ********* New NSIDC East Siberian Sea (new feature) *********

    # Define East Siberian Sea as MASIE region #3
    fcESS = FeatureCollection()
    fcESS = make_rectangle(lon0=180., lon1=145., lat0=67., lat1=80.,
                           name='East Siberian Sea NSIDC', author=author,
                           tags='East_Siberian_Sea_NSIDC;Arctic_NSIDC')
    fc.merge(fcESS)

    # ********* New NSIDC Laptev Sea (new feature) *********

    # Define Laptev Sea as MASIE region #4, minus intersection with
    # Kara Sea
    fcLap = FeatureCollection()
    fcLap.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Laptev Sea NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Laptev_Sea_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[145.,  68.],
                              [145.,  80.],
                              [95.4, 81.29],
                              [99.89, 78.27],
                              [102.,  72.],
                              [145.,  68.]]]}})
    fcLap = fcLap.difference(fcKara)
    fc.merge(fcLap)

    # ********* Central Arctic (entirely new feature) *********

    # Define Central Arctic region as New Arctic Ocean minus BG, BGshelf,
    # New Chukchi, New ESS, and New Laptev
    fcCentralArctic = fcArctic.difference(fcBG)
    fcCentralArctic = fcCentralArctic.difference(fcBGshelf)
    fcCentralArctic = fcCentralArctic.difference(fcChukchi)
    fcCentralArctic = fcCentralArctic.difference(fcESS)
    fcCentralArctic = fcCentralArctic.difference(fcLap)
    props = fcCentralArctic.features[0]['properties']
    props['name'] = 'Central Arctic'
    props['tags'] = 'Central_Arctic;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcCentralArctic)

    # "split" these features into individual files in the geometric data cache
    gf.split(fc)

    # update the database of feature names and tags
    write_feature_names_and_tags(gf.cacheLocation)
    # move the resulting file into place
    shutil.copyfile('features_and_tags.json',
                    '../../geometric_features/features_and_tags.json')

    # Fix features if necessary
    fcArcticTags = gf.read(componentName='ocean', objectType='region',
                           tags=['Arctic'])
    for feature in fcArcticTags.features:
        featureName = feature['properties']['name']
        shape = shapely.geometry.shape(feature['geometry'])
        print('{} is_valid: {}'.format(featureName, shape.is_valid))
        if not shape.is_valid:
            fixed = shape.buffer(0)
            print('  Fixed? {}'.format(fixed.is_valid))
            feature['geometry'] = shapely.geometry.mapping(fixed)
    fcArcticNSIDCTags = gf.read(componentName='ocean', objectType='region',
                                tags=['Arctic_NSIDC'])
    for feature in fcArcticNSIDCTags.features:
        featureName = feature['properties']['name']
        shape = shapely.geometry.shape(feature['geometry'])
        print('{} is_valid: {}'.format(featureName, shape.is_valid))
        if not shape.is_valid:
            fixed = shape.buffer(0)
            print('  Fixed? {}'.format(fixed.is_valid))
            feature['geometry'] = shapely.geometry.mapping(fixed)

    fcArctic = fcArcticTags
    fcArctic.merge(fcArcticNSIDCTags)
    fcArctic.to_geojson('arctic_ocean_regions.geojson')
    fcArctic.plot(projection='northpole')

    # "split" these features into individual files in the geometric data cache
    gf.split(fcArctic)

    # update the database of feature names and tags
    write_feature_names_and_tags(gf.cacheLocation)
    # move the resulting file into place
    shutil.copyfile('features_and_tags.json',
                    '../../geometric_features/features_and_tags.json')

    plt.show()

if __name__ == '__main__':
    main()
