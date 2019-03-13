.. _adding_features:

Adding New Features
===================

If you have created new feature collection and wish for the individual features
to be included in :ref:`GeometricData`, you should:
* clone the full `GitHub repository`_
* split the feature collection into its individual features
* update the manifest of all features and tags
* commit the changes and make a pull request

.. code-block:: python

   import os
   from geometric_features import GeometricFeatures, read_feature_collection
   from geometric_features.utils import write_feature_names_and_tags

   # A new feature colleciton has been constructed and tagged using the
   # naming convetions of geometric_features
   fc = read_feature_collection('my_new_features.geojson')

   # get geometric data from geometric_features v0.1 and store it in
   # the local directory ./geometric_data
   gf = GeometricFeatures(localCache='./geometric_data')

   # split the feature collection into individual features within
   # ./geometric_data
   gf.split(fc)

   # write a file features_and_tags.json with features and tags from the cache
   write_feature_names_and_tags(gf.cacheLocation)

   # move features_and_tags.json into geometric_features to replace the old
   # manifest
   os.rename('features_and_tags.json',
             'geometric_features/features_and_tags.json)

After this, you can ``git add`` and ``git commit`` the changes, and make a
pull request to have them added to the repository.

.. _`GitHub repository`: https://github.com/MPAS-Dev/geometric_features