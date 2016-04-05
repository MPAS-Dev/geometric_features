This repository houses definitions of geometric features. These features
can include regions, transects, and points. Currently they are described in
geojson format.  For example, here are some regions for Antarctica.

![alt text](https://cloud.githubusercontent.com/assets/4179064/12921663/93282b64-cf4e-11e5-9260-a78dfadc4459.png "Antarctica regions")

Data for regions has been derived from sources listed in the
[contributors file](contributors/CONTRIBUTORS.md) as specified
via the `author` field in each `geojson` file.

The scripts in the top level directory can be used to help maintain and use
this repository. All of them can be run with the -h flag to get usage
information.

A typical workflow will look like:
* Build feature list (features.geojson):
 - Multiple calls to: ./merge_features.py
* Edit features:
 - Edit features.geojson
* Visualize features:
 - ./plot_features.py <br /> (Note: requires cartopy package, e.g., `conda install -c scitools cartopy`)
* Split features:
 - ./split_features.py

**IMPORTANT:** Always use the split_features.py script when placing features in
their respective directories. This will help everyone maintain the repository,
and allow tools to parse them cleanly.

An example workflow to select and plot region features is

```
$ rm features.geojson
$ ./merge_features.py -d ocean
$ ./merge_features.py -f iceshelves/region/Ronne_1/region.geojson
$ ./merge_features.py -d landice
$ ./plot_features.py -f features.geojson
```
