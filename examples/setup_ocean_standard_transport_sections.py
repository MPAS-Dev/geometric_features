#!/usr/bin/env python
"""
This script creates region groups for the standard set of transport sections,
all of which have the "standard_transport_sections" tag.
"""

from geometric_features import GeometricFeatures

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures('./geometric_data')

# create a FeatureCollection containing all ocean transects wtih the
# "Critical_Passage" tag
fc = gf.read(componentName='ocean', objectType='transect',
             tags=['standard_transport_sections'])

# set the group name describing the full feature collection
fc.set_group_name(groupName='StandardTransportSectionsRegionsGroup')

# save the feature collection to a geojson file
fc.to_geojson('standard_transport_sections.geojson')
