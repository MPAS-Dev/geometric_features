#############
API reference
#############

This page provides an auto-generated summary of the geometric features API. For
more details and examples, refer to the relevant chapters in the main part of
the documentation.

Command-line scripts
====================

.. currentmodule:: geometric_features.__main__

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

.. currentmodule:: geometric_features.geometric_features

.. autosummary::
   :toctree: generated/

   GeometricFeatures
   GeometricFeatures.read
   GeometricFeatures.split

.. currentmodule:: geometric_features.feature_collection

.. autosummary::
   :toctree: generated/

   read_feature_collection
   FeatureCollection
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
