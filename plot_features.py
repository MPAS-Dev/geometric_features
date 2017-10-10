#!/usr/bin/env python
"""
This script plots a file containing multiple features onto a basemap using
cartopy.

It requires cartopy: http://scitools.org.uk/cartopy/docs/latest/index.html

The -f flag is used to pass in a features file that will be plotted, and the -o
flag can optionally be used to specify the name of the image that will be
generated.  If more than one map type is used, the name of the map type will
be appended to the image name.  The option -m flag can be used to specify a
comma-separated list of map types to be plotted.  If no map type is specified,
all maps are used.  Possible map types are 'cyl', 'merc', 'mill', 'mill2',
'moll', 'moll2', 'robin', 'robin2', 'ortho', 'northpole',
'southpole', 'atlantic', 'pacific', 'americas', 'asia'

Authors: Xylar Asay-Davis, Doug Jacobsen, Phillip J. Wolfram
Last Modified: 09/29/2016
"""

import os.path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs
import cartopy.feature
import shapely


def build_projections():  # {{{
    projections = {}
    projections['cyl'] = cartopy.crs.PlateCarree()
    projections['merc'] = cartopy.crs.Mercator()
    projections['mill'] = cartopy.crs.Miller()
    projections['mill2'] = cartopy.crs.Miller(central_longitude=180.)
    projections['moll'] = cartopy.crs.Mollweide()
    projections['moll2'] = cartopy.crs.Mollweide(central_longitude=180.)
    projections['robin'] = cartopy.crs.Robinson()
    projections['robin2'] = cartopy.crs.Robinson(central_longitude=180.)

    projections['ortho'] = cartopy.crs.Orthographic(central_longitude=-100.,
                                                    central_latitude=45.)
    projections['northpole'] = cartopy.crs.Orthographic(central_longitude=0.,
                                                        central_latitude=90.)
    projections['southpole'] = cartopy.crs.Orthographic(central_longitude=0.,
                                                        central_latitude=-90.)
    projections['atlantic'] = cartopy.crs.Orthographic(central_longitude=0.,
                                                       central_latitude=0.)
    projections['pacific'] = cartopy.crs.Orthographic(central_longitude=180.,
                                                      central_latitude=0.)
    projections['americas'] = cartopy.crs.Orthographic(central_longitude=-90.,
                                                       central_latitude=0.)
    projections['asia'] = cartopy.crs.Orthographic(central_longitude=90.,
                                                   central_latitude=0.)

    return projections  # }}}

def plot_base(mapType, projection):  # {{{

    ax = plt.axes(projection=projection)
    resolution = '50m'

    ax.add_feature(cartopy.feature.NaturalEarthFeature(
        'physical', 'land', resolution, edgecolor='face',
        facecolor=cartopy.feature.COLORS['land']), zorder=1)

    ax.add_feature(cartopy.feature.NaturalEarthFeature(
        'physical', 'coastline', resolution,
        edgecolor='black', facecolor='none'), zorder=2)

    draw_labels = mapType in ['merc', 'cyl']

    ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=draw_labels,
                 linewidth=0.5, color='gray', linestyle='--')

    if not draw_labels:
        plt.tight_layout()

    return (ax, projection)  # }}}


def subdivide_geom(geometry, geomtype, max_length):  # {{{

    def subdivide_line_string(lineString, periodic=False):  # {{{
        coords = list(lineString.coords)
        if periodic:
            # add periodic last entry
            coords.append(coords[0])

        outCoords = [coords[0]]
        for iVert in range(len(coords)-1):
            segment = shapely.geometry.LineString([coords[iVert],
                                                   coords[iVert+1]])
            if(segment.length < max_length):
                outCoords.append(coords[iVert+1])
            else:
                # we need to subdivide this segment
                subsegment_count = int(np.ceil(segment.length/max_length))
                for index in range(subsegment_count):
                    point = segment.interpolate(
                        float(index+1)/float(subsegment_count),
                        normalized=True)
                    outCoords.append(point.coords[0])

        if periodic:
            # remove the last entry
            outCoords.pop()
        return outCoords   # }}}

    if geomtype == 'LineString':
        newGeometry = shapely.geometry.LineString(
            subdivide_line_string(geometry))
    elif geomtype == 'MultiLineString':
        outStrings = [subdivide_line_string(inLineString) for inLineString
                      in geometry]
        newGeometry = shapely.geometry.MultiLineString(outStrings)
    elif geomtype == 'Polygon':
        exterior = subdivide_line_string(geometry.exterior, periodic=True)
        interiors = [subdivide_line_string(inLineString, periodic=True)
                     for inLineString in geometry.interiors]
        newGeometry = shapely.geometry.Polygon(exterior, interiors)
    elif geomtype == 'MultiPolygon':
        polygons = []
        for polygon in geometry:
            exterior = subdivide_line_string(polygon.exterior, periodic=True)
            interiors = [subdivide_line_string(inLineString, periodic=True)
                         for inLineString in polygon.interiors]
            polygons.append((exterior, interiors))

        newGeometry = shapely.geometry.MultiPolygon(polygons)
    elif geomtype == 'Point':
        newGeometry = geometry
    else:
        print "Warning: subdividing geometry type {} is not supported.".format(
            geomtype)
        newGeometry = geometry

    return newGeometry  # }}}


