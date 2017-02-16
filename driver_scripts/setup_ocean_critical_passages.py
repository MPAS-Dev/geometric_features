#!/usr/bin/env python
"""
This script combines transects defining cricial passages.  No arguments
are required.
"""
import os
import os.path
import subprocess

outName = 'criticalPassages.geojson'

try:
    os.remove(outName)
except OSError:
    pass

args = ['./merge_features.py', '-d', 'ocean/transect',
        '-t', 'Critical_Passage', '-o', outName]
subprocess.check_call(args, env=os.environ.copy())
