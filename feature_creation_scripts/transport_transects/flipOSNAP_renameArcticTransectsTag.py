#!/usr/bin/env python
  
import shutil

from geometric_features import GeometricFeatures, FeatureCollection
from geometric_features.utils import write_feature_names_and_tags


gf = GeometricFeatures(cacheLocation='../../geometric_data',
                       remoteBranchOrTag='main')

fcNew = FeatureCollection()

# Flip OSNAP sections and rename their tag to 'arctic_transport_sections'
fc = gf.read('ocean', 'transect', ['OSNAP section East'])
properties = fc.features[0]['properties']
properties['tags'] = 'arctic_transport_sections'
geometry = fc.features[0]['geometry']
coords = geometry['coordinates']
geometry['coordinates'] = coords[::-1]
fcNew = fc

fc = gf.read('ocean', 'transect', ['OSNAP section West'])
properties = fc.features[0]['properties']
properties['tags'] = 'arctic_transport_sections'
geometry = fc.features[0]['geometry']
coords = geometry['coordinates']
geometry['coordinates'] = coords[::-1]
fcNew.merge(fc)

# Rename tag of remaining Arctic sections to 'arctic_transport_sections'
fc = gf.read(componentName='ocean', objectType='transect',
        tags=['standard_transport_sections', 'arctic_sections'])
for feature in fc.features:
    print(feature['properties']['name'])
    properties =  feature['properties']
    properties['tags'] = 'standard_transport_sections;arctic_transport_sections'
fcNew.merge(fc)
fc = gf.read('ocean', 'transect', ['Hudson Bay-Labrador Sea'])
properties = fc.features[0]['properties']
properties['tags'] = 'arctic_transport_sections'
fcNew.merge(fc)

fcNew.to_geojson('arctic_transport_sections.geojson')

# "split" these features into individual files in the geometric data cache
gf.split(fcNew)

# update the database of feature names and tags
write_feature_names_and_tags(gf.cacheLocation)
# move the resulting file into place
shutil.copyfile('features_and_tags.json',
                '../../geometric_features/features_and_tags.json')
