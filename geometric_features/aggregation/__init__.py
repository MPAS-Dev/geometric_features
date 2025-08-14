from geometric_features.aggregation.landice import (
    nasa_greenland as nasa_greenland,
)
from geometric_features.aggregation.landice import (
    uummannaq_disko as uummannaq_disko,
)
from geometric_features.aggregation.ocean import (
    antarctic as antarctic,
)
from geometric_features.aggregation.ocean import arctic as arctic_ocean
from geometric_features.aggregation.ocean import (
    arctic_transport as arctic_transport,
)
from geometric_features.aggregation.ocean import (
    basins as basins,
)
from geometric_features.aggregation.ocean import (
    ice_shelves as ice_shelves,
)
from geometric_features.aggregation.ocean import (
    ismip6 as ismip6,
)
from geometric_features.aggregation.ocean import (
    ismip6_greenland as ismip6_greenland,
)
from geometric_features.aggregation.ocean import (
    moc as moc,
)
from geometric_features.aggregation.ocean import (
    subbasins as subbasins,
)
from geometric_features.aggregation.ocean import (
    transport as transport,
)
from geometric_features.aggregation.seaice import arctic as arctic_seaice
from geometric_features.aggregation.seaice import (
    qgreenland as qgreenland_seaice,
)


def get_aggregator_by_name(region_group):
    """
    Get a geojson mask file and the appropriate file suffix for the given
    region group.

    Parameters
    ----------
    region_group : str
        The name of a region group to get mask features for, one of
        'Antarctic Regions', 'Arctic Ocean Regions', 'Arctic Sea Ice Regions',
        'Ocean Basins', 'Ice Shelves', 'Ocean Subbasins', 'ISMIP6 Regions',
        'MOC Basins', 'Transport Transects', or 'Arctic Transport Transects'

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

    regions = {
        'Antarctic Regions': {
            'prefix': 'antarcticRegions',
            'date': '20230403',
            'function': antarctic,
        },
        'Arctic Ocean Regions': {
            'prefix': 'arcticOceanRegions',
            'date': '20201130',
            'function': arctic_ocean,
        },
        'Arctic Sea Ice Regions': {
            'prefix': 'arcticSeaIceRegions',
            'date': '20201130',
            'function': arctic_seaice,
        },
        'Ocean Basins': {
            'prefix': 'oceanBasins',
            'date': '20240830',
            'function': basins,
        },
        'Ice Shelves': {
            'prefix': 'iceShelves',
            'date': '20200621',
            'function': ice_shelves,
        },
        'Ocean Subbasins': {
            'prefix': 'oceanSubbasins',
            'date': '20201123',
            'function': subbasins,
        },
        'ISMIP6 Greenland Regions': {
            'prefix': 'ismip6GreenlandRegions',
            'date': '20240510',
            'function': ismip6_greenland,
        },
        'NASA Greenland Regions': {
            'prefix': 'nasaGreenlandRegions',
            'date': '20241017',
            'function': nasa_greenland,
        },
        'Uummannaq/Disko GIS Glaciers': {
            'prefix':'UummannaqDisko',
            'date': '20250812',
            'function': uummannaq_disko,
        },
        'ISMIP6 Regions': {
            'prefix': 'ismip6Regions',
            'date': '20210201',
            'function': ismip6,
        },
        'MOC Basins': {
            'prefix': 'mocBasins',
            'date': '20210623',
            'function': moc,
        },
        'Historical Sea Ice': {
            'prefix': 'historicalSeaIce',
            'date': '20241018',
            'function': qgreenland_seaice,
        },
        'Transport Transects': {
            'prefix': 'transportTransects',
            'date': '20210323',
            'function': transport,
        },
        'Arctic Transport Transects': {
            'prefix': 'arcticTransportTransects',  # noqa: E501
            'date': '20220926',
            'function': arctic_transport,
        },
    }

    if region_group not in regions:
        raise ValueError(f'Unknown region group {region_group}')

    region = regions[region_group]

    prefix = region['prefix']
    date = region['date']

    function = region['function']

    return function, prefix, date
