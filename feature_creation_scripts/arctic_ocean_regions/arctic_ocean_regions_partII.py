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
    z[(x == numpy.amin(x)) | (x == numpy.amax(x)) |
      (y == numpy.amin(y)) | (y == numpy.amax(y))] = 0.0
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
         "properties": {"name": f"Contour {contourValue}",
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
    gf = GeometricFeatures(cacheLocation='../../geometric_data',
                           remoteBranchOrTag='main')

    fc = FeatureCollection()

    # *********** First, fix Atlantic_Basin regions in such a way that ********
    # **********  they do not overlap each other (so that, we can combine
    # *********   them together to form a Atlantic Basin region)

    # ********* New Baltic Sea (modified feature) *********

    # Combine old Baltic Sea feature with other small features
    fcBalticSea = gf.read('ocean', 'region', ['Baltic Sea'])
    fcFinland = gf.read('ocean', 'region', ['Gulf of Finland'])
    fcBothnia = gf.read('ocean', 'region', ['Gulf of Bothnia'])
    fcRiga = gf.read('ocean', 'region', ['Gulf of Riga'])
    fcKattegat = gf.read('ocean', 'region', ['Kattegat'])
    fcSkaggerak = gf.read('ocean', 'region', ['Skaggerak'])
    fcBalticSea.merge(fcFinland)
    fcBalticSea.merge(fcBothnia)
    fcBalticSea.merge(fcRiga)
    fcBalticSea.merge(fcKattegat)
    fcBalticSea.merge(fcSkaggerak)
    fcBalticSea = fcBalticSea.combine('Baltic Sea')
    props = fcBalticSea.features[0]['properties']
    props['tags'] = 'Baltic_Sea;Arctic;Atlantic_Basin'
    props['author'] = author
    fc = fcBalticSea

    # ********* New North Atlantic Ocean (modified feature) *********

    # Fix North Atlantic so that it does not overlap with new Labdrador
    # Sea, Irminger Sea, North Sea, Greenland Sea, and Norwegian Sea
    fcNorthAtlantic = gf.read('ocean', 'region', ['North Atlantic Ocean'])
    fcLabSea = gf.read('ocean', 'region', ['Labrador Sea'])
    fcIrmSea = gf.read('ocean', 'region', ['Irminger Sea'])
    fcGS = gf.read('ocean', 'region', ['Greenland Sea'])
    fcNS = gf.read('ocean', 'region', ['Norwegian Sea'])
    fcNorthSea = gf.read('ocean', 'region', ['North Sea'])
    fc_todiscard = fcLabSea
    fc_todiscard.merge(fcIrmSea)
    fc_todiscard.merge(fcGS)
    fc_todiscard.merge(fcNS)
    fc_todiscard.merge(fcNorthSea)
    fc_todiscard = fc_todiscard.combine('Combined region to discard')
    fcNorthAtlantic.merge(fc_todiscard)
    fcNorthAtlantic = fcNorthAtlantic.combine('North Atlantic Ocean')
    fcNorthAtlantic = fcNorthAtlantic.difference(fc_todiscard)
    props = fcNorthAtlantic.features[0]['properties']
    props['tags'] = 'North_Atlantic_Ocean;Atlantic_Basin'
    props['author'] = author
    fc.merge(fcNorthAtlantic)

    # *********** Second, complete definition of oceanography-relevant *********
    # **********  Arctic regions, started in part I, and identified with
    # *********   tag='Arctic'

    # ********* New Canadian Archipelago (modified feature) *********

    # Modify old CAA by 1) including the shelf in the Arctic Ocean, and
    # 2) including Nares Strait. Old CAA feature will be superseded by this.
    fcContour500 = get_longest_contour(contourValue=-500., author=author)
    fcContour1000 = get_longest_contour(contourValue=-1000., author=author)
    fcCAA1 = make_rectangle(lon0=-130., lon1=-90., lat0=67.0, lat1=86.0,
                            name='West Canadian Archipelago', author=author,
                            tags='Canadian_Archipelago;Arctic;Atlantic_Basin')
    fcCAA1 = fcCAA1.difference(fcContour500)
    fcCAA2 = make_rectangle(lon0=-90., lon1=-70., lat0=67.0, lat1=86.0,
                            name='Mid Canadian Archipelago', author=author,
                            tags='Canadian_Archipelago;Arctic;Atlantic_Basin')
    fcCAA2 = fcCAA2.difference(fcContour1000)
    fcCAA3 = make_rectangle(lon0=-70., lon1=-50.5, lat0=76.0, lat1=86.0,
                            name='East Canadian Archipelago', author=author,
                            tags='Canadian_Archipelago;Arctic;Atlantic_Basin')
    fcCAA3 = fcCAA3.difference(fcContour500)
    fcCAA = fcCAA1
    fcCAA.merge(fcCAA2)
    fcCAA.merge(fcCAA3)
    fcCAA = fcCAA.combine('Canadian Archipelago')
    fcHudson = gf.read('ocean', 'region', ['Hudson Bay'])
    fcCAA = fcCAA.difference(fcHudson)
    fcBaffin = gf.read('ocean', 'region', ['Baffin Bay'])
    fcCAA = fcCAA.difference(fcBaffin)
    props = fcCAA.features[0]['properties']
    props['tags'] = 'Canadian_Archipelago;Arctic;Atlantic_Basin'
    props['author'] = author
    fc.merge(fcCAA)

    # ********* Canada Basin (new feature) *********

    # This is a slightly modified version of the Beaufort Gyre feature
    # defined in part I. Differences include 1) a region that expands to
    # the west to touch the northern boundary of the new CAA feature, and
    # 2) a region that includes the Canada Basin shelf (whereas, for the
    # Beuafort Gyre, we have separated the 'Gyre' from the 'Gyre Shelf').
    fcContour300 = get_longest_contour(contourValue=-300., author=author)
    fcCB1 = make_rectangle(lon0=-170., lon1=-156.65, lat0=67.0, lat1=80.0,
                           name='West Canada Basin', author=author,
                           tags='Canada_Basin;Arctic;Arctic_Basin')
    fcCB = fcCB1.difference(fcContour300)
    fcCB = fcCB1.difference(fcCB)
    fcCB2 = make_rectangle(lon0=-156.65, lon1=-100.0, lat0=67.0, lat1=80.0,
                           name='East Canada Basin', author=author,
                           tags='Canada_Basin;Arctic;Arctic_Basin')
    fcCB2 = fcCB2.difference(fcCAA)
    fcCB.merge(fcCB2)
    fcCB = fcCB.combine('Canada Basin')
    props = fcCB.features[0]['properties']
    props['tags'] = 'Canada_Basin;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcCB)

    # ********* Chukchi Sea (new feature) *********

    # This supersedes the old Chukchi Sea feature
    fcChukchi = make_rectangle(lon0=-180., lon1=-156.65, lat0=65.0, lat1=80.0,
                               name='Chukchi Sea', author=author,
                               tags='Chukchi_Sea;Arctic;Arctic_Basin')
    fcChukchi = fcChukchi.difference(fcContour300)
    fcChukchi_NSIDC = gf.read('ocean', 'region', ['Chukchi Sea NSIDC'])
    fcChukchi_todiscard = fcChukchi.difference(fcChukchi_NSIDC)
    fcChukchi = fcChukchi.difference(fcChukchi_todiscard)
    props = fcChukchi.features[0]['properties']
    props['tags'] = 'Chukchi_Sea;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcChukchi)

    # ********* East Siberian Sea (new feature) *********

    # This supersedes the old East Siberian Sea feature
    fcESS = make_rectangle(lon0=142., lon1=180.0, lat0=68.5, lat1=80.0,
                           name='East Siberian Sea', author=author,
                           tags='East_Siberian_Sea;Arctic;Arctic_Basin')
    fcESS = fcESS.difference(fcContour300)
    props = fcESS.features[0]['properties']
    props['tags'] = 'East_Siberian_Sea;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcESS)

    # ********* Laptev Sea (new feature) *********

    # This supersedes the old Laptev Sea feature
    fcLap = make_rectangle(lon0=90., lon1=142.0, lat0=70.0, lat1=81.25,
                           name='Laptev Sea', author=author,
                           tags='Laptev_Sea;Arctic;Arctic_Basin')
    fcLap = fcLap.difference(fcContour300)
    fcKara = gf.read('ocean', 'region', ['Kara Sea'])
    fcLap = fcLap.difference(fcKara)
    props = fcLap.features[0]['properties']
    props['tags'] = 'Laptev_Sea;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcLap)

    # ********* Central Arctic (new feature) *********

    # Define Central Arctic region as Arctic Ocean minus Canadian
    # Archipelago, Canada Basin, Chukchi Sea, ESS, and Laptev Sea
    fcArctic = gf.read('ocean', 'region', ['Arctic Ocean'])
    fcCentralArctic = fcArctic.difference(fcCAA)
    fcCentralArctic = fcCentralArctic.difference(fcCB)
    fcCentralArctic = fcCentralArctic.difference(fcChukchi)
    fcCentralArctic = fcCentralArctic.difference(fcESS)
    fcCentralArctic = fcCentralArctic.difference(fcLap)
    props = fcCentralArctic.features[0]['properties']
    props['name'] = 'Central Arctic'
    props['tags'] = 'Central_Arctic;Arctic;Arctic_Basin'
    props['author'] = author
    fc.merge(fcCentralArctic)

    # *********** Third, complete definition of seaice-relevant ***********
    # ***** Arctic regions, started in part I, according to NSIDC
    # ***** (regions map: https://nsidc.org/data/masie/browse_regions)
    # ****  and identified with tag='Arctic_NSIDC'

    # ********* New Chukchi Sea NSIDC (modified feature) *********

    # This supersedes the Chukchi Sea NSIDC feature defined in part I
    fcChukchi_NSIDC = FeatureCollection()
    fcChukchi_NSIDC.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Chukchi Sea NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Chukchi_Sea_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[-156.65, 65.37],
                              [-180.0,  66.0],
                              [-180.0,  80.0],
                              [-156.48, 80.0],
                              [-156.65, 65.37]]]}})
    fc.merge(fcChukchi_NSIDC)

    # ********* Beaufort Sea NSIDC (new feature) *********

    fcBS_NSIDC = FeatureCollection()
    fcBS_NSIDC.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Beaufort Sea NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Beaufort_Sea_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[-156.65, 65.37],
                              [-156.48, 80.0],
                              [-112.34, 77.69],
                              [-124.58, 75.67],
                              [-124.0,  65.0],
                              [-156.65, 65.37]]]}})
    fc.merge(fcBS_NSIDC)

    # ********* Canadian Archipelago NSIDC (new feature) *********

    fcCAA_NSIDC = FeatureCollection()
    fcCAA_NSIDC.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Canadian Archipelago NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Canadian_Archipelago_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[-103.41, 60.69],
                              [-124.0,  65.0],
                              [-124.58, 75.67],
                              [-112.34, 77.69],
                              [-69.33,  82.67],
                              [-81.21,  71.79],
                              [-83.94,  70.43],
                              [-84.45,  67.27],
                              [-93.04,  65.70],
                              [-103.41, 60.69]]]}})
    fc.merge(fcCAA_NSIDC)

    # ********* Hudson Bay NSIDC (new feature) *********

    fcHudson_NSIDC = FeatureCollection()
    fcHudson_NSIDC.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Hudson Bay NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Hudson_Bay_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[-81.24,  49.19],
                              [-103.41, 60.69],
                              [-93.04,  65.70],
                              [-84.45,  67.27],
                              [-83.94,  70.43],
                              [-81.21,  71.79],
                              [-70.70,  66.95],
                              [-70.12,  65.99],
                              [-63.70,  57.35],
                              [-81.24,  49.19]]]}})
    fc.merge(fcHudson_NSIDC)

    # ********* Baffin Bay NSIDC (new feature) *********

    fcBaffin_NSIDC = FeatureCollection()
    fcBaffin_NSIDC.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Baffin Bay NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Baffin_Bay_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[-53.20,  42.0],
                              [-68.07,  38.38],
                              [-76.82,  48.01],
                              [-60.85,  54.33],
                              [-63.70,  57.35],
                              [-70.12,  65.99],
                              [-70.70,  66.95],
                              [-81.21,  71.79],
                              [-69.33,  82.67],
                              [-45.0,   60.0],
                              [-45.0,   42.0],
                              [-53.20,  42.0]]]}})
    fc.merge(fcBaffin_NSIDC)

    # ********* Central Arctic NSIDC (new feature) *********

    fcCentralArctic_NSIDC = FeatureCollection()
    fcCentralArctic_NSIDC.add_feature(
        {"type": "Feature",
         "properties": {"name": 'Central Arctic NSIDC',
                        "author": author,
                        "object": 'region',
                        "component": 'ocean',
                        "tags": 'Central_Arctic_NSIDC;Arctic_NSIDC'},
         "geometry": {
             "type": "Polygon",
             "coordinates": [[[180.0, 80.0],
                              [180.0, 90.0],
                              [-69.33,  90.0],
                              [-180.0,  90.0],
                              [-180.0,  80.0],
                              [-156.48, 80.0],
                              [-112.34, 77.69],
                              [-69.33,  82.67],
                              [-51.66,  74.25],
                              [-12.72,  81.41],
                              [18.99,   79.18],
                              [58.68,   81.08],
                              [94.95,   81.08],
                              [145.0, 80.0],
                              [180.0, 80.0]]]}})
    fc.merge(fcCentralArctic_NSIDC)

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
        print(f'{featureName} is_valid: {shape.is_valid}')
        if not shape.is_valid:
            fixed = shape.buffer(0)
            print(f'  Fixed? {fixed.is_valid}')
            feature['geometry'] = shapely.geometry.mapping(fixed)
    fcArcticTags.plot(projection='northpole')
    fcArcticTags.to_geojson('arctic_ocean_regions.geojson')

    fcArcticNSIDCTags = gf.read(componentName='ocean', objectType='region',
                                tags=['Arctic_NSIDC'])
    for feature in fcArcticNSIDCTags.features:
        featureName = feature['properties']['name']
        shape = shapely.geometry.shape(feature['geometry'])
        print(f'{featureName} is_valid: {shape.is_valid}')
        if not shape.is_valid:
            fixed = shape.buffer(0)
            print(f'  Fixed? {fixed.is_valid}')
            feature['geometry'] = shapely.geometry.mapping(fixed)
    fcArcticNSIDCTags.plot(projection='northpole')
    fcArcticNSIDCTags.to_geojson('arcticNSIDC_ocean_regions.geojson')

    fcArctic = fcArcticTags
    fcArctic.merge(fcArcticNSIDCTags)

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
