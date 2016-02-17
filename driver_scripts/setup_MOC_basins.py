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

defaultFileName = 'features.geojson'

if os.path.exists(defaultFileName):
    os.remove(defaultFileName)

basinName = 'Atlantic'
print " * merging features to make %s Basin"%basinName
MOCName =  '%s_MOC.geojson'%basinName
imageName =  '%s_MOC.png'%basinName
basinFileName =  '%s_Basin.geojson'%basinName
for oceanName in ['Atlantic', 'Mediterranean']:
    tag = '%s_Basin'%oceanName
    MOCMaskFileName = 'ocean/region/MOC_mask_30S/region.geojson'

    args = ['./merge_features.py', '-d', 'ocean', '-t', tag]
    subprocess.check_call(args, env=os.environ.copy())

shutil.move(defaultFileName,basinFileName)

print " * masking out features south of MOC region"
args = ['./difference_features.py', '-f', basinFileName, '-m', MOCMaskFileName]
subprocess.check_call(args, env=os.environ.copy())

shutil.move(defaultFileName,MOCName)

if options.plot:
    args = ['./plot_features.py', '-f', MOCName, '-o', imageName, '-m', 'cyl']
    subprocess.check_call(args, env=os.environ.copy())



if os.path.exists(defaultFileName):
    os.remove(defaultFileName)

basinName = 'IndoPacific'
print " * merging features to make %s Basin"%basinName
MOCName =  '%s_MOC.geojson'%basinName
imageName =  '%s_MOC.png'%basinName
basinFileName =  '%s_Basin.geojson'%basinName
for oceanName in ['Pacific', 'Indian']:
    tag = '%s_Basin'%oceanName
    MOCMaskFileName = 'ocean/region/MOC_mask_30S/region.geojson'

    args = ['./merge_features.py', '-d', 'ocean', '-t', tag]
    subprocess.check_call(args, env=os.environ.copy())

shutil.move(defaultFileName,basinFileName)

print " * masking out features south of MOC region"
args = ['./difference_features.py', '-f', basinFileName, '-m', MOCMaskFileName]
subprocess.check_call(args, env=os.environ.copy())

shutil.move(defaultFileName,MOCName)

if options.plot:
    args = ['./plot_features.py', '-f', MOCName, '-o', imageName, '-m', 'cyl']
    subprocess.check_call(args, env=os.environ.copy())


for oceanName in ['Pacific', 'Indian']:
    tag = '%s_Basin'%oceanName
    basinFileName =  '%s_Basin.geojson'%oceanName
    MOCName =  '%s_MOC.geojson'%oceanName
    imageName =  '%s_MOC.png'%oceanName
    MOCMaskFileName = 'ocean/region/MOC_mask_6S/region.geojson'
    if os.path.exists(defaultFileName):
        os.remove(defaultFileName)

    print " * merging features to make %s Basin"%oceanName
    args = ['./merge_features.py', '-d', 'ocean', '-t', tag]
    subprocess.check_call(args, env=os.environ.copy())

    shutil.move(defaultFileName,basinFileName)

    print " * masking out features south of MOC region"
    args = ['./difference_features.py', '-f', basinFileName, '-m', MOCMaskFileName]
    subprocess.check_call(args, env=os.environ.copy())

    shutil.move(defaultFileName,MOCName)

    if options.plot:
        args = ['./plot_features.py', '-f', MOCName, '-o', imageName, '-m', 'cyl']
        subprocess.check_call(args, env=os.environ.copy())
