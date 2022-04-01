.. _GeometricFeatures:

GeometricFeatures
=================

The ``GeometricFeatures`` class knows about both a local cache of
:ref:`GeometricData` and the `GitHub repository`_ where it can be retrieved as
needed.  A ``GeometricFeatures`` object is created with an optional path to the
local cache and/or the name of the remote branch or tag in which to find the
geometric data.  The default local cache is ``./geometric_data``, and the
default remote branch is the same as the version number of the
``geometric_features`` package that is installed (highly recommended!).  If
using a branch other than the package version, the list of all available
features and tags (which is included in the package) may not include all the
features in the desired branch. That is, if you install v0.1 of the
``geometric_features`` conda package, you should expect to work with v0.1
of the :ref:`GeometricData` as well.

An example workflow for creating a ``GeometricFeatures`` object and using it
to read in a set of geometric features (possibly after downloading the
geometric data from GitHub) is:

.. code-block:: python

   from geometric_features import GeometricFeatures

   # get geometric data from geometric_features v0.1 and store it in
   # the local directory ./geometric_data
   gf = GeometricFeatures(localCache='./geometric_data',
                          remoteBranchOrTag='0.1')

   # read in a feature collection defining the coastline
   fc = gf.read(componentName='natural_earth', objectType='region',
                featureNames=['Land Coverage'])

.. _`GitHub repository`: https://github.com/MPAS-Dev/geometric_features