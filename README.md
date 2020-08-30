# Geometric Features

[![Build Status](https://dev.azure.com/MPAS-Dev/geometric_features%20testing/_apis/build/status/MPAS-Dev.geometric_features?branchName=temp)](https://dev.azure.com/MPAS-Dev/geometric_features%20testing/_build/latest?definitionId=3&branchName=temp)

This repository houses definitions of geometric features. These features
can include regions, transects, and points, described in geojson format.
For example, here are some regions for Antarctica.
![alt text](https://cloud.githubusercontent.com/assets/4179064/12921663/93282b64-cf4e-11e5-9260-a78dfadc4459.png "Antarctica regions")

## Documentation

[http://mpas-dev.github.io/geometric_features/stable/](http://mpas-dev.github.io/geometric_features/stable/)

## Contributors

Data for regions has been derived from sources listed in the
[contributors file](contributors/CONTRIBUTORS.md) as specified
via the `author` field in each `geojson` file.

## Quick Start

The python `geometric_features` package can be used to help maintain and use
this repository. Several example scripts that make use of the package can be
found in the `examples` directory.  Each of the classes and functions that make
up the package have extensive documentation.  More user-level documentation
will be added shortly.

To use geometric features, you can install it in a conda environment:
```bash
conda create -n geometric_features -c conda-forge python=3.7 geometric_features
conda activate geometric_features
```
By default, `geometric_features` will download the data it needs on the fly.
Since some of the features are quite large, this can be convenient if disk
space is at a premium.

Some systems do not support downloading the data (e.g. because of firewalls or
compute nodes that don't have internet access.  In such cases, it is convenient
to install `geometric_features` including all the data:
```bash
conda create -n geometric_features -c conda-forge python=3.7 \
    "geometric_features=*=*with_data*"
conda activate geometric_features
```
This syntax is admittedly a bit clunky but it selects for a special build of
the conda package with the data included.

To develop `geometric_features` (e.g. to add new features), it is highly
recommended that you use an `anaconda` python environment.  Here is how to
create and activate an environment with all of the required dependencies:
```bash
conda create -n geometric_features -c conda-forge python=3.7 numpy matplotlib \
    cartopy shapely requests progressbar2
conda activate geometric_features
```

A typical workflow will look like:
* Create a `GeometricFeatures` object and point it to a location where you have
  stored (or would like to store) geometry data.
  - `gf = GeometricFeatures(localCache='./geometric_data')`
* Read in one or more `FeatureCollection`s from the `geojson` files in the
  `geometric_data` directory.
  - `fcArctic = gf.read('ocean', 'region', featureNames=['Arctic Ocean'])`
  - `fcAtlantic = gf.read('ocean', 'region', tags=['Atlantic_Basin'])`
* Edit features:
  - Merge, combine, tag, mask out or simplify the features, see below.
  - Use the `shapely` package to edit the geometry in more sophisticated ways
* Visualize features:
  - `fc.plot(projection='cyl')`
* Split feature collection back into individual features for inclusion in the
  repo:
  - `gf.split(fc)`

Available functionality includes:
* `fc.merge(other)` - Merge two feature collection together.
* `fc.combine()` - Combine features into a single feature.
* `fc.difference()` - Mask features using shapes in a second feature file.
* `fc.fix_antimeridian()` - Split a feature at the antimeridian (+/- 180 longitude). The resulting feature has all points between -180 and 180 lon.
* `fc.set_group_name()` - Set the "groupName" property of the `FeatureCollection`
* `fc.tag()` - Add one or more tags to the "tag" property of each feature in a collection.  This can be useful for reading back a collection of features with that tag.

**IMPORTANT:** Always use the `gf.split(fc)` script when placing features into
the `geometric_data` directory. This will help everyone maintain the
repository, and allow tools to parse them cleanly.

Many of this functionality can also be accessed with a command-line interface:
```bash
merge_features
combine_features
difference_features
set_group_name
split_features
simplify_features
tag_features
plot_features
```
Use the `-h` flag to find out more.

An example workflow to read in, plot and write out a set of features is
```python
#!/usr/bin/env python

from geometric_features import GeometricFeatures
import matplotlib.pyplot as plt

# create a GeometricFeatures object that points to a local cache of geometric
# data and knows which branch of geometric_feature to use to download
# missing data
gf = GeometricFeatures(cacheLocation='./geometric_data')

# read in a FeatureCollection containing all ocean regions in the Atlantic
# basin
fcAtlantic = gf.read(componentName='ocean', objectType='region',
                     tags=['Atlantic_Basin'])

fcAtlantic.plot('cyl')
plt.title('Atlantic merged')

# combine them all into a single feature
fcAtlantic = fcAtlantic.combine(featureName='Atlantic_Basin')
fcAtlantic.plot('cyl')
plt.title('Atlantic combined')

# make another feature containing the regions in Filchner-Ronne Ice Shelf
fcFilchnerRonne = gf.read(componentName='iceshelves', objectType='region',
                          featureNames=['Filchner_1', 'Filchner_2',
                                        'Filchner_3', 'Ronne_1', 'Ronne_2'])
fcFilchnerRonne.plot('southpole')
plt.title('Filchner-Ronne')


# make one more collection of all the IMBIE basins in West Antarctica
fcWestAntarctica = gf.read(componentName='landice', objectType='region',
                           tags=['WestAntarcticaIMBIE'])

fcWestAntarctica.plot('southpole')
plt.title('West Antarctica')

fcWestAntarctica.to_geojson('west_antarctica.geojson')
plt.show()
```
