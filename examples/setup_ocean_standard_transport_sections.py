#!/usr/bin/env python

"""
This script creates region groups for the standard set of transport sections,
all of which have the "standard_transport_sections" tag.

Author: Xylar Asay-Davis
"""

import os
import os.path
import subprocess

tag = 'standard_transport_sections'
fileName = 'standard_transport_sections.geojson'
groupName = 'StandardTransportSectionsRegionsGroup'
    
if os.path.exists(fileName):
    os.remove(fileName)


subprocess.check_call(['./merge_features.py',
                       '-d', 'ocean/transect',
                       '-t', tag,
                       '-o', fileName])

subprocess.check_call(['./set_group_name.py',
                       '-f', fileName,
                       '-g', groupName])

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
