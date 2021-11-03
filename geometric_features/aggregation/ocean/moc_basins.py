import shapely.geometry
import shapely.ops
import copy

from geometric_features import FeatureCollection


def moc(gf):
    """
    Aggregate features defining the ocean basins used in computing the
    meridional overturning circulation (MOC)

    Parameters
    ----------
    gf : ``GeometricFeatures``
        An object that knows how to download and read geometric featuers

    Returns
    -------
    fc : ``FeatureCollection``
        The new feature collection
    """
    # Authors
    # -------
    # Xylar Asay-Davis

    MOCSubBasins = {'Atlantic': ['Atlantic'],
                    'AtlanticMed': ['Atlantic', 'Mediterranean'],
                    'IndoPacific': ['Pacific', 'Indian'],
                    'Pacific': ['Pacific'],
                    'Indian': ['Indian']}

    MOCSouthernBoundary = {'Atlantic': '34S',
                           'AtlanticMed': '34S',
                           'IndoPacific': '34S',
                           'Pacific': '6S',
                           'Indian': '6S'}

    fc = FeatureCollection()
    fc.set_group_name(groupName='MOCBasinRegionsGroup')

    # build MOC basins from regions with the appropriate tags
    for basinName in MOCSubBasins:
        tags = ['{}_Basin'.format(basin) for basin in
                MOCSubBasins[basinName]]

        fcBasin = gf.read(componentName='ocean', objectType='region',
                          tags=tags, allTags=False)

        fcBasin = fcBasin.combine(featureName='{}_MOC'.format(basinName))

        maskName = 'MOC mask {}'.format(MOCSouthernBoundary[basinName])
        fcMask = gf.read(componentName='ocean', objectType='region',
                         featureNames=[maskName])
        # mask out the region covered by the mask
        fcBasin = fcBasin.difference(fcMask)

        # remove various small polygons that are not part of the main MOC
        # basin shapes.  Most are tiny but one below Australia is about 20
        # deg^2, so make the threshold 100 deg^2 to be on the safe side.
        fcBasin = _remove_small_polygons(fcBasin, minArea=100.)

        # add this basin to the full feature collection
        fc.merge(fcBasin)

    return fc


def _remove_small_polygons(fc, minArea):
    """
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
    """
    # Authors
    # -------
    # Xylar Asay-Davis

    fcOut = FeatureCollection()

    removedCount = 0
    for feature in fc.features:
        geom = feature['geometry']
        add = False
        if geom['type'] not in ['Polygon', 'MultiPolygon']:
            # no area to check, so just add it
            fcOut.add_feature(copy.deepcopy(feature))
        else:
            featureShape = shapely.geometry.shape(geom)
            if featureShape.type == 'Polygon':
                if featureShape.area > minArea:
                    add = True
                else:
                    removedCount += 1
            else:
                # a MultiPolygon
                outPolygons = []
                for polygon in featureShape:
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

    return fcOut
