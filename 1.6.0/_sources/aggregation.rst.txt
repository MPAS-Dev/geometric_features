.. _aggregation:

Aggregate Existing Features
===========================

The :py:mod:`geometric_features.aggregation` module contains functions used to
aggregate existing features to make new, larger ones.  An example usage of these
aggregation functions is to create masks for regional averaging.

The function :py:func:`geometric_features.aggregation.get_aggregator_by_name()`
can be used to get information about one of the aggregated features by one of
the following group names:

* Antarctic Regions

* Arctic Ocean Regions

* Arctic Sea Ice Regions

* ISMIP6 Greenland Regions

* NASA Greenland Regions

* Ocean Basins

* Ice Shelves

* Ocean Subbasins

* Historical Sea Ice

* ISMIP6 Regions

* Transport Transects

This function returns the function that will aggregate the requested group,
a prefix for the group (a modified version of the group name) and a date stamp
that is updated each time the features in the group are changed.  This way,
mask files can be created from these features with filenames that include the
date stamp.  As long as the date stamp has not changed, these cached mask files
can be reused.


Aggregating Ocean Features
--------------------------

Ocean Sub-basins
~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.subbasins`
aggregates oceanic regions to make the following ocean subbasins: North and
South Atlantic, North and South Pacific, Indian Basin, Arctic Basin, and
Southern Ocean Basin.

.. image:: images/subbasins.png
   :width: 500 px
   :align: center

Ocean Basins
~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.basins` aggregates
oceanic regions to make the following ocean basins: Atlantic, Pacific, Indian,
Arctic, Southern Ocean, Mediterranean, Global Ocean, Global Ocean 65N to 65S,
Global Ocean 15S to 15N.

Meridional Overturning Circulation Basins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.moc` aggregates
basins for computing the MOC: Atlantic, IndoPacific, Pacific and Indian

Arctic Regions
~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.arctic` aggregates
regions of the Arcic (and subArctic): Baffin Bay, Baltic Sea, Barents Sea, 
Beaufort Gyre, Beaufort Gyre Shelf, Canada Basin, Canadian Archipelago, 
Central Arctic, Chukchi Sea, East Siberian Sea, Greenland Sea, Hudson Bay, 
Irminger Sea, Kara Sea, Labrador Sea, Laptev Sea, North Sea, Norwegian Sea, and
Arctic Ocean - no Barents, Kara Seas.

Antarctic Regions
~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.antarctic` aggregates
regions of the Antarctic: Southern Ocean, Southern Ocean 60S,
Eastern Weddell Sea Shelf, Eastern Weddell Sea Deep, Western Weddell Sea Shelf,
Western Weddell Sea Deep, Weddell Sea Shelf, Weddell Sea Deep,
Bellingshausen Sea Shelf, Bellingshausen Sea Deep, Amundsen Sea Shelf,
Amundsen Sea Deep, Eastern Ross Sea Shelf, Eastern Ross Sea Deep,
Western Ross Sea Shelf, Western Ross Sea Deep, East Antarctic Seas Shelf,
East Antarctic Seas Deep.

ISMIP6 Greenland Regions
~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.ismip6_greenland`
aggregates regions of the continental shelves around Greenland based on the
ISMIP6 regions: ISMIP6 Greenland Central East Shelf,
ISMIP6 Greenland Central West Shelf, ISMIP6 Greenland North East Shelf,
ISMIP6 Greenland North Shelf, ISMIP6 Greenland North West Shelf,
ISMIP6 Greenland South East Shelf, ISMIP6 Greenland South West Shelf. Regions cover both
landice and ocean, and could be used for either component.

NASA Greenland Regions
~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.landice.nasa_greenland`
aggregates regions of Greenland drainage basins taken from NASA: 
(https://earth.gsfc.nasa.gov/cryo/data/polar-altimetry/antarctic-and-greenland-drainage-systems)
The drainage basins have been altered to extend to the continental shelf break. Boundaries between basins
have also been altered so that all glaciers terminating in an individual fjord 
are from the same drainage basin. Regions cover both landice and ocean, and could be used for either
component.

Historical Sea Ice
~~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.seaice.qgreenland`
aggregates the historical monthly median sea ice extents taken from 
the QGreenland dataset (doi: doi:10.5281/zenodo.12823307): January Historical Median Sea Ice Extent,
February Historical Median Sea Ice Extent, March Historical Median Sea Ice Extent,
April Historical Median Sea Ice Extent, May Historical Median Sea Ice Extent,
June Historical Median Sea Ice Extent, July Historical Median Sea Ice Extent,
August Historical Median Sea Ice Extent, September Historical Median Sea Ice Extent,
October Historical Median Sea Ice Extent, November Historical Median Sea Ice Extent,
December Historical Median Sea Ice Extent.

Ice-shelf Regions
~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.ice_shelves`
aggregates ice shelves and ice-shelf regions.  There are 106 regions, so they
won't all be listed.  See the resulting feature collection or the code itself
for the full list.

Transport Transects
~~~~~~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.ocean.transport`
aggregates transport transects:  Africa-Ant, Agulhas, Antilles Inflow,
Barents Sea Opening, Bering Strait, Davis Strait, Drake Passage,
Florida-Bahamas, Florida-Cuba, Fram Strait", Indonesian Throughflow,
Lancaster Sound, Mona Passage", Mozambique Channel, Nares Strait, Tasmania-Ant
Windward Passage.

Aggregating Sea-ice Features
----------------------------

Arctic Regions
~~~~~~~~~~~~~~

The function :py:func:`geometric_features.aggregation.seaice.arctic` aggregates
regions of the Arctic as defined by the
`National Snow and Ice Data Center (NSIDC) <https://nsidc.org/>`_ that are
relevant for sea ice: Baffin Bay NSIDC, Barents Sea, Beaufort Sea NSIDC,
Canadian Archipelago NSIDC, Central Arctic NSIDC, Chukchi Sea NSIDC,
East Siberian Sea NSIDC, Hudson Bay NSIDC, Kara Sea, Laptev Sea NSIDC.
