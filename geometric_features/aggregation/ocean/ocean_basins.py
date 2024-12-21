from geometric_features import FeatureCollection


def basins(gf):
    """
    Aggregate Global Ocean as well as Atlantic, Pacific, Indian, Arctic,
    Southern Ocean, Equatorial (global 15S-15N), and Mediterranean basins

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features

    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with ocean basins
    """
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

    # add the global ocean, global ocean between 65S and 65S, and
    # equatorial region
    fc.merge(gf.read(componentName='ocean', objectType='region',
                     featureNames=['Global Ocean',
                                   'Global Ocean 65N to 65S',
                                   'Global Ocean 15S to 15N',
                                   'Southern Hemisphere']))

    return fc
