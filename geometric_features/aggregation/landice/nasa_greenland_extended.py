def nasa_greenland(gf):
    """
    Aggregate NASA Greenland ice basin region extended to continental shelf.

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features

    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with antarctic regions
    """
    # Authors
    # -------
    # Alex Hager

    regions = ['eastCentralGreenland1_oceanExtended',
               'eastCentralGreenland2_oceanExtended',
               'eastCentralGreenland3_oceanExtended',
               'northEastGreenland1_oceanExtended',
               'northEastGreenland2_oceanExtended',
               'northGreenland1_oceanExtended',
               'northGreenland2_oceanExtended',
               'northGreenland3_oceanExtended',
               'northWestGreenland1_oceanExtended',
               'northWestGreenland2_oceanExtended',
               'southEastGreenland1_oceanExtended',
               'southEastGreenland2_oceanExtended',
               'southEastGreenland3_oceanExtended',
               'southGreenland1_oceanExtended',
               'southWestGreenland1_oceanExtended',
               'southWestGreenland2_oceanExtended',
               'westCentralGreenland1_oceanExtended',
               'westCentralGreenland2_oceanExtended']

    fc = gf.read(componentName='landice', objectType='region',
                 featureNames=regions)

    return fc
