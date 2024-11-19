.. currentmodule:: geometric_features

#############
API reference
#############

This page provides an auto-generated summary of the geometric features API. For
more details and examples, refer to the relevant chapters in the main part of
the documentation.

Command-line scripts
====================

.. autosummary::
   :toctree: generated/

   combine_features
   difference_features
   fix_features_at_antimeridian
   merge_features
   plot_features
   set_group_name
   split_features
   simplify_features
   tag_features


Python package
==============

Reading Geometric Features
--------------------------

.. autosummary::
   :toctree: generated/

   GeometricFeatures
   GeometricFeatures.read

Splitting new data into Geometric Features
------------------------------------------

.. autosummary::
   :toctree: generated/

   GeometricFeatures.split
   write_feature_names_and_tags

Reading a Feature Collection
----------------------------

.. autosummary::
   :toctree: generated/

   read_feature_collection

Creating a Feature Collection
-----------------------------

.. autosummary::
   :toctree: generated/

   FeatureCollection

Manipulating a Feature Collection
---------------------------------

.. autosummary::
   :toctree: generated/

   FeatureCollection.add_feature
   FeatureCollection.merge
   FeatureCollection.tag
   FeatureCollection.set_group_name
   FeatureCollection.combine
   FeatureCollection.difference
   FeatureCollection.fix_antimeridian
   FeatureCollection.simplify
   FeatureCollection.feature_in_collection
   FeatureCollection.to_geojson
   FeatureCollection.plot

Aggregation
-----------

.. autosummary::
   :toctree: generated/

   aggregation
   aggregation.get_aggregator_by_name
   aggregation.ocean
   aggregation.ocean.subbasins
   aggregation.ocean.basins
   aggregation.ocean.moc
   aggregation.ocean.arctic
   aggregation.ocean.antarctic
   aggregation.ocean.ismip6_greenland
   aggregation.ocean.ice_shelves
   aggregation.ocean.transport

   aggregation.seaice
   aggregation.seaice.arctic
   aggregation.seaice.qgreenland
   aggregation.landice.nasa_greenland
