def arctic(gf):
    """
    Aggregate sea-ice-relevant Arctic regions

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features

    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with sea-ice-relevant Arctic regions
    """
    # Authors
    # -------
    # Milena Veneziani, Xylar Asay-Davis

    fc = gf.read(componentName='ocean', objectType='region',
                 tags=['Arctic_NSIDC'])

    return fc
