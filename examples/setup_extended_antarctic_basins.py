#!/usr/bin/env python
"""
This script combines Antarctic basins extended to the continental-shelf break
into a single feature file.
"""

import matplotlib.pyplot as plt

from geometric_features import FeatureCollection, GeometricFeatures

plot = True

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data')

# create a FeatureCollection containing all iceshelf regions wtih one of the
# 27 IMBIE basin tags tags
fc = FeatureCollection()
for basin in range(1, 28):
    print(f'Adding feature from IMBIE basin {basin:d}')
    basinName = f'Antarctica_IMBIE{basin:d}'
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
