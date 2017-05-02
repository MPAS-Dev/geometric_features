#!/usr/bin/env python

"""
This script creates the following ocean region groups:
i) OceanBasinRegionsGroup, which includes the Global Ocean as well as
   Atlantic, Pacific, Indian, Arctic, Southern Ocean, Equatorial
   (global 15S-15N), and Mediterranean basins;
ii) MOCBasinRegionGroup, which includes five regions used for computing the
    meridional overturning circulation (MOC) and meridional heat transport
    (MHT);
iii) NinoRegionGroups, which includes the Nino3, Nino4, and Nino3.4
    regions.

No arguments are required. The optional --plot flag
can be used to produce plots of each basin or region.

Author: Xylar Asay-Davis
Last Modified: 02/15/2017
"""

import os
import os.path
import subprocess
from optparse import OptionParser
import json
from collections import defaultdict

from utils.feature_write_utils import write_all_features
from utils.feature_test_utils import feature_already_exists

import shapely.geometry
import shapely.ops


def spcall(args):  # {{{
    return subprocess.check_call(args, env=os.environ.copy())  # }}}


def remove_small_polygons(inFileName, outFileName, minArea):  # {{{

    features = defaultdict(list)

    if os.path.exists(outFileName):
        try:
            with open(outFileName) as f:
                appended_file = json.load(f)
                for feature in appended_file['features']:
                    features['features'].append(feature)
                del appended_file
        except:
            pass

    inFeatures = defaultdict(list)

    try:
        with open(inFileName) as f:
            feature_file = json.load(f)

        for feature in feature_file['features']:
            inFeatures['features'].append(feature)

        del feature_file
    except:
        print "Error parsing geojson file: %s" % (inFileName)
        raise

    for feature in inFeatures['features']:
        name = feature['properties']['name']
        if feature_already_exists(features, feature):
            print "Warning: feature %s already in features.geojson.  " \
                  "Skipping..." % name
            continue
        geom = feature['geometry']
        if geom['type'] not in ['Polygon', 'MultiPolygon']:
            # no area to check, so just add it
            features['features'].append(feature)
        else:
            add = False
            featureShape = shapely.geometry.shape(geom)
            if featureShape.type == 'Polygon':
                if featureShape.area > minArea:
                    add = True
            else:
                # a MultiPolygon
                outPolygons = []
                for polygon in featureShape:
                    if polygon.area > minArea:
                        outPolygons.append(polygon)
                if len(outPolygons) > 0:
                    outShape = shapely.ops.cascaded_union(outPolygons)
                    feature['geometry'] = shapely.geometry.mapping(outShape)
                    add = True
        if add:
            features['features'].append(feature)
        else:
            print "%s has been removed." % name

    write_all_features(features, outFileName, indent=4)  # }}}


def build_ocean_basins():  # {{{
    basinGroupName = 'OceanBasinRegionsGroup'
    basinFileName = 'oceanBasins.geojson'

    # temp file names that we delete later
    tempSeparateBasinFileName = 'temp_separate_basins.geojson'
    tempCombinedBasinFileName = 'temp_combined_basins.geojson'

    # remove old files so we don't unintentionally append features
    for fileName in [basinFileName,
                     tempSeparateBasinFileName,
                     tempCombinedBasinFileName]:
        if os.path.exists(fileName):
            os.remove(fileName)

    # build ocean basins from regions with the appropriate tags
    for oceanName in ['Atlantic', 'Pacific', 'Indian', 'Arctic',
                      'Southern_Ocean', 'Mediterranean']:

        tag = '%s_Basin' % oceanName

        print " * merging features to make %s Basin" % oceanName
        spcall(['./merge_features.py', '-d', 'ocean/region', '-t', tag,
                '-o', tempSeparateBasinFileName])

        # merge the the features into a single file
        print " * combining features into single feature named %s_Basin" \
            % oceanName
        spcall(['./combine_features.py', '-f', tempSeparateBasinFileName,
                '-n', '%s_Basin' % oceanName,
                '-o', tempCombinedBasinFileName])

        if(options.plot):
            spcall(['./plot_features.py', '-f', tempCombinedBasinFileName,
                   '-o', '%s_Basin.png' % oceanName, '-m', 'cyl'])

        spcall(['./merge_features.py', '-f', tempCombinedBasinFileName,
                '-o', basinFileName])

        # remove temp files
        for fileName in [tempSeparateBasinFileName, tempCombinedBasinFileName]:
            os.remove(fileName)

    # add the global ocean
    spcall(['./merge_features.py',
            '-f', 'ocean/region/Global_Ocean/region.geojson',
            '-o', basinFileName])

    # add the global ocean between 65S and 65S
    spcall(['./merge_features.py',
            '-f', 'ocean/region/Global_Ocean_65N_to_65S/region.geojson',
            '-o', basinFileName])

    # add the equatorial region, which does not correspond to an ocean basin
    spcall(['./merge_features.py',
            '-f', 'ocean/region/Global_Ocean_15S_to_15N/region.geojson',
            '-o', basinFileName])

    spcall(['./set_group_name.py', '-f', basinFileName,
            '-g', basinGroupName])

    if(options.plot):
        spcall(['./plot_features.py', '-f', basinFileName,
               '-o', 'oceanBasins.png', '-m', 'cyl'])  # }}}


