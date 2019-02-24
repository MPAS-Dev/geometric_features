#!/usr/bin/env python
"""
This script combines Antarctic basins extended to the continental-shelf break
into a single feature file.
"""

# stuff to make scipts work for python 2 and python 3
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from geometric_features import GeometricFeatures, FeatureCollection

import matplotlib.pyplot as plt

plot = True

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data', 'master')

# create a FeatureCollection containing all iceshelf regions wtih one of the
# 27 IMBIE basin tags tags
fc = FeatureCollection()
for basin in range(1, 28):
    print('Adding feature from IMBIE basin {:d}'.format(basin))
    basinName = 'Antarctica_IMBIE{:d}'.format(basin)
    tags = [basinName]
    # load the iceshelf regions for one IMBIE basin
    fcBasin = gf.read(componentName='iceshelves', objectType='region',
                      tags=tags)

    # combine all regions in the basin into a single feature
    fcBasin = fcBasin.combine(featureName=basinName)

    # merge the feature for the basin into the collection of all basins
    fc.merge(fcBasin)

# save the feature collection to a geojson file
fc.to_geojson('Extended_Antarctic_Basins.geojson')

if plot:
    fc.plot(projection='southpole')
    plt.show()
