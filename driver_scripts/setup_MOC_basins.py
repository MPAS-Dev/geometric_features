#!/usr/bin/env python
"""
This script creates basins for computing the meridional overturning
circulation (MOC).  No arguments are required.  The optional --plot
flag can be used to produce plots of each MOC basin.

Authors: Xylar Asay-Davis, Phillip J. Wolfram
Last Modified: 10/16/2016
"""
import os
import subprocess
from optparse import OptionParser

def spcall(args): #{{{
    return subprocess.check_call(args, env=os.environ.copy()) #}}}

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

MOCGroupName = 'MOCBasinRegionsGroup'
basinsGroupName = 'OceanBasinRegionsMOCGroup'

subBasins = {'Atlantic': ['Atlantic', 'Mediterranean'],
             'IndoPacific': ['Pacific', 'Indian'],
             'Pacific': ['Pacific'],
             'Indian': ['Indian']}


MOCSouthernBoundary = {'Atlantic': '34S',
                    'IndoPacific': '34S',
                    'Pacific': '6S',
                    'Indian': '6S'}

# output file names
MOCFileName = 'MOCBasins.geojson'
unmaskedBasinFileName = 'unmaskedMOCBasins.geojson'

# temp file names that we delete later
tempSeparateBasinFileName = 'temp_separate_basins.geojson'
tempCombinedBasinFileName = 'temp_combined_basins.geojson'
tempMOCFileName = 'temp_MOC.geojson'

# remove old files so we don't unintentionally append features
for fileName in [MOCFileName, unmaskedBasinFileName, tempSeparateBasinFileName,
                 tempCombinedBasinFileName, tempMOCFileName]:
    if os.path.exists(fileName):
        os.remove(fileName)

for basinName in subBasins:

    imageName =  '%s_MOC.png'%basinName

    MOCMaskFileName = 'ocean/region/MOC_mask_%s/region.geojson' \
        %  MOCSouthernBoundary[basinName]

    MOCSouternBoarderFileName = 'ocean/transect/MOC_%s/transect.geojson' \
        %  MOCSouthernBoundary[basinName]

    print " * merging features to make %s Basin"%basinName

    for oceanName in subBasins[basinName]:
        spcall(['./merge_features.py', '-d', 'ocean/region',
                '-t', '%s_Basin'%oceanName,
                '-o', tempSeparateBasinFileName])

    #merge the the features into a single file
    print " * combining features into single feature named %s_MOC"%basinName
    spcall(['./combine_features.py', '-f', tempSeparateBasinFileName,
            '-n', '%s_MOC'%basinName,
            '-o', tempCombinedBasinFileName])

    spcall(['./merge_features.py', '-f', tempCombinedBasinFileName,
            '-o', unmaskedBasinFileName])

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

spcall(['./set_group_name.py', '-f', unmaskedBasinFileName,
        '-g', basinsGroupName])

spcall(['./set_group_name.py', '-f', MOCFileName,
        '-g', MOCGroupName])

if options.plot:
    spcall(['./plot_features.py', '-f', unmaskedBasinFileName,
            '-o', 'unmaskedMOCBasins.png', '-m', 'cyl'])

    spcall(['./plot_features.py', '-f', MOCFileName,
            '-o', 'MOCBasins.png', '-m', 'cyl'])

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
