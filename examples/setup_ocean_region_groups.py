#!/usr/bin/env python
"""
This script creates the following ocean region groups:
i) OceanBasinRegionsGroup, which includes the Global Ocean as well as
   Atlantic, Pacific, Indian, Arctic, Southern Ocean, Equatorial
   (global 15S-15N), and Mediterranean basins;
ii) MOCBasinRegionGroup, which includes five regions used for computing the
    meridional overturning circulation (MOC) and meridional heat transport
    (MHT);
iii) NinoRegionGroups, which includes the Nino3, Nino4, and Nino3.4
    regions.
"""

# stuff to make scipts work for python 2 and python 3
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import matplotlib.pyplot as plt
import copy
import shapely

from geometric_features import GeometricFeatures, FeatureCollection


def build_ocean_basins(gf, plot):
    '''
    Builds features defining the major ocean basins

    Parameters
    ----------
    gf : ``GeometricFeatures``
        An object that knows how to download and read geometric featuers

    plot : bool
        Whether to plot each basin

    Returns
    -------
    fc : ``FeatureCollection``
        The new feature collection
    '''
    # Authors
    # -------
    # Xylar Asay-Davis

    fc = FeatureCollection()
    fc.set_group_name(groupName='OceanBasinRegionsGroup')

    # build ocean basins from regions with the appropriate tags
    for oceanName in ['Atlantic', 'Pacific', 'Indian', 'Arctic',
                      'Southern_Ocean', 'Mediterranean']:

        basinName = f'{oceanName}_Basin'
        print(oceanName)

        print(' * merging features')
        fcBasin = gf.read(componentName='ocean', objectType='region',
                          tags=[basinName])

        print(' * combining features')
        fcBasin = fcBasin.combine(featureName=basinName)

        fc.merge(fcBasin)

        if plot:
            fcBasin.plot(projection='cyl')
            plt.title(oceanName)

    # add the global ocean, global ocean between 65S and 65S, and
    # equatorial region
    fc.merge(gf.read(componentName='ocean', objectType='region',
                     featureNames=['Global Ocean',
                                   'Global Ocean 65N to 65S',
                                   'Global Ocean 15S to 15N']))

    return fc


def build_MOC_basins(gf):
    '''
    Builds features defining the ocean basins used in computing the meridional
    overturning circulation (MOC)

    Parameters
    ----------
    gf : ``GeometricFeatures``
        An object that knows how to download and read geometric featuers

    Returns
    -------
    fc : ``FeatureCollection``
        The new feature collection
    '''
    # Authors
    # -------
    # Xylar Asay-Davis

    MOCSubBasins = {'Atlantic': ['Atlantic', 'Mediterranean'],
                    'IndoPacific': ['Pacific', 'Indian'],
                    'Pacific': ['Pacific'],
                    'Indian': ['Indian']}

    MOCSouthernBoundary = {'Atlantic': '34S',
                           'IndoPacific': '34S',
                           'Pacific': '6S',
                           'Indian': '6S'}

    fc = FeatureCollection()
    fc.set_group_name(groupName='MOCBasinRegionsGroup')

    # build MOC basins from regions with the appropriate tags
    for basinName in MOCSubBasins:

        print(f'{basinName} MOC')

        print(' * merging features')
        tags = [f'{basin}_Basin' for basin in MOCSubBasins[basinName]]

        fcBasin = gf.read(componentName='ocean', objectType='region',
                          tags=tags, allTags=False)

        print(' * combining features')
        fcBasin = fcBasin.combine(featureName=f'{basinName}_MOC')

        print(' * masking out features south of MOC region')
        maskName = f'MOC mask {MOCSouthernBoundary[basinName]}'
        fcMask = gf.read(componentName='ocean', objectType='region',
                         featureNames=[maskName])
        # mask out the region covered by the mask
        fcBasin = fcBasin.difference(fcMask)

        # remove various small polygons that are not part of the main MOC
        # basin shapes.  Most are tiny but one below Australia is about 20
        # deg^2, so make the threshold 100 deg^2 to be on the safe side.
        fcBasin = remove_small_polygons(fcBasin, minArea=100.)

        # add this basin to the full feature collection
        fc.merge(fcBasin)

    return fc


def build_Nino_regions(gf):
    '''
    Builds features defining the ocean basins used in computing the El Nino-
    Southern Oscillation climate indices.

    Parameters
    ----------
    gf : ``GeometricFeatures``
        An object that knows how to download and read geometric featuers

    Returns
    -------
    fc : ``FeatureCollection``
        The new feature collection
    '''
    # Authors
    # -------
    # Xylar Asay-Davis

    fc = gf.read(componentName='ocean', objectType='region',
                 tags=['Nino'])
    fc.set_group_name(groupName='NinoRegionsGroup')

    return fc


def remove_small_polygons(fc, minArea):
    '''
    A helper function to remove small polygons from a feature collection

    Parameters
    ----------
    fc : ``FeatureCollection``
        The feature collection to remove polygons from

    minArea : float
        The minimum area (in square degrees) below which polygons should be
        removed

    Returns
    -------
    fcOut : ``FeatureCollection``
        The new feature collection with small polygons removed
    '''
    # Authors
    # -------
    # Xylar Asay-Davis

    fcOut = FeatureCollection()

    removedCount = 0
    for feature in fc.features:
        geom = feature['geometry']
        if geom['type'] not in ['Polygon', 'MultiPolygon']:
            # no area to check, so just add it
            fcOut.add_feature(copy.deepcopy(feature))
        else:
            add = False
            featureShape = shapely.geometry.shape(geom)
            if featureShape.type == 'Polygon':
                if featureShape.area > minArea:
                    add = True
                else:
                    removedCount += 1
            else:
                # a MultiPolygon
                outPolygons = []
                for polygon in featureShape.geoms:
                    if polygon.area > minArea:
                        outPolygons.append(polygon)
                    else:
                        removedCount += 1
                if len(outPolygons) > 0:
                    outShape = shapely.ops.unary_union(outPolygons)
                    feature['geometry'] = shapely.geometry.mapping(outShape)
                    add = True
        if add:
            fcOut.add_feature(copy.deepcopy(feature))
        else:
            print(f"{feature['pproperties']['name']} has been removed.")

    print(f' * Removed {removedCount} small polygons')

    return fcOut


plot = True

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data')

fcOceanBasins = build_ocean_basins(gf, plot)
fcOceanBasins.to_geojson('oceanBasins.geojson')

fcMOC = build_MOC_basins(gf)
fcMOC.to_geojson('MOCBasins.geojson')

fcNino = build_Nino_regions(gf)
fcNino.to_geojson('NinoRegions.geojson')

if plot:
    fcOceanBasins.plot(projection='cyl')
    fcMOC.plot(projection='cyl')
    fcNino.plot(projection='cyl')
    plt.show()
