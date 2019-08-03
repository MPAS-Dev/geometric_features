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

   # make a geometric features object that points to geometry in the local
   # cache in ./geometric_data
   gf = GeometricFeatures(cacheLocation='./geometric_data')

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


It is not recommended that you modified features directly in
``geometric_data``, but if you have already done so, you can update the
manifest of all features and tags based on your changes first, then merge your
features into a feature collection and then split it back out into individual
features to ensure consistent formatting.

.. code-block:: python

    import os
    from geometric_features import GeometricFeatures
    from geometric_features.utils import write_feature_names_and_tags


    # Write a file features_and_tags.json with features and tags from the cache.
    # This updates the file names, feature names and tags that geometric_features
    # knows about.
    write_feature_names_and_tags('./geometric_data')

    # move features_and_tags.json into geometric_features to replace the old
    # manifest
    os.rename('features_and_tags.json',
              'geometric_features/features_and_tags.json')

    # Make a geometric features object that gets data from a local cache in
    # ./geometric_data.  (The remote branch won't matter.)
    gf = GeometricFeatures(cacheLocation='./geometric_data')

    # Make a feature colleciton with the standrd transport sections
    fc = gf.read(componentName='ocean', objectType='transect',
                 tags=['standard_transport_sections'])

    # split the feature collection back into individual features within
    # ./geometric_data to clean things up
    gf.split(fc)


.. _`GitHub repository`: https://github.com/MPAS-Dev/geometric_features
