#!/usr/bin/env python
"""
This script combines Antarctic basins into a single feature file.
"""

# stuff to make scipts work for python 2 and python 3
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import matplotlib.pyplot as plt

from geometric_features import GeometricFeatures

plot = True

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data')

# create a FeatureCollection containing all land-ice regions wtih one of three
# IMBIE tags
tags = ['WestAntarcticaIMBIE', 'AntarcticPeninsulaIMBIE',
        'EastAntarcticaIMBIE']
fc = gf.read(componentName='landice', objectType='region', tags=tags,
             allTags=False)

# save the feature collection to a geojson file
fc.to_geojson('Antarctic_Basins.geojson')

if plot:
    fc.plot(projection='southpole')
    plt.show()
