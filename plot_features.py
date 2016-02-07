#!/usr/bin/env python
"""
This script plots a file containing multiple features onto a basemap using
matplotlib's basemap.

It requires basemap: http://matplotlib.org/basemap/

The -f flag is used to pass in a features file that will be plotted, and the -o
flag can optionally be used to specify the name of the image that will be
generated.  If more than one map type is used, the name of the map type will
be appended to the image name.  The option -m flag can be used to specify a 
comma-separated list of map types to be plotted.  If no map type is specified, 
all maps are used.  Possible map types are 'ortho', 'aeqd', 'eck4', 'cyl',
'merc', 'vandg', 'mill', 'mill2', 'robin', 'robin2', 'hammer', 'northpole', 
'southpole', 'atlantic', 'pacific', 'americas', 'asia'

Authors: Phillip J. Wolfram, Doug Jacobsen, Xylar Asay-Davis
Last Modified: 02/07/2016
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import os.path
from matplotlib.patches import Polygon

def plot_base(maptype): #{{{
    if maptype == 'ortho':
        map = Basemap(projection='ortho', lat_0=45, lon_0=-100, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'aeqd':
        map = Basemap(projection='aeqd', lat_0=0, lon_0=0, resolution='l')
        map.drawparallels(np.arange(-80,81,20))
        map.drawmeridians(np.arange(0,360,60))
    elif maptype == 'eck4':
        map = Basemap(projection='eck4',lon_0=0, resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'cyl':
        map = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180, resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'merc':
        map = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,lat_ts=20, resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'vandg':
        map = Basemap(projection='vandg',lon_0=0,resolution='l')
        map.drawparallels(np.arange(-80,81,20))
        map.drawmeridians(np.arange(0,360,60))
    elif maptype == 'mill':
        map = Basemap(llcrnrlon=0,llcrnrlat=-90,urcrnrlon=360,urcrnrlat=90,projection='mill', resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'mill2':
        map = Basemap(llcrnrlon=-180,llcrnrlat=-90,urcrnrlon=180,urcrnrlat=90,projection='mill', resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'robin':
        map = Basemap(projection='robin',lon_0=0,lat_0=0, resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'robin2':
        map = Basemap(projection='robin',lon_0=180,lat_0=0, resolution='l')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'hammer':
        map = Basemap(projection='hammer',lon_0=0, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'northpole':
        map = Basemap(projection='ortho', lat_0=90, lon_0=-180, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'southpole':
        map = Basemap(projection='ortho', lat_0=-90, lon_0=0, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'atlantic':
        map = Basemap(projection='ortho', lat_0=0, lon_0=0, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'pacific':
        map = Basemap(projection='ortho', lat_0=0, lon_0=-180, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'americas':
        map = Basemap(projection='ortho', lat_0=0, lon_0=-90, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'asia':
        map = Basemap(projection='ortho', lat_0=0, lon_0=90, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    else:
        raise NameError("Didn't select a valid maptype!")

    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='#e0e0e0', lake_color='white')
    map.drawmapboundary(fill_color='white')
    return map #}}}

def divide_poly_segments(points):
    inPoints = np.asarray(points)
    minDist = 1.0 # one-degree segments
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
        
    return outPoints

def plot_poly(mapInfo, points, color, filled=True):
    points = divide_poly_segments(points)
    
    for mapIndex in range(len(mapInfo)):
        (mapType, map, plotFileName, fig, offsets, supportsFill) = mapInfo[mapIndex]
        plt.figure(fig.number) 
        for offset in offsets:
            lon = points[:,0]+offset
            lat = points[:,1]
            if(mapType == 'robin2'):
                mask = np.logical_or(lon < 0.,lon > 360.)
                lon[mask] = np.nan
                lon[mask] = np.nan

            (x, y) = map(lon, lat)
                
            mask = x == 1e30
            x[mask] = np.nan
            y[mask] = np.nan
            if(filled and supportsFill):
                xy = zip(x,y)
                poly = Polygon( xy, facecolor=color, alpha=0.4)
                plt.gca().add_patch(poly)
            map.plot(x, y, linewidth=2.0, color=color)
  
def plot_point(mapInfo, points, marker, color):
    points = np.asarray(points)
    
    for mapIndex in range(len(mapInfo)):
        (mapType, map, plotFileName, fig, offsets, supportsFill) = mapInfo[mapIndex]
        plt.figure(fig.number) 
        for offset in offsets:
            (x, y) = map(points[:,0] + offset, points[:,1])
            map.plot(x, y, marker, markersize=20, color=color)

def plot_features_file(featurefile, mapInfo):
    
    # open up the database
    with open(featurefile) as f:
        featuredat = json.load(f)

    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
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
    for mapIndex in range(len(mapInfo)):
        (mapType, map, plotFileName, fig, offsets, supportsFill) = mapInfo[mapIndex]
        print 'saving ' + plotFileName
        plt.figure(mapIndex+1) 
        plt.savefig(plotFileName)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--features_file", dest="features_file", help="Feature file to plot", metavar="FILE", required=True)
    parser.add_argument("-o", "--features_plot", dest="features_plotname", help="Feature plot filename", metavar="FILE")
    parser.add_argument("-m", "--map_type", dest="map_type", help="The map type on which to project", metavar="FILE")

    args = parser.parse_args()


    if not args.map_type:
        mapTypes = ['ortho', 'aeqd', 'eck4', 'cyl',
                    'merc', 'vandg', 'mill', 'mill2',
                    'robin', 'robin2', 'hammer', 'northpole', 'southpole',
                    'atlantic','pacific', 'americas', 'asia']
    else:
        mapTypes = args.map_type.split(',')

    if not args.features_plotname:
        args.features_plotname = os.path.splitext(args.features_file)[0] + '.png'


    mapInfo = []
    for mapType in mapTypes:
        print 'plot type: %s'%mapType
        fig = plt.figure(figsize=(16,12),dpi=100)
        map = plot_base(mapType)
        if mapType in ['mill', 'robin2']:
            offsets = [0., 360.]
        else:
            offsets = [0.]
        supportsFill = mapType in ['eck4', 'cyl','vandg', 'mill', 'mill2','robin', 'hammer']
        if(len(mapTypes) == 1):
            plotFileName = args.features_plotname
        else:
            plotFileName = '%s_%s.png'%(os.path.splitext(args.features_plotname)[0],mapType)
        mapInfo.append((mapType, map, plotFileName, fig, offsets, supportsFill))
        
    plot_features_file(args.features_file, mapInfo)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
