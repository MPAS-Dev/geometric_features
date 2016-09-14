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
Last Modified: 09/14/2016
"""

import os.path
import json
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs
import cartopy.feature
import shapely

def build_projections(): #{{{
    projections = {}
    projections['cyl'] = cartopy.crs.PlateCarree()
    projections['merc'] = cartopy.crs.Mercator()
    projections['mill'] = cartopy.crs.Miller()
    projections['mill2'] = cartopy.crs.Miller(central_longitude=180.)
    projections['moll'] = cartopy.crs.Mollweide()
    projections['moll2'] = cartopy.crs.Mollweide(central_longitude=180.)
    projections['robin'] = cartopy.crs.Robinson()
    projections['robin2'] = cartopy.crs.Robinson(central_longitude=180.)

    projections['ortho'] = cartopy.crs.Orthographic(central_longitude=-100., central_latitude=45.)
    projections['northpole'] = cartopy.crs.Orthographic(central_longitude=0., central_latitude=90.)
    projections['southpole'] = cartopy.crs.Orthographic(central_longitude=0., central_latitude=-90.)
    projections['atlantic'] = cartopy.crs.Orthographic(central_longitude=0., central_latitude=0.)
    projections['pacific'] = cartopy.crs.Orthographic(central_longitude=180., central_latitude=0.)
    projections['americas'] = cartopy.crs.Orthographic(central_longitude=-90., central_latitude=0.)
    projections['asia'] = cartopy.crs.Orthographic(central_longitude=90., central_latitude=0.)

    return projections #}}}

def plot_base(mapType, projection): #{{{

    ax = plt.axes(projection=projection)
    resolution = '50m'

    ax.add_feature(cartopy.feature.NaturalEarthFeature('physical', 'land', resolution,
                   edgecolor='face', facecolor=cartopy.feature.COLORS['land']), zorder=1)

    ax.add_feature(cartopy.feature.NaturalEarthFeature('physical', 'coastline', resolution,
                   edgecolor='black', facecolor='none'), zorder=2)

    draw_labels = mapType in ['merc','cyl']

    ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=draw_labels,
                 linewidth=0.5, color='gray', linestyle='--')

    if not draw_labels:
        plt.tight_layout()

    return (ax,projection) #}}}


def plot_features_file(featurefile, mapInfo): #{{{

    # open up the database
    with open(featurefile) as f:
        featuredat = json.load(f)

    # use colorbrewer qualitative 7 data class colors, "7-class Accent": http://colorbrewer2.org/
    colors = ['#7fc97f' ,'#beaed4', '#fdc086', '#ffff99','#386cb0','#f0027f','#bf5b17']
    markers = ['o', 's', 'v', '^', '>', '<', '*', 'p', 'D', 'h']

    feature_num = 0

    bounds = None

    for feature in featuredat['features']:
        geomtype = feature['geometry']['type']
        shape = shapely.geometry.shape(feature['geometry'])
        featurename = feature['properties']['name']
        print '  feature: %s'%featurename

        refProjection = cartopy.crs.PlateCarree()

        color = colors[feature_num % len(colors)]
        marker = markers[feature_num % len(markers)]

        props = {'linewidth':2.0, 'edgecolor':color}
        if geomtype in ['Polygon','MultiPolygon']:
            props['alpha'] = 0.4
            props['facecolor'] = color
        if geomtype in ['LineString','MultiLineString']:
            props['facecolor'] = 'none'
        if geomtype in ['Point']:
            props['marker'] = marker

        if bounds is None:
            bounds = list(shape.bounds)
        else:
            # expand the bounding box
            bounds[:2] = np.minimum(bounds[:2], shape.bounds[:2])
            bounds[2:] = np.maximum(bounds[2:], shape.bounds[2:])

        for mapType in mapInfo:
            (ax, projection, plotFileName, fig) = mapInfo[mapType]
            ax.add_geometries((shape,), crs=refProjection, **props)

        feature_num = feature_num + 1

    box = shapely.geometry.box(*bounds)

    for mapType in mapInfo:
        (ax, projection, plotFileName, fig) = mapInfo[mapType]
        print 'saving ' + plotFileName

        boxProjected = projection.project_geometry(box, src_crs=refProjection)
        try:
            x1, y1, x2, y2 = boxProjected.bounds
            ax.set_xlim([x1, x2])
            ax.set_ylim([y1, y2])
        except ValueError:
            print "Warning: bounding box could not be projected into projection", mapType
            print "Defaulting to global bounds."
            ax.set_global()

        fig.savefig(plotFileName)

    return #}}}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--features_file", dest="features_file", help="Feature file to plot", metavar="FILE", required=True)
    parser.add_argument("-o", "--features_plot", dest="features_plotname", help="Feature plot filename", metavar="FILE")
    parser.add_argument("-m", "--map_type", dest="map_type", help="The map type on which to project", metavar="FILE")

    args = parser.parse_args()


    if not args.map_type:
        mapTypes = ['cyl', 'merc', 'mill', 'mill2',
                    'moll', 'moll2', 'robin', 'robin2', 'ortho', 'northpole',
                    'southpole', 'atlantic', 'pacific', 'americas', 'asia']
    else:
        mapTypes = args.map_type.split(',')

    if not args.features_plotname:
        args.features_plotname = os.path.splitext(args.features_file)[0] + '.png'

    projections = build_projections()

    mapInfo = {}
    for mapType in mapTypes:
        print 'plot type: %s'%mapType
        fig = plt.figure(figsize=(16,12),dpi=100)
        (ax,projection) = plot_base(mapType,projections[mapType])

        if(len(mapTypes) == 1):
            plotFileName = args.features_plotname
        else:
            plotFileName = '%s_%s.png'%(os.path.splitext(args.features_plotname)[0],mapType)
        mapInfo[mapType] = (ax, projection, plotFileName, fig)

    plot_features_file(args.features_file, mapInfo)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
