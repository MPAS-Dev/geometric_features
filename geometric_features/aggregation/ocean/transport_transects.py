def transport(gf):
    """
    Aggregate standard transport transects

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features

    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with transport transects
    """
    # Authors
    # -------
    # Xylar Asay-Davis

    # create a FeatureCollection to which we will add all regions
    fc = gf.read(componentName='ocean', objectType='transect',
                 tags=['standard_transport_sections'])

    return fc
