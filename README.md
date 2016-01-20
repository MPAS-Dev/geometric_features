This repository will house definitions of geometric features. These features
can include regions, transects, and points. Currently they are described in
geojson format.

The scripts in the top level directory can be used to help maintain and use
this repository. All of them can be run with the -h flag to get usage
information.

A typical workflow will look like:
* Build feature list (features.geojson):
 - Multiple calls to: ./merge_features.py
* Edit features:
 - Edit features.geojson
* Visualize features:
 - ./plot_features.py <br /> (Note: requires basemap package, e.g., conda install -c `https://conda.anaconda.org/anaconda basemap`)
* Split features:
 - ./split_features.py

**IMPORTANT:** Always use the split_features.py script when placing features in
their respective directories. This will help everyone maintain the repository,
and allow tools to parse them cleanly.