def plot_features_file(featurefile, mapInfo, max_length):  # {{{

    # open up the database
    with open(featurefile) as f:
        featuredat = json.load(f)

    # use colorbrewer qualitative 7 data class colors, "7-class Accent":
    # http://colorbrewer2.org/
    colors = ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0', '#f0027f',
              '#bf5b17']
    # markers = ['o', 's', 'v', '^', '>', '<', '*', 'p', 'D', 'h']

    feature_num = 0

    bounds = None

    for feature in featuredat['features']:
        geomtype = feature['geometry']['type']
        shape = shapely.geometry.shape(feature['geometry'])
        if(max_length > 0.0):
            shape = subdivide_geom(shape, geomtype, max_length)

        featurename = feature['properties']['name']
        print '  feature: {}'.format(featurename)

        refProjection = cartopy.crs.PlateCarree()

        color = colors[feature_num % len(colors)]
        # marker = markers[feature_num % len(markers)]

        if geomtype in ['Polygon', 'MultiPolygon']:
            props = {'linewidth': 2.0, 'edgecolor': color, 'alpha': 0.4,
                     'facecolor': color}
        elif geomtype in ['LineString', 'MultiLineString']:
            props = {'linewidth': 4.0, 'edgecolor': color, 'alpha': 1.,
                     'facecolor': 'none'}

        if bounds is None:
            bounds = list(shape.bounds)
        else:
            # expand the bounding box
            bounds[:2] = np.minimum(bounds[:2], shape.bounds[:2])
            bounds[2:] = np.maximum(bounds[2:], shape.bounds[2:])

        for mapType in mapInfo:
            (ax, projection, plotFileName, fig) = mapInfo[mapType]
            if geomtype == 'Point':
                ax.scatter(shape.coords[0][0], shape.coords[0][1], s=9,
                           transform=cartopy.crs.PlateCarree(), marker='o',
                           color='blue', edgecolor='blue')
            else:
                ax.add_geometries((shape,), crs=refProjection, **props)

        feature_num = feature_num + 1

    box = shapely.geometry.box(*bounds)
    if(max_length > 0.0):
        box = subdivide_geom(box, 'Polygon', max_length)

    for mapType in mapInfo:
        (ax, projection, plotFileName, fig) = mapInfo[mapType]
        print 'saving ' + plotFileName

        boxProjected = projection.project_geometry(box, src_crs=refProjection)
        try:
            x1, y1, x2, y2 = boxProjected.bounds
            ax.set_xlim([x1, x2])
            ax.set_ylim([y1, y2])
        except ValueError:
            print "Warning: bounding box could not be projected into " \
                "projection", mapType
            print "Defaulting to global bounds."
            ax.set_global()

        fig.savefig(plotFileName)

    return  # }}}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--features_file", dest="features_file",
                        help="Feature file to plot", metavar="FILE",
                        required=True)
    parser.add_argument("-o", "--features_plot", dest="features_plotname",
                        help="Feature plot filename", metavar="FILE")
    parser.add_argument("-m", "--map_type", dest="map_type",
                        help="The map type on which to project",
                        metavar="FILE")
    parser.add_argument("--max_length", dest="max_length", type=float,
                        default=4.0,
                        help="Maximum allowed segment length after subdivision"
                        " (0.0 indicates skip subdivision)")

    args = parser.parse_args()

    if not args.map_type:
        mapTypes = ['cyl', 'merc', 'mill', 'mill2',
                    'moll', 'moll2', 'robin', 'robin2', 'ortho', 'northpole',
                    'southpole', 'atlantic', 'pacific', 'americas', 'asia']
    else:
        mapTypes = args.map_type.split(',')

    if not args.features_plotname:
        args.features_plotname = os.path.splitext(args.features_file)[0] + \
            '.png'

    projections = build_projections()

    mapInfo = {}
    for mapType in mapTypes:
        print 'plot type: {}'.format(mapType)
        if mapType in ['cyl', 'merc', 'mill', 'mill2', 'moll', 'moll2',
                       'robin', 'robin2']:
            figsize = (12, 6)
        else:
            figsize = (12, 9)
        fig = plt.figure(figsize=figsize, dpi=200)
        (ax, projection) = plot_base(mapType, projections[mapType])

        if(len(mapTypes) == 1):
            plotFileName = args.features_plotname
        else:
            plotFileName = '{}_{}.png'.format(
                os.path.splitext(args.features_plotname)[0], mapType)
        mapInfo[mapType] = (ax, projection, plotFileName, fig)

    plot_features_file(args.features_file, mapInfo, max_length=args.max_length)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
