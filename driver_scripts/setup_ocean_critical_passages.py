#!/usr/bin/env python
"""
This script combines transects defining cricial passages.  No arguments
are required.
"""
import os
import os.path
import subprocess
import shutil
from optparse import OptionParser

import glob


parser = OptionParser()
options, args = parser.parse_args()

defaultFileName = 'features.geojson'

try:
    os.remove(defaultFileName)
except OSError:
    pass

args = ['./merge_features.py', '-d', 'ocean/transect', '-t', 'Critical_Passage']
subprocess.check_call(args, env=os.environ.copy())
    

outName = 'criticalPassages.geojson'
shutil.move(defaultFileName,outName)
