#!/bin/bash

# This is the main driver script.  See README.md for details.

rm -f iceshelves.geojson

# convert Bedmap2 data to NetCDF format
./feature_creation_scripts/iceshelves/bedmap2_to_netcdf.py

# Compute the distance from each point to the closest ice shelf
./feature_creation_scripts/iceshelves/write_iceshelf_distance.py

# Regrid the Measures velocity data to the Bedmap2 grid
./feature_creation_scripts/iceshelves/ice_vel_to_bedmap2.py

# Plot streamlines for separating basins on ice shelves
./feature_creation_scripts/iceshelves/plot_streamline.py

# Write out a map of ice-shelf numbers
ln -sfn feature_creation_scripts/iceshelves/ice_shelf_lat_lon.csv
./feature_creation_scripts/iceshelves/write_iceshelf_numbers.py

# Create combine the IMBIE basin features
./driver_scripts/setup_antarctic_basins.py

# Make images for each IMBIE basin
./feature_creation_scripts/iceshelves/write_basin_images.py

# Find the distance to each basin
./feature_creation_scripts/iceshelves/write_basin_distances.py

# Write out a map of basin numbers
./feature_creation_scripts/iceshelves/write_basin_numbers.py

# Find which shelves overlap with which IMBIE basins
./feature_creation_scripts/iceshelves/write_expanded_overlaps.py

# Create features for each ice shelf in each basin
./feature_creation_scripts/iceshelves/write_iceshelf_features.py

# Fix features that cross the antemeridian (+/- 180)
./fix_features_at_antimeridian.py -f iceshelves_before_fix.geojson \
    -o iceshelves.geojson
rm -f iceshelves_before_fix.geojson

# Plot the features
./plot_features.py -f iceshelves.geojson -m southpole

# To split the features, uncomment the following
# ./split_features -f iceShelfes.geojson
