.. _GeometricData:

Geometric Data
==============

The the overarching purpose of ``geometric_features`` is to facilitate access
to and manipulation of the geometric data in the repository.  This data is
currently divided across 5 components, ``bedmap2``, ``iceshelves``,
``landice``,  ``natural_earth``, and  ``ocean``.

Components
----------

bedmap2
^^^^^^^

This component defines two "coastlines" between the Antarctic continent and
the ocean.  One exclues the cavity under ice shelves while the other includes
them.  The dataset used to define these coastlines is Bedmap2
(`Fretwell et al. 2016`_).

iceshelves
^^^^^^^^^^

This component defines regions that extend the bounds of present-day Antarctic
ice shelves both out to the edge of the continental shelf and into regions of
grounded ice.  These maps are used to partition maps of Antarctic melt into
total and average melt fluxes over these ice shelves in ocean models that
simulate this melting.  The ice-shelf features have been divided across the
`IMBIE1 Basins`_ so that melt rates can also be aggregated per basin.

landice
^^^^^^^

This component defines regions covering `IMBIE1 Basins`_ in Antarctica and
Greenland.

natural_earth
^^^^^^^^^^^^^

This component defines a single, high-resolution region for global land
coverage from `Natural Earth`_.

ocean
^^^^^

This component contains regions, transects and points of significance for the
global ocean.  The regions mostly define individual seas from the
`International Hydrographic Organisation`_, but some are masking regions used
to delineate larger basins such as those used for computing the Meridional
Overturning Circulation.  The transects include passages through which ocean
transport is commonly measured; locations of so-called "critical passages",
though which ocean flow must be allowed at lower model resolution; and
"critical land blockages" such as the Antarctic Peninsula, though which ocean
should not be allowed to flow.  The points in the database are mostly used
as seed points for flood-filling ocean meshes to exclude inland seas that are
not connected to the ocean.  These points are also sometimes used to sample
ocean properties to debug model runs.

Object Types
------------

``geometric_features`` supports three object types: regions, transects and
points.  Regions are by far the most common, defining areas on the globe.
Transects define a connected series of line setments on the globe (typically
with the implication that they will also include a depth component from the
ocean model, though the features are defined only on the surface of the
sphere).  These could represent such features as ship tracks, passages,
radar lines, or float trajectories.  Points specify a single location on the
globe.

.. _feature:

Feature
-------

An individual feature is defined by nested datastructure of python
dictionaries.  The outermost dictionary contains at least 3 keys:
``'type'``, ``'properties'`` and ``'geometry'``.

type
^^^^

The value corresponding to the ``'type'`` key of a feature is always
``'Feature'``.

properties
^^^^^^^^^^

The properties of a feature are stored in another python dictionary, nested in
the outer dictionary.  Properties include: ``'name'`` - the name of the
feature; ``'tags'`` - a list of tags describing the feature, separated by
semicolons; ``'object'`` - the object type of the feature (region, transect or
point); ``'component'`` - the component of the feature; and ``'author'`` -
a comma- or semicolon-separated list of authors (or URLs).  Optionally, a
feature can include any number of other user-defined properties.

geometry
^^^^^^^^

The ``'type'`` of the geometry (``'Polygon'`` or ``'MultiPolygon'`` for a
region, ``'LineString'`` or ``'MultiLineString'`` for a transect and
``'Point'`` or ``'Multipoint'`` for a point) and the ``'coordinates'`` defining
the feature's geometry.  By far, the easiest way to create an manipulate the
geometry is with the `shapely package`_.

Examples
^^^^^^^^

Here are two simple examples of features from the repository:

.. code-block:: python

    {
        "type": "Feature",
        "properties": {
            "name": "Southern_Ocean_Drake_Passage_W070.0_S55.0",
            "tags": "seed_point",
            "object": "point",
            "component": "ocean",
            "author": "Todd Ringler"
        },
        "geometry": {
            "type": "Point",
            "coordinates": [
                -70.000000,
                -55.000000
            ]
        }
    }

.. code-block:: python

    {
        "type": "Feature",
        "properties": {
            "name": "Global Ocean 15S to 15N",
            "tags": "Equatorial_Basin",
            "object": "region",
            "component": "ocean",
            "author": "Anne Berres, Xylar Asay-Davis"
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        180.000000,
                        15.000000
                    ],
                    [
                        180.000000,
                        -15.000000
                    ],
                    [
                        0.000000,
                        -15.000000
                    ],
                    [
                        -180.000000,
                        -15.000000
                    ],
                    [
                        -180.000000,
                        15.000000
                    ],
                    [
                        0.000000,
                        15.000000
                    ],
                    [
                        180.000000,
                        15.000000
                    ]
                ]
            ]
        }

.. _`Fretwell et al. 2016`: http://www.the-cryosphere.net/7/375/2013/
.. _`IMBIE1 Basins`: http://imbie.org/imbie-2016/drainage-basins/
.. _`Natural Earth`: http://www.naturalearthdata.com/
.. _`International Hydrographic Organisation`: http://www.marineregions.org/downloads.php#iho
.. _`shapely package`: https://shapely.readthedocs.io/
