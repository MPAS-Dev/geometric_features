#!/usr/bin/env python
"""
This script creates basins for computing the meridional overturning 
circulation (MOC).  No arguments are required.  The optional --plot
flag can be used to produce plots of each MOC basin.
"""
import os
import os.path
import subprocess
import shutil
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()


for oceanName in 'Atlantic', 'Pacific', 'Indian':

    defaultFileName = 'features.geojson'
    tag = '%s_Basin'%oceanName
    basinName =  '%s_Basin.geojson'%oceanName
    MOCName =  '%s_MOC.geojson'%oceanName
    imageName =  '%s_MOC.png'%oceanName
    MOCMaskFileName = 'ocean/region/MOC_mask/region.geojson'
    if os.path.exists(defaultFileName):
        os.remove(defaultFileName)

    print " * merging features to make %s Basin"%oceanName
    args = ['./merge_features.py', '-d', 'ocean', '-t', tag]
    subprocess.check_call(args, env=os.environ.copy())

    shutil.move(defaultFileName,basinName)

    print " * masking out features south of MOC region"
    args = ['./difference_features.py', '-f', basinName, '-m', MOCMaskFileName]
    subprocess.check_call(args, env=os.environ.copy())

    shutil.move(defaultFileName,MOCName)

    if options.plot:
        args = ['./plot_features.py', '-f', MOCName, '-o', imageName, '-m', 'cyl']
        subprocess.check_call(args, env=os.environ.copy())
