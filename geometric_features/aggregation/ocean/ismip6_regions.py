def ismip6(gf):
    """
    Aggregate ISMIP6 Antarctic regions similar to Barthel et al. (2020)

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
    # Xylar Asay-Davis

    regions = ['ISMIP6 Amery Sector Shelf', 'ISMIP6 Amundsen Sea Shelf',
               'ISMIP6 Dronning Maud Land Shelf', 'ISMIP6 Ross Sea',
               'ISMIP6 Totten Region Shelf', 'ISMIP6 Weddell Sea Shelf']

    fc = gf.read(componentName='ocean', objectType='region',
                 featureNames=regions)

    return fc
