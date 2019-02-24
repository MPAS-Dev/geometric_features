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


parser = OptionParser()
parser.add_option("--plot", action="store_true", dest="plot")

options, args = parser.parse_args()

outFinalFileName = 'Extended_Antarctic_Basins.geojson'

if os.path.exists(outFinalFileName):
    os.remove(outFinalFileName)

tempFileName = 'merged_basin.geojson'
if os.path.exists(tempFileName):
    os.remove(tempFileName)

for basin in range(1, 28):
    print "Adding feature from IMBIE basin {:d}".format(basin)
    outFileName = 'AntarcticIMBIE{:d}.geojson'.format(basin)
    basinName = 'Antarctica_IMBIE{:d}'.format(basin)
    tags = basinName

    if os.path.exists(outFileName):
        os.remove(outFileName)

    # add all the features in the basin
    args = ['./merge_features.py', '-d', 'iceshelves/region',
            '-o', tempFileName, '-t', tags]
    subprocess.check_call(args, env=os.environ.copy())

    # combine (i.e. fuse) them into a single feature
    args = ['./combine_features.py', '-f', tempFileName, '-n', basinName,
            '-o', outFileName]
    subprocess.check_call(args, env=os.environ.copy())

    os.remove(tempFileName)

    # add the new feature to the final file
    args = ['./merge_features.py', '-f', outFileName, '-o', outFinalFileName]
    subprocess.check_call(args, env=os.environ.copy())

if(options.plot):
    imageName = 'Extended_Antarctic_Basins.png'

    args = ['./plot_features.py', '-f', outFinalFileName, '-o', imageName,
            '-m', 'southpole']
    subprocess.check_call(args, env=os.environ.copy())
