#!/usr/bin/env python

import json
import sys

import matplotlib
import numpy
from descartes import PolygonPatch
from netCDF4 import Dataset
from shapely.geometry import shape

matplotlib.use('Agg')
import os.path

import matplotlib.pyplot as plt
from polar import toPolar


def makePolarBasins(basinData):
    basinShapes = []
    for feature in basinData['features']:
        basinGeom = feature['geometry']
        coords = basinGeom['coordinates']
        newCoords = []
        if(basinGeom['type'] == 'Polygon'):
            for subpoly in coords:
                newCoords.append(toPolar(numpy.array(subpoly)).tolist())
        elif(basinGeom['type'] == 'MultiPolygon'):
            for poly in coords:
                newPoly = []
                for subpoly in poly:
                    newPoly.append(toPolar(numpy.array(subpoly)).tolist())
                newCoords.append(newPoly)
        basinGeom['coordinates'] = newCoords
        basinShape = shape(basinGeom)
        basinShapes.append(basinShape)
    return basinShapes


def writeBasinImage(basinShape, name):
    my_dpi = 600
    fig = plt.figure(figsize=(nx/float(my_dpi), ny/float(my_dpi)), dpi=my_dpi)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    plt.axis('off')

    color = 'black'

    if basinShape.geom_type == 'Polygon':
        ax.add_patch(PolygonPatch(basinShape, fc=color, ec=color, linewidth=0))
    elif basinShape.geom_type == 'MultiPolygon':
        for poly in basinShape:
            ax.add_patch(PolygonPatch(poly, fc=color, ec=color, linewidth=0))

    plt.xlim([-dx*0.5*(nx+1), dx*0.5*(nx+1)])
    plt.ylim([-dx*0.5*(ny+1), dx*0.5*(ny+1)])
    # plt.show()
    fig.canvas.draw()
    plt.savefig('basins/{}.png'.format(name), dpi=my_dpi)
    plt.close()


inFileName = 'Bedmap2_ice_shelf_distance.nc'
basinFileName = 'Antarctic_Basins.geojson'

if basinFileName:
    if not os.path.exists(basinFileName):
        print 'The file {} does not exist.'.format(basinFileName)
        sys.exit(1)

with open(basinFileName) as f:
    basinData = json.load(f)

basinShapes = makePolarBasins(basinData)

inFile = Dataset(inFileName, 'r')

X = inFile.variables['X'][:, :]
Y = inFile.variables['Y'][:, :]

inFile.close()

(ny, nx) = X.shape

dx = 1e3

try:
    os.makedirs('basins')
except OSError:
    pass

for index in range(len(basinShapes)):
    name = basinData['features'][index]['properties']['name']
    print name
    writeBasinImage(basinShapes[index], name)
