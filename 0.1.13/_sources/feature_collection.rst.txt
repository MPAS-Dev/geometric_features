.. _FeatureCollection:

FeatureCollection
=================

``FeatureCollection`` objects can be used to manipulate features in several
ways.  Typically, you would use member functions such as ``fc.merge()``,
``fc.combine()`` and ``fc.plot()`` to perform these manipulations.

Reading in Features
-------------------

A ``FeatureCollection`` can be read from a file with the function
:func:`geometric_features.read_feature_collection`:

.. code-block:: python

   from geometric_features import read_feature_collection

   fc = read_feature_collection('features.geojson')

Add a Feature
-------------

To add a single feature to a ``FeatureColleciton``, use
:meth:`geometric_features.FeatureCollection.add_feature`:

.. code-block:: python

   fc.add_feature(feature)

``feature`` is a dictionary describing a single :ref:`feature`.

Merging Features
----------------

A ``FeatureCollection`` ``fc2`` can be merged into another colleciton ``fc1``
 with :meth:`geometric_features.FeatureCollection.merge`:

.. code-block:: python

   fc1.merge(fc2)

If the same feature name is found in both, the original feature from ``fc1`` is
retained.

Plotting Features
-----------------

A ``FeatureCollection`` can be plotted on a given map projection with
:meth:`geometric_features.FeatureCollection.plot`:

.. code-block:: python

   import matplotlib.pyplot as plt

   # plot the features in fc on a cylindrical projection
   fig = fc.plot('cyl')

   plt.show()

Tag Features
------------

All the features in a ``FeatureCollection`` can be tagged with one or more tags
using :meth:`geometric_features.FeatureCollection.tag`:

.. code-block:: python

   fc.tag(['tag1', 'tag2'])

These features can later be split into the :ref: `GemoetricData`
direcory (see :ref:`adding_features`) and uploaded to the `GitHub repository`_.
Tags make it easier to combine many features into a feature collection (e.g.
individual ocean regions into ocean basins).

Writing out Features
--------------------

To write out a ``FeatureCollection`` to a ``geojson`` file, call
:meth:`geometric_features.FeatureCollection.to_geojson`

.. code-block:: python

   fc.to_geojson('features.geojson')

Set a Group Name
----------------

To set the ``groupName`` property of a ``FeatureCollection``, call
:meth:`geometric_features.FeatureCollection.set_group_name`.

.. code-block:: python

   fc.set_group_name('Regions Group')

Group names can be used later to identify the features in a collection, e.g.
in order to create a mask for that cells in a mesh that belong to the features
in that group.  The MPAS-Ocean model uses these features to create masks for
land and for ocean regions such as ocean basins and Antarctic ice-shelf
cavities.

Combine Features
----------------

Features in a ``FeatureCollection`` can be combined (fused together into a
single feature) using
:meth:`geometric_features.FeatureCollection.combine`:

.. code-block:: python

   fcCombined = fc.combine('my feature name')


Difference Features
-------------------

Features in a ``FeatureCollection`` can be masked with one or more masking
features from another ``FeatureCollection`` using
:meth:`geometric_features.FeatureCollection.difference`:

.. code-block:: python

   fcMasked = fc.difference(fcMask)

In this example, any part of the features in ``fc`` that overlap with any of
the features in ``fcMask`` is removed in the resulting ``fcMasked``.

Simplify Features
-----------------

Sometimes, features are made up of segments or polygons with tiny edges that
add little relevant detail to the features but make the files describing them
needlessly large.  In such cases, the features can be simplified by calling
:meth:`geometric_features.FeatureCollection.simplify` with
and appropriate length scale (in degrees latitude/longitude) over which the
feature may be modified to make it simpler.  If a length scale of zero is
used, the feature will be simplified without any modification tot he shape
being described (so that only edges or polygons that are truly reduntant will
be removed).

.. code-block:: python

   fcSimplified = fc.simplify(1.0)

Fix Features at +/- 180
-----------------------

Valid ``geojson`` shapes should not cross the "antimeridian", the location
where 180 degrees longitude meets -180 degrees.  Often, it isn't practical to
contstruct a feature's geometry from the start in this way, so this function
provides a bit of a hack for removing a tiny sliver of the feature around the
antimeridian so that the resulting shape remians between -180 and 180 degrees
longitude.

:meth:`geometric_features.FeatureCollection.fix_antimeridian`

.. code-block:: python

   fcFixed = fc.fix_antimeridian()

.. _`GitHub repository`: https://github.com/MPAS-Dev/geometric_features