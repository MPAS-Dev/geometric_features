#!/usr/bin/env python
"""
This script combines Natural Earth land coverage north of 60S with Antarctic
ice coverage or grounded ice coverage from Bedmap2.  If the ``withCavities``
variable is set to ``True``, the land over uses grounded ice rather than
both grounded and floating ice to determine land coverage (thus opening
up sub-ice-shelf cavities in the ocean around Antarctica.
"""

# stuff to make scipts work for python 2 and python 3
from __future__ import absolute_import, division, print_function, \
    unicode_literals

from geometric_features import GeometricFeatures

import matplotlib.pyplot as plt

plot = True
withCavities = False

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data', 'master')

# start with the land coverage from Natural Earth
fcLandCoverage = gf.read(componentName='natural_earth', objectType='region',
                         featureNames=['Land Coverage'])

# remove the region south of 60S so we can replace it based on ice-sheet
# topography
fcSouthMask = gf.read(componentName='ocean', objectType='region',
                      featureNames=['Global Ocean 90S to 60S'])

fcLandCoverage = fcLandCoverage.difference(fcSouthMask)

# Add "land" coverage from either the full ice sheet or just the grounded
# part
if withCavities:
    fcAntarcticLand = gf.read(componentName='bedmap2', objectType='region',
                              featureNames=['AntarcticGroundedIceCoverage'])
else:
    fcAntarcticLand = gf.read(componentName='bedmap2', objectType='region',
                              featureNames=['AntarcticIceCoverage'])

fcLandCoverage.merge(fcAntarcticLand)

# save the feature collection to a geojson file
fcLandCoverage.to_geojson('landCoverage.geojson')

if plot:
    fcLandCoverage.plot(projection='cyl')
    plt.show()
