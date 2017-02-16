#!/usr/bin/env python
"""
This script combines Antarctic basins into a single feature file.  No arguments
are required. The optional --plot flag can be used to produce plots of the
result.
"""
import os
import os.path
import subprocess
from optparse import OptionParser

import glob

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

files = glob.glob('landice/region/Antarctica_IMBIE*/*.geojson')
files.sort()

outName = 'Antarctic_Basins.geojson'

if os.path.exists(outName):
    os.remove(outName)

print "Adding feature from files:"
for fileName in files:
    print fileName
    args = ['./merge_features.py', '-f', fileName, '-o', outName]
    subprocess.check_call(args, env=os.environ.copy())


imageName = 'Antarctic_Basins.png'

if(options.plot):
    args = ['./plot_features.py', '-f', outName, '-o', imageName,
            '-m', 'southpole']
    subprocess.check_call(args, env=os.environ.copy())
