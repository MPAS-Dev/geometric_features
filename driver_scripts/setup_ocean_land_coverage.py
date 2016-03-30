#!/usr/bin/env python
"""
This script combines Natural Earth land coverage north of 60S with Antarctic
ice coverage or grounded ice coverage from Bedmap2.  No arguments
are required. The optional --with_cavities flag uses grounded ice rather than
both grounded and floating ice to determine land coverage (thus opening
up sub-ice-shelf cavities in the ocean.  The --plot flag can be used to 
produce plots of the result.
"""
import os
import os.path
import subprocess
import shutil
from optparse import OptionParser

parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")
parser.add_option("--with_cavities", action="store_true", dest="with_cavities")

options, args = parser.parse_args()

defaultFileName = 'features.geojson'

if os.path.exists(defaultFileName):
    os.remove(defaultFileName)

args = ['./difference_features.py', '-f', 'natural_earth/region/Land_Coverage/region.geojson', 
        '-m', 'ocean/region/Global_Ocean_90S_to_60S/region.geojson']
subprocess.check_call(args, env=os.environ.copy())

if options.with_cavities:
    antarcticLandCoverage = 'bedmap2/region/AntarcticGroundedIceCoverage/region.geojson'
    imageName = 'landCoverageWithCavities.png'
else:
    antarcticLandCoverage = 'bedmap2/region/AntarcticIceCoverage/region.geojson'
    imageName = 'landCoverageWithoutCavities.png'

args = ['./merge_features.py', '-f', antarcticLandCoverage]
subprocess.check_call(args, env=os.environ.copy())

outName = 'landCoverage.geojson'

shutil.move(defaultFileName,outName)

#print "Splitting features at prime meridian"
#args = ['./fix_features_at_prime_meridian.py', '-f', outName]
#subprocess.check_call(args, env=os.environ.copy())

#shutil.move(defaultFileName,outName)
    
if(options.plot):
    args = ['./plot_features.py', '-f', outName, '-o', imageName, '-m', 'cyl']
    subprocess.check_call(args, env=os.environ.copy())
