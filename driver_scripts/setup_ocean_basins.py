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



parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

groupName = 'OceanBasinRegionsGroup'

for oceanName in 'Atlantic', 'Pacific', 'Indian', 'Arctic', 'Southern_Ocean', 'Mediterranean':

    tag = '%s_Basin'%oceanName
    basinFileNameName =  '%s_Basin_separate.geojson'%oceanName
    basinCombinedFileName =  '%s_Basin.geojson'%oceanName
    imageName =  '%s_Basin.png'%oceanName

    # remove old files (to ensure there isn't double-appending via merge_features
    for afile in [basinFileNameName, basinCombinedFileName, imageName]:
        if os.path.exists(afile):
            os.remove(afile)
  
    print " * merging features to make %s Basin"%oceanName
    args = ['./merge_features.py', '-d', 'ocean/region', '-t', tag, '-o', basinFileNameName]
    subprocess.check_call(args, env=os.environ.copy())

    #merge the the features into a single file
    print " * combining features into single feature named %s_Basin"%oceanName
    spcall(['./combine_features.py', '-f', basinFileNameName, '-n', '%s_Basin'%oceanName,
            '-g', groupName, '-o', basinCombinedFileName])
    
    if(options.plot):
        args = ['./plot_features.py', '-f', basinCombinedFileName, '-o', imageName, '-m', 'cyl']
        subprocess.check_call(args, env=os.environ.copy())
