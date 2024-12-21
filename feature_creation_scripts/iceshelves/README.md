These scripts are used to create the `iceshelf` features that cover not only
the current positions of ice shelves but also extend them both under grounded
ice and out to the -800 m isobath, allowing floating regions to be identified
with ice shelves even after the grounding line has advanced or retreated.

Instructions for re-creating the `iceshelf` feature sin `iceshelves.geojson`:

 * Download `bedmap2_bin.zip` from [https://www.bas.ac.uk/project/bedmap-2/](https://www.bas.ac.uk/project/bedmap-2/)
 * Unzip `bedmap2_bin.zip` (should create `./bedmpa2_bin/`)
 * Download `antarctica_ice_velocity_900m.nc` from
   [http://nsidc.org/data/docs/measures/nsidc0484_rignot/](http://nsidc.org/data/docs/measures/nsidc0484_rignot/)
 * Do the following:
```bash
conda install numpy scipy netcdf4 matplotlib progressbar scikit-fmm basemap \
    scikit-image shapely descartes cartopy
ln -s feature_creation_scripts/iceshelves/driver.bash
./driver.bash
```
