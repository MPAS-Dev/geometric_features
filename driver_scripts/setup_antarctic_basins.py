#!/usr/bin/env python
"""
This script combines Antarctic basins into a single feature file.  No arguments
are required. The optional --plot flag can be used to produce plots of the 
result.
"""
import os
import os.path
import subprocess
import shutil
from optparse import OptionParser

import glob

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

files = glob.glob('landice/region/Antarctica_IMBIE*/*.geojson')
files.sort()

defaultFileName = 'features.geojson'

if os.path.exists(defaultFileName):
    os.remove(defaultFileName)
  
print "Adding feature from files:"
for fileName in files:
    print fileName
    args = ['./merge_features.py', '-f', fileName]
    subprocess.check_call(args, env=os.environ.copy())
    

outName = 'Antarctic_Basins.geojson'
imageName = 'Antarctic_Basins.png'

shutil.move(defaultFileName,outName)

print "Splitting features at prime meridian"
args = ['./fix_features_at_prime_meridian.py', '-f', outName]
subprocess.check_call(args, env=os.environ.copy())

shutil.move(defaultFileName,outName)
    
if(options.plot):
    args = ['./plot_features.py', '-f', outName, '-o', imageName, '-m', 'southpole']
    subprocess.check_call(args, env=os.environ.copy())
