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
Last Modified: 02/08/2016
"""

import os.path
import json
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs
import cartopy.feature

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

def divide_poly_segments(points): #{{{

    inPoints = np.asarray(points)
    minDist = 4.0 # 4-degree segments
    dLon = inPoints[1:,0] - inPoints[0:-1,0]
    dLat = inPoints[1:,1] - inPoints[0:-1,1]
    dist = np.sqrt(dLon**2 + dLat**2)

    longSegmentIndices = np.nonzero(dist > minDist)[0]
    if(len(longSegmentIndices) == 0):
        return inPoints

    # start with all points up to the first long segiment
    outPoints = inPoints[0:longSegmentIndices[0],:]
    for index in range(len(longSegmentIndices)):
        segIndex = longSegmentIndices[index]
        newPointCount = int(dist[segIndex]/minDist)+2
        newPoints = np.zeros((newPointCount, 2))
        newPoints[:,0] = np.linspace(inPoints[segIndex,0], inPoints[segIndex+1,0], newPointCount)
        newPoints[:,1] = np.linspace(inPoints[segIndex,1], inPoints[segIndex+1,1], newPointCount)
        outPoints = np.append(outPoints, newPoints[0:-1,:], axis=0)

        # now add all the points up to the next long segment, or remaining points
        # if there are no more long segments
        if(index+1 < len(longSegmentIndices)):
            endIndex = longSegmentIndices[index+1]
        else:
            endIndex = inPoints.shape[0]
        outPoints = np.append(outPoints, inPoints[segIndex+1:endIndex,:], axis=0)

    return outPoints #}}}

def plot_poly(mapInfo, points, color, filled=True): #{{{

    points = divide_poly_segments(points)

    refProjection = cartopy.crs.PlateCarree()

    for mapType in mapInfo:
        (ax, projection, plotFileName, fig) = mapInfo[mapType]
        x = points[:,0]
        y = points[:,1]
        ax.fill(x, y, transform=refProjection, color=color, alpha=0.4, linewidth=2.0, zorder=3)

    return #}}}

def plot_point(mapInfo, points, marker, color): #{{{

    points = np.asarray(points)

    refProjection = cartopy.crs.PlateCarree()

    for mapType in mapInfo:
        (ax, projection, plotFileName, fig) = mapInfo[mapType]
        ax.plot(points[:,0], points[:,1], marker = marker, transform=refProjection, color=color, zorder=5)

    return #}}}

def plot_features_file(featurefile, mapInfo): #{{{

    # open up the database
    with open(featurefile) as f:
        featuredat = json.load(f)

    # use colorbrewer qualitative 7 data class colors, "7-class Accent": http://colorbrewer2.org/
    colors = ['#7fc97f' ,'#beaed4', '#fdc086', '#ffff99','#386cb0','#f0027f','#bf5b17']
    markers = ['o', 's', 'v', '^', '>', '<', '*', 'p', 'D', 'h']

    feature_num = 0

    for feature in featuredat['features']:
        polytype = feature['geometry']['type']
        coords = feature['geometry']['coordinates']
        feature = feature['properties']['name']
        print '  feature: %s'%feature

        color_num = feature_num % len(colors)
        marker_num = feature_num % len(markers)

        try:
            if polytype == 'MultiPolygon':
                for poly in coords:
                    for shape in poly:
                        plot_poly(mapInfo,shape,colors[color_num])
            elif polytype == 'Polygon' or polytype == 'MultiLineString':
                for poly in coords:
                    plot_poly(mapInfo,poly,colors[color_num])
            elif polytype == 'LineString':
                plot_poly(mapInfo,coords,colors[color_num],filled=False)
            elif polytype == 'Point':
                plot_point(mapInfo,coords,markers[marker_num],colors[color_num])
            else:
                assert False, 'Geometry %s not known.'%(polytype)
        except:
            print 'Error plotting %s'%(feature)

        feature_num = feature_num + 1

    for mapType in mapInfo:
        (ax, projection, plotFileName, fig) = mapInfo[mapType]
        print 'saving ' + plotFileName
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
