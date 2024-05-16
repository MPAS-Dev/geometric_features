def greenland(gf):
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
    # Carolyn Begeman

    regions = ['ISMIP6 Greenland Central East Shelf',
               'ISMIP6 Greenland Central West Shelf',
               'ISMIP6 Greenland North East Shelf',
               'ISMIP6 Greenland North Shelf',
               'ISMIP6 Greenland North West Shelf',
               'ISMIP6 Greenland South East Shelf',
               'ISMIP6 Greenland South West Shelf']

    fc = gf.read(componentName='ocean', objectType='region',
                 featureNames=regions)

    return fc
