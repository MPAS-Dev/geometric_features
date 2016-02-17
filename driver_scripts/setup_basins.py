#!/usr/bin/env python
"""
This script creates 6 major ocean basins.  No arguments are required. The 
optional --plot flag can be used to produce plots of each basin.
"""
import os
import os.path
import subprocess
import shutil
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

for oceanName in 'Atlantic', 'Pacific', 'Indian', 'Arctic', 'Southern_Ocean', 'Mediterranean':

    defaultFileName = 'features.geojson'
    tag = '%s_Basin'%oceanName
    basinName =  '%s_Basin.geojson'%oceanName
    imageName =  '%s_Basin.png'%oceanName

    if os.path.exists(defaultFileName):
        os.remove(defaultFileName)
  
    print " * merging features to make %s Basin"%oceanName
    args = ['./merge_features.py', '-d', 'ocean', '-t', tag]
    subprocess.check_call(args, env=os.environ.copy())

    shutil.move(defaultFileName,basinName)
    
    if(options.plot):
        args = ['./plot_features.py', '-f', basinName, '-o', imageName, '-m', 'cyl']
        subprocess.check_call(args, env=os.environ.copy())
