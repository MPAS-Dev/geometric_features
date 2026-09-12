#!/usr/bin/env python
"""
Download the BedMachine topography
----------------------------------
1. Go tohttps://nsidc.org/data/nsidc-0756/versions/3
2. Click on "HTTPS File System"
3. Log in or create and account.
5. Under "1970.01.01" choose "BedMachineAntarctica-v3.nc"

On Anvil or Chrysalis, BedMachine Antarctica v3 is available so create a
symlink with:
ln -s /lcrc/group/e3sm/public_html/mpas_standalonedata/mpas-ocean/bathymetry_database/BedMachineAntarctica-v3.nc
"""

import shutil

import matplotlib.pyplot as plt
import numpy as np
import shapely
import xarray as xr
from pyproj import Transformer

from geometric_features import GeometricFeatures, FeatureCollection
from geometric_features.feature_collection import _round_coords
from geometric_features.utils import write_feature_names_and_tags


def get_longest_contour(contour_value, author):

    def stereo_to_lon_lat(x, y):
        lat, lon = transformer.transform(x, y)
        return lon, lat

    with xr.open_dataset('BedMachineAntarctica-v3.nc') as ds:
        # the bed but only in the open ocean or under floating ice
        bed = xr.where(np.logical_or(ds.mask == 0, ds.mask == 3),
                       ds.bed, 0.).values
        x = ds.x.values
        y = ds.y.values

    # plot contours
    plt.figure()
    cs = plt.contour(x, y, bed, (contour_value,))
    paths = cs.allsegs[0]

    path_lengths = [len(paths[i]) for i in range(len(paths))]
    ilongest = np.argmax(path_lengths)

    v = paths[ilongest]
    x = v[:, 0]
    y = v[:, 1]

    # the starting index should be the point closest to -180 longitude
    mask = np.logical_and(y < 0., x <= 0.)
    indices = np.arange(x.shape[0])[mask]
    index = np.argmin(np.abs(x[mask]))
    first = indices[index]
    x = np.append(x[first:], x[:first+1])
    y = np.append(y[first:], y[:first+1])

    # Antarctic stereographic to lat/lon
    transformer = Transformer.from_crs('epsg:3031', 'epsg:4326')

    transect = shapely.geometry.LineString([(i[0], i[1]) for i in zip(x, y)])

    poly = shapely.geometry.Polygon([(i[0], i[1]) for i in zip(x, y)])

    # cut a tiny weged out to break the shape into 2 at the antimeridian
    epsilon = 1e-14
    minY = np.amin(y)
    wedge = shapely.geometry.Polygon([(epsilon, minY),
                                      (epsilon**2, -epsilon),
                                      (0, epsilon),
                                      (-epsilon**2, -epsilon),
                                      (-epsilon, minY),
                                      (epsilon, minY)])

    plt.figure()
    x, y = transect.xy
    plt.plot(x, y)

    difference = transect.difference(wedge)

    plt.figure()
    x, y = difference.xy
    plt.plot(x, y)

    transect_latlon = shapely.ops.transform(stereo_to_lon_lat, difference)

    difference = poly.difference(wedge)

    region_latlon = shapely.ops.transform(stereo_to_lon_lat, difference)

    plt.figure()
    x, y = transect_latlon.xy
    plt.plot(x, y)

    fc = FeatureCollection()

    isobath_name = f'{int(np.abs(contour_value))}m isobath'

    geometry = shapely.geometry.mapping(transect_latlon)
    # get rid of the wedge again by rounding the coordinates
    geometry['coordinates'] = _round_coords(geometry['coordinates'])

    fc.add_feature(
        {'type': 'Feature',
         'properties': {'name': f'Antarctic {isobath_name}',
                        'author': author,
                        'object': 'transect',
                        'component': 'ocean',
                        'tags': 'Antarctic'},
         'geometry': geometry})

    geometry = shapely.geometry.mapping(region_latlon)
    # get rid of the wedge again by rounding the coordinates
    geometry['coordinates'] = _round_coords(geometry['coordinates'])

    fc.add_feature(
        {'type': 'Feature',
         'properties': {'name': f'Antarctica within {isobath_name}',
                        'author': author,
                        'object': 'region',
                        'component': 'ocean',
                        'tags': 'Antarctic'},
         'geometry': geometry})

    return fc


def main():
    xylar = 'Xylar Asay-Davis'

    # make a geometric fieatures object that knows about the geometric data
    # cache up a couple of directories
    gf = GeometricFeatures('../../geometric_data')

    fc = get_longest_contour(contour_value=-1000., author=xylar)

    # "split" these features into individual files in the geometric data cache
    gf.split(fc)

    # update the database of feature names and tags
    write_feature_names_and_tags(gf.cacheLocation)
    # move the resulting file into place
    shutil.copyfile('features_and_tags.json',
                    '../../geometric_features/features_and_tags.json')

    plt.show()


if __name__ == '__main__':
    main()