def build_MOC_basins():  # {{{
    MOCFileName = 'MOCBasins.geojson'
    MOCGroupName = 'MOCBasinRegionsGroup'

    MOCSubBasins = {'Atlantic': ['Atlantic', 'Mediterranean'],
                    'IndoPacific': ['Pacific', 'Indian'],
                    'Pacific': ['Pacific'],
                    'Indian': ['Indian']}

    MOCSouthernBoundary = {'Atlantic': '34S',
                           'IndoPacific': '34S',
                           'Pacific': '6S',
                           'Indian': '6S'}

    # temp file names that we delete later
    tempSeparateBasinFileName = 'temp_separate_basins.geojson'
    tempCombinedBasinFileName = 'temp_combined_basins.geojson'
    tempMOCFileName = 'temp_MOC.geojson'
    tempMOCLargePolygonsFileName = 'temp_MOC_large_polys.geojson'

    # remove old files so we don't unintentionally append features
    for fileName in [MOCFileName,
                     tempSeparateBasinFileName,
                     tempCombinedBasinFileName,
                     tempMOCFileName,
                     tempMOCLargePolygonsFileName]:
        if os.path.exists(fileName):
            os.remove(fileName)

    # build MOC basins
    for basinName in MOCSubBasins:

        imageName = '%s_MOC.png' % basinName

        MOCMaskFileName = 'ocean/region/MOC_mask_%s/region.geojson' \
            % MOCSouthernBoundary[basinName]

        print " * merging features to make %s Basin" % basinName

        for oceanName in MOCSubBasins[basinName]:
            spcall(['./merge_features.py', '-d', 'ocean/region',
                    '-t', '%s_Basin' % oceanName,
                    '-o', tempSeparateBasinFileName])

        # merge the the features into a single file
        print " * combining features into single feature named %s_MOC" \
            % basinName
        spcall(['./combine_features.py', '-f', tempSeparateBasinFileName,
                '-n', '%s_MOC' % basinName,
                '-o', tempCombinedBasinFileName])

        print " * masking out features south of MOC region"
        spcall(['./difference_features.py', '-f', tempCombinedBasinFileName,
                '-m', MOCMaskFileName,
                '-o', tempMOCFileName])

        # remove various small polygons that are not part of the main MOC
        # basin shapes.  Most are tiny but one below Australia is about 20
        # deg^2, so make the threshold 100 deg^2 to be on the safe side.
        remove_small_polygons(tempMOCFileName, tempMOCLargePolygonsFileName,
                              minArea=100.)

        spcall(['./merge_features.py', '-f', tempMOCLargePolygonsFileName,
                '-o', MOCFileName])

        if options.plot:
            spcall(['./plot_features.py', '-f', tempMOCLargePolygonsFileName,
                    '-o', imageName, '-m', 'cyl'])

        # remove temp files
        for fileName in [tempSeparateBasinFileName, tempCombinedBasinFileName,
                         tempMOCFileName, tempMOCLargePolygonsFileName]:
            os.remove(fileName)

    spcall(['./set_group_name.py', '-f', MOCFileName,
            '-g', MOCGroupName])

    if options.plot:
        spcall(['./plot_features.py', '-f', MOCFileName,
                '-o', 'MOCBasins.png', '-m', 'cyl'])  # }}}


def build_Nino_regions():  # {{{
    NinoFileName = 'NinoRegions.geojson'
    NinoGroupName = 'NinoRegionsGroup'

    if os.path.exists(NinoFileName):
        os.remove(NinoFileName)

    # build Nino basins
    spcall(['./merge_features.py', '-d', 'ocean/region',
            '-t', 'Nino',
            '-o', NinoFileName])

    spcall(['./set_group_name.py', '-f', NinoFileName,
            '-g', NinoGroupName])

    if options.plot:
        spcall(['./plot_features.py', '-f', NinoFileName,
                '-o', 'NinoRegions.png', '-m', 'cyl'])  # }}}

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

build_ocean_basins()
build_MOC_basins()
build_Nino_regions()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
