from geometric_features.aggregation.ocean import basins, subbasins, \
    antarctic, ice_shelves, ismip6, arctic as arctic_ocean, transport, \
    moc
from geometric_features.aggregation.seaice import arctic as arctic_seaice


def get_aggregator_by_name(region_group):
    """
    Get a geojson mask file and the appropriate file suffix for the given
    region group.

    Parameters
    ----------
    region_group : str
        The name of a region group to get mask features for, one of
        'Antarctic Regions', 'Arctic Ocean Regions', 'Arctic Sea Ice Regions',
        'Ocean Basins', 'Ice Shelves', 'Ocean Subbasins', or 'ISMIP6 Regions'

    Returns
    -------
    function : callable
        An aggregation functions for collecting the features, which takes a
        :py:class:`geometric_features.GeometricFeatures` object as its argument

    prefix : str
        A prefix (or suffix) for use in file names that corresponds to the
        region group

    date : str
        A date stamp when the regions in ``fc`` were last modified.  This date
        can be used to cache masks based on these regions as long as the date
        remains the same.
    """

    regions = {'Antarctic Regions': {'prefix': 'antarcticRegions',
                                     'date': '20200621',
                                     'function': antarctic},
               'Arctic Ocean Regions': {'prefix': 'arcticOceanRegions',
                                        'date': '20201130',
                                        'function': arctic_ocean},
               'Arctic Sea Ice Regions': {'prefix': 'arcticSeaIceRegions',
                                          'date': '20201130',
                                          'function': arctic_seaice},
               'Ocean Basins': {'prefix': 'oceanBasins',
                                'date': '20200621',
                                'function': basins},
               'Ice Shelves': {'prefix': 'iceShelves',
                               'date': '20200621',
                               'function': ice_shelves},
               'Ocean Subbasins': {'prefix': 'oceanSubbasins',
                                   'date': '20201123',
                                   'function': subbasins},
               'ISMIP6 Regions': {'prefix': 'ismip6Regions',
                                  'date': '20210201',
                                  'function': ismip6},
               'MOC Basins': {'prefix': 'mocBasins',
                              'date': '20210331',
                              'function': moc},
               'Transport Transects': {'prefix': 'transportTransects',
                                       'date': '20200621',
                                       'function': transport}}

    if region_group not in regions:
        raise ValueError('Unknown region group {}'.format(region_group))

    region = regions[region_group]

    prefix = region['prefix']
    date = region['date']

    function = region['function']

    return function, prefix, date
