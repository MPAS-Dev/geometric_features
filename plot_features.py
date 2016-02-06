#!/usr/bin/env python
"""
This script plots a file containing multiple features onto a basemap using
matplotlib's basemap.

It requires basemap: http://matplotlib.org/basemap/

The -r flag is used to pass in a features file that will be plotted, and the -o
flag can optionally be used to specify the name of the image that will be
generated.

Author: Phillip J. Wolfram
Date: 08/25/2015
"""

import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic

def plot_base(maptype): #{{{
    if maptype == 'ortho':
        map = Basemap(projection='ortho', lat_0=45, lon_0=-100, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'aeqd':
        map = Basemap(projection='aeqd', lat_0=0, lon_0=0)
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'eck4':
        map = Basemap(projection='eck4',lon_0=0)
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'cyl':
        map = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,llcrnrlon=-180,urcrnrlon=180)
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'merc':
        map = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,llcrnrlon=-180,urcrnrlon=180,lat_ts=20)
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'vandg':
        map = Basemap(projection='vandg',lon_0=0,resolution='c')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'mill':
        map = Basemap(llcrnrlon=0,llcrnrlat=-90,urcrnrlon=360,urcrnrlat=90,projection='mill')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'mill2':
        map = Basemap(llcrnrlon=-180,llcrnrlat=-90,urcrnrlon=180,urcrnrlat=90,projection='mill')
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'robin':
        map = Basemap(projection='robin',lon_0=0,lat_0=0)
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'robin2':
        map = Basemap(projection='robin',lon_0=180,lat_0=0)
        map.drawparallels(np.arange(-80,81,20),labels=[1,1,0,0])
        map.drawmeridians(np.arange(0,360,60),labels=[0,0,0,1])
    elif maptype == 'hammer':
        map = Basemap(projection='hammer',lon_0=180)
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'northpole':
        map = Basemap(projection='ortho', lat_0=90, lon_0=-100, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'southpole':
        map = Basemap(projection='ortho', lat_0=-90, lon_0=-100, resolution='l')
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
    elif maptype == 'europe':
        map = Basemap(projection='ortho', lat_0=0, lon_0=-90, resolution='l')
        map.drawmeridians(np.arange(0,360,30))
        map.drawparallels(np.arange(-90,90,30))
    elif maptype == 'northamerica':
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


def plot_features_file(featurefile, plotname):
    # open up the database
    with open(featurefile) as f:
        featuredat = json.load(f)

    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black']
    markers = ['o', 's', 'v', '^', '>', '<', '*', 'p', 'D', 'h']

    fig = plt.figure(figsize=(16,12),dpi=100)
    for anum, maptype in enumerate(['mill2','mill', 'northpole', 'southpole']):
        print 'plot type: %s'%maptype
        ax = fig.add_subplot(2,2,1+anum)
        feature_num = 0
        for feature in featuredat['features']:
            polytype = feature['geometry']['type']
            coords = feature['geometry']['coordinates']
            feature = feature['properties']['name']
            print '  feature: %s'%feature

            color_num = feature_num % len(colors)
            marker_num = feature_num % len(markers)

            map = plot_base(maptype)
            try:
                if polytype == 'MultiPolygon':
                    for poly in coords:
                        for shape in poly:
                            points = np.asarray(shape)
                            (x, y) = map(points[:,0], points[:,1])
                            map.plot(x, y, linewidth=2.0, color=colors[color_num])
                elif polytype == 'Polygon' or polytype == 'MultiLineString':
                    for poly in coords:
                        points = np.asarray(poly)
                        (x, y) = map(points[:,0], points[:,1])
                        map.plot(x, y, linewidth=2.0, color=colors[color_num])
                elif polytype == 'LineString':
                    points = np.asarray(coords)
                    # due to bug in basemap http://stackoverflow.com/questions/31839047/valueerror-in-python-basemap/32252594#32252594
                    lons = [points[0,0],points[0,0],points[1,0],points[1,0]]
                    lats = [points[0,1],points[0,1],points[1,1],points[1,1]]
                    (x, y) = map(lons, lats)
                    map.plot(x, y, linewidth=2.0, color=colors[color_num])
                elif polytype == 'Point':
                    points = np.asarray(coords)
                    (x, y) = map(points[:,0], points[:,1])
                    map.plot(x, y, markers[marker_num], markersize=20, color=colors[color_num])
                else:
                    assert False, 'Geometry %s not known.'%(polytype)
            except:
                print 'Error plotting %s for map type %s'%(feature, maptype)

            feature_num = feature_num + 1
    print 'saving ' + plotname
    plt.savefig(plotname)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--features_file", dest="features_file", help="Feature file to plot", metavar="FILE", required=True)
    parser.add_argument("-o", "--features_plot", dest="features_plotname", help="Feature plot filename", metavar="FILE")

    args = parser.parse_args()

    if not args.features_plotname:
        args.features_plotname = args.features_file.strip('.*') + '_plot.png'

    plot_features_file(args.features_file, args.features_plotname)

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
