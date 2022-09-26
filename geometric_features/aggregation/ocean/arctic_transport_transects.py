def arctic_transport(gf):
    """
    Aggregate Arctic transport transects

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
    # Milena Veneziani

    fc = gf.read(componentName='ocean', objectType='transect',
                 tags=['arctic_transport_sections'])

    return fc
