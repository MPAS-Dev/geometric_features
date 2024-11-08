def qgreenland(gf):
    """
    Aggregate Greenland continental shelf regions similar to ISMIP6
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

    regions = ['April Historical Median Sea Ice Extent',
               'August Historical Median Sea Ice Extent',
               'December Historical Median Sea Ice Extent',
               'February Historical Median Sea Ice Extent',
               'January Historical Median Sea Ice Extent',
               'July Historical Median Sea Ice Extent',
               'June Historical Median Sea Ice Extent',
               'March Historical Median Sea Ice Extent',
               'May Historical Median Sea Ice Extent',
               'November Historical Median Sea Ice Extent',
               'October Historical Median Sea Ice Extent',
               'September Historical Median Sea Ice Extent'
              ]
    fc = gf.read(componentName='seaice', objectType='region',
                 featureNames=regions)

    return fc
