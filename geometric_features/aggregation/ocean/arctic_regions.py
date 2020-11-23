def arctic(gf):
    """
    Aggregate ocean-relevant Arctic regions

    Parameters
    ----------
    gf : geometric_features.GeometricFeatures
        An object that knows how to download and read geometric features

    Returns
    -------
    fc : geometric_features.FeatureCollection
        The new feature collection with ocean-relevant Arctic regions
    """
    # Authors
    # -------
    # Milena Veneziani, Xylar Asay-Davis

    fc = gf.read(componentName='ocean', objectType='region',
                 tags=['Arctic', 'Arctic_Proshutinsky'], allTags=False)

    fcArcticLimited = gf.read('ocean', 'region', featureNames=[
        'Chukchi Sea', 'Canada Basin', 'East Siberian Sea', 'Laptev Sea',
        'Central Arctic'])

    fcArcticLimited = fcArcticLimited.combine(
        'Arctic Ocean - no Barents, Kara Seas')

    fc.merge(fcArcticLimited)

    return fc
