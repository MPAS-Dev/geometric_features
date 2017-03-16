#!/usr/bin/env python
"""
Utility funcitons for provenance of feature files.

Authors: Phillip J. Wolfram
Last Modified: 09/29/2016
"""

import os
import sys
import socket
import subprocess
import numpy as np
import datetime

def provenance_command(): #{{{
    cwd = os.getcwd()
    user = os.getenv('USER')
    curtime = datetime.datetime.now().strftime('%m/%d/%y %H:%M')
    call = ' '.join(sys.argv)
    host = socket.gethostname()
    try:
        githash = subprocess.check_output(['git', 'describe', '--always','--dirty']).strip('\n')
    except:
        githash = 'None'
    sep = ' : '
    provstr = sep.join([curtime,  host, user, cwd, githash, call]) + ';'
    return provstr #}}}

if __name__ == "__main__":
    print provenance_command()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
