.. _aggregation:

Aggregate Existing Features
===========================

The :py:mod:`geometric_features.aggregation` module contains functions used to
aggregate existing features to make new, larger ones.


Aggregating Ocean Features
--------------------------

Ocean Sub-basins
~~~~~~~~~~~~~~~~

The only aggregation function that is currently available is
:py:func:`geometric_features.aggregation.ocean.subbasins`, which aggregates
oceanic regions to make the following ocean subbasins: North and South Atlantic,
North and South Pacific, Indian Basin, Arctic Basin, and Southern Ocean Basin.

.. image:: images/subbasins.png
   :width: 500 px
   :align: center
