#!/usr/bin/env python
"""
This script creates basins for computing the meridional overturning
circulation (MOC).  No arguments are required.  The optional --plot
flag can be used to produce plots of each MOC basin.

Authors: Xylar Asay-Davis, Phillip J. Wolfram
Last Modified: 09/09/2016
"""
import os
import subprocess
from optparse import OptionParser

def spcall(args): #{{{
    return subprocess.check_call(args, env=os.environ.copy()) #}}}

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

groupNameMOC = 'MOCBasinRegionsGroup'
groupNameBasins = 'OceanBasinRegionsMOCGroup'

subBasins = {'Atlantic': ['Atlantic', 'Mediterranean'],
             'IndoPacific': ['Pacific', 'Indian'],
             'Pacific': ['Pacific'],
             'Indian': ['Indian']}

MOCMaskFileNames = {'Atlantic': 'ocean/region/MOC_mask_34S/region.geojson',
                    'IndoPacific': 'ocean/region/MOC_mask_34S/region.geojson',
                    'Pacific': 'ocean/region/MOC_mask_6S/region.geojson',
                    'Indian': 'ocean/region/MOC_mask_6S/region.geojson'}

for basinName in subBasins:

    # output file names
    basinFileName =  '%s_Basin_separate.geojson'%basinName
    basinCombinedFileName =  '%s_Basin.geojson'%basinName
    MOCName =  '%s_MOC.geojson'%basinName
    imageName =  '%s_MOC.png'%basinName

    # remove old files (to ensure there isn't double-appending via merge_features
    for afile in [basinFileName, basinCombinedFileName, MOCName, imageName]:
        if os.path.exists(afile):
            os.remove(afile)

    print " * merging features to make %s Basin"%basinName

    for oceanName in subBasins[basinName]:
        spcall(['./merge_features.py', '-d', 'ocean/region', '-t', '%s_Basin'%oceanName,
                '-o', basinFileName])

    #merge the the features into a single file
    print " * combining features into single feature named %s_MOC"%basinName
    spcall(['./combine_features.py', '-f', basinFileName, '-n', '%s_MOC'%basinName,
            '-g', groupNameBasins, '-o', basinCombinedFileName])

    print " * masking out features south of MOC region"
    spcall(['./difference_features.py', '-f', basinCombinedFileName,
            '-m', MOCMaskFileNames[basinName], '-g', groupNameMOC, '-o', MOCName])

    if options.plot:
        spcall(['./plot_features.py', '-f', MOCName, '-o', imageName, '-m', 'cyl'])


# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
