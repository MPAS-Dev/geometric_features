#!/usr/bin/env python

# in addition to the packages in geometric_features, this script requires:
#   * ismip6-antarctic-ocean-forcing
#   * xarray
#   * pyproj

import os
import numpy
import xarray
import pyproj
import matplotlib.pyplot as plt
from importlib.resources import path
from configparser import ConfigParser, ExtendedInterpolation

from ismip6_ocean_forcing.bedmap2 import bedmap2_to_ismip6_grid
from ismip6_ocean_forcing.imbie import make_imbie_masks

from geometric_features import GeometricFeatures, FeatureCollection
from geometric_features.utils import write_feature_names_and_tags


def basin_masks_to_features():

    # from https://github.com/ismip/ismip6-antarctic-ocean-forcing/blob/4e80cf776d36ff05361158b45e26e74f07c029c5/ismip6_ocean_forcing/imbie/make_imbie_masks.py#L27-L42
    basins = {'A-Ap': ['A-Ap'],
              'Ap-B': ['Ap-B'],
              'B-C': ['B-C'],
              'C-Cp': ['C-Cp'],
              'Cp-D': ['Cp-D'],
              'D-Dp': ['D-Dp'],
              'Dp-E': ['Dp-E'],
              'E-F': ['E-Ep', 'Ep-F'],
              'F-G': ['F-G'],
              'G-H': ['G-H'],
              'H-Hp': ['H-Hp'],
              'Hp-I': ['Hp-I'],
              'I-Ipp': ['I-Ipp'],
              'Ipp-J': ['Ipp-J'],
              'J-K': ['J-Jpp', 'Jpp-K'],
              'K-A': ['K-A']}

    ds = xarray.open_dataset('imbie/basinNumbers_8km.nc')
    da_basin_number = ds.basinNumber
    x = ds.x
    y = ds.y

    projection = pyproj.Proj(
        '+proj=stere +lat_0=-90 +lat_ts=-71 +lon_0=0  +k=1 +x_0=0 +y_0=0 '
        '+datum=WGS84 +units=m +no_defs')

    basin_count = da_basin_number.max().values + 1

    fc = FeatureCollection()

    for basin_number in range(basin_count):
        mask = da_basin_number == basin_number
        field = xarray.ones_like(da_basin_number).where(mask, other=0.)
        field = field.values
        # boundaries are not in any basin so we get square edges
        field[0, :] = 0.
        field[-1, :] = 0.
        field[:, 0] = 0.
        field[:, -1] = 0.

        basin_name = list(basins)[basin_number]
        imbie_basins = list(basins.values())[basin_number]
        imbie_tags = '; '.join([f'IMBIE_{basin}' for basin in imbie_basins])
        tags = f'ISMIP6_Basin; {imbie_tags}'

        # add properties
        properties = dict(name=f'ISMIP6 Basin {basin_name}',
                          component='landice',
                          tags=tags,
                          author='Xylar Asay-Davis',
                          object='region')

        geometry = dict()
        # add geometry
        plt.figure(1)
        cs = plt.contour(x.values, y.values, field, [0.5])
        # extract the contour as paths
        contours = cs.collections[0].get_paths()

        # convert the paths to lat/lon
        for contour in contours:
            lon, lat = projection(contour.vertices[:, 0],
                                  contour.vertices[:, 1],
                                  inverse=True)
            contour.vertices[:, 0] = lon
            contour.vertices[:, 1] = lat
            # repeat the first entry as the last
            contour.vertices = numpy.append(contour.vertices,
                                            contour.vertices[0:1, :],
                                            axis=0)

        # extract the contour as a polygon or multipolygon
        if len(contours) == 1:
            # create a Polygon
            geometry['type'] = 'Polygon'
            geometry['coordinates'] = [contours[0].vertices.tolist()]
        else:
            # create a MultiPolygon
            geometry['type'] = 'MultiPolygon'
            polys = []
            for index in range(len(contours)):
                polys.append([contours[index].vertices.tolist()])
            geometry['coordinates'] = polys

        fc.add_feature(dict(type='feature', properties=properties,
                            geometry=geometry))
        plt.close()

    fc.to_geojson('features_before_fix.geojson')

    fc = fc.fix_antimeridian()
    fc.plot(projection='southpole')
    plt.savefig(f'ISMIP6_basins.png')

    for feature in fc.features:
        fc_plot = FeatureCollection()
        fc_plot.add_feature(feature)
        fc_plot.plot(projection='southpole')
        plt.savefig(f'{feature["properties"]["name"].replace(" ", "_")}.png')

    fc.to_geojson('features_after_fix.geojson')

    # make a geometric features object that points to geometry in the local
    # cache in ./geometric_data
    gf = GeometricFeatures(cacheLocation='../../geometric_data')

    # split the feature collection into individual features within
    # ./geometric_data
    gf.split(fc)

    # write a file features_and_tags.json with features and tags from the cache
    write_feature_names_and_tags(gf.cacheLocation)

    # move features_and_tags.json into geometric_features to replace the old
    # manifest
    os.rename('features_and_tags.json',
              '../../geometric_features/features_and_tags.json')


def main():
    config = ConfigParser(interpolation=ExtendedInterpolation())
    with path('ismip6_ocean_forcing', 'default.cfg') as default_config:
        config.read(str(default_config))

    bedmap2_to_ismip6_grid(config)
    make_imbie_masks(config)

    basin_masks_to_features()


if __name__ == '__main__':
    main()
