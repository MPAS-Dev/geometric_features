def antarctic(gf):
    """
    Aggregate Antarctic regions similar to Timmermann et al. (2013)

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

    regions = ['Southern Ocean', 'Southern Ocean 60S',
               'Eastern Weddell Sea Shelf', 'Eastern Weddell Sea Deep',
               'Western Weddell Sea Shelf', 'Western Weddell Sea Deep',
               'Weddell Sea Shelf', 'Weddell Sea Deep',
               'Bellingshausen Sea Shelf', 'Bellingshausen Sea Deep',
               'Amundsen Sea Shelf', 'Amundsen Sea Deep',
               'Eastern Ross Sea Shelf', 'Eastern Ross Sea Deep',
               'Western Ross Sea Shelf', 'Western Ross Sea Deep',
               'East Antarctic Seas Shelf', 'East Antarctic Seas Deep']

    fc = gf.read(componentName='ocean', objectType='region',
                 featureNames=regions)

    return fc
