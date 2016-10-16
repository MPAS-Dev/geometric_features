#!/usr/bin/env python
"""
This script creates 6 major ocean basins.  No arguments are required. The
optional --plot flag can be used to produce plots of each basin.
"""
import os
import os.path
import subprocess
from optparse import OptionParser

def spcall(args): #{{{
    return subprocess.check_call(args, env=os.environ.copy()) #}}}


def build_basins(): #{{{
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
    for oceanName in ['Atlantic', 'Pacific', 'Indian', 'Arctic', 'Southern_Ocean',
                      'Mediterranean']:

        tag = '%s_Basin'%oceanName

        print " * merging features to make %s Basin"%oceanName
        spcall(['./merge_features.py', '-d', 'ocean/region', '-t', tag,
                '-o', tempSeparateBasinFileName])

        #merge the the features into a single file
        print " * combining features into single feature named %s_Basin"%oceanName
        spcall(['./combine_features.py', '-f', tempSeparateBasinFileName,
                '-n', '%s_Basin'%oceanName,
                '-o', tempCombinedBasinFileName])

        if(options.plot):
            spcall(['./plot_features.py', '-f', tempCombinedBasinFileName,
                   '-o', '%s_Basin.png'%oceanName, '-m', 'cyl'])

        spcall(['./merge_features.py', '-f', tempCombinedBasinFileName,
                '-o', basinFileName])

        # remove temp files
        for fileName in [tempSeparateBasinFileName, tempCombinedBasinFileName]:
            os.remove(fileName)


    spcall(['./set_group_name.py', '-f', basinFileName,
            '-g', basinGroupName])

    if(options.plot):
        spcall(['./plot_features.py', '-f', basinFileName,
               '-o', 'oceanBasins.png', '-m', 'cyl']) #}}}


def build_MOC_basins(): #{{{
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

    # remove old files so we don't unintentionally append features
    for fileName in [MOCFileName, tempSeparateBasinFileName,
                     tempCombinedBasinFileName, tempMOCFileName]:
        if os.path.exists(fileName):
            os.remove(fileName)


    # build MOC basins
    for basinName in MOCSubBasins:

        imageName =  '%s_MOC.png'%basinName

        MOCMaskFileName = 'ocean/region/MOC_mask_%s/region.geojson' \
            %  MOCSouthernBoundary[basinName]

        print " * merging features to make %s Basin"%basinName

        for oceanName in MOCSubBasins[basinName]:
            spcall(['./merge_features.py', '-d', 'ocean/region',
                    '-t', '%s_Basin'%oceanName,
                    '-o', tempSeparateBasinFileName])

        #merge the the features into a single file
        print " * combining features into single feature named %s_MOC"%basinName
        spcall(['./combine_features.py', '-f', tempSeparateBasinFileName,
                '-n', '%s_MOC'%basinName,
                '-o', tempCombinedBasinFileName])

        print " * masking out features south of MOC region"
        spcall(['./difference_features.py', '-f', tempCombinedBasinFileName,
                '-m', MOCMaskFileName,
                '-o', tempMOCFileName])

        spcall(['./merge_features.py', '-f', tempMOCFileName,
                '-o', MOCFileName])

        if options.plot:
            spcall(['./plot_features.py', '-f', tempMOCFileName, '-o', imageName,
                    '-m', 'cyl'])

        # remove temp files
        for fileName in [tempSeparateBasinFileName, tempCombinedBasinFileName,
                         tempMOCFileName]:
            os.remove(fileName)

    spcall(['./set_group_name.py', '-f', MOCFileName,
            '-g', MOCGroupName])

    if options.plot:
        spcall(['./plot_features.py', '-f', MOCFileName,
                '-o', 'MOCBasins.png', '-m', 'cyl'])

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

build_basins()
build_MOC_basins()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
