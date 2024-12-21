#!/usr/bin/env python
"""
This script combines transects defining cricial passages.
"""

# stuff to make scipts work for python 2 and python 3
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from geometric_features import GeometricFeatures

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data')

# create a FeatureCollection containing all ocean transects wtih the
# "Critical_Passage" tag
fc = gf.read(componentName='ocean', objectType='transect',
             tags=['Critical_Passage'])

# save the feature collection to a geojson file
fc.to_geojson('criticalPassages.geojson')
