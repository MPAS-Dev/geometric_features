#!/usr/bin/env python
"""
Determines contributors for geojson files and makes CONTRIBUTORS.md file

Phillip J. Wolfram
04/05/2016
"""

import os
import subprocess
import shutil
import datetime
import re


def append_to_file(aline, afile):
    """ appends aline to afile """
    with open(afile, "a") as fid:
        fid.write(aline)
        if aline[-1] != '\n':
            fid.write('\n')

def build_contrib_file():
    """ builds the contributor file CONTRIBUTORS.md """
    # get file directories
    gitroot = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).replace('\n', '')
    contribdir = gitroot + '/contributors'
    contribfile = contribdir + '/CONTRIBUTORS.md'

    # go to git root
    os.chdir(gitroot)

    # build up contrib file
    shutil.copyfile(contribdir + '/CONTRIBUTORS_HEADER', contribfile)

    append_to_file('List populated on %s:'%
                   (datetime.datetime.now().strftime("%Y-%m-%d %H:%M")), contribfile)
    append_to_file('\n', contribfile)

    gitgrep = subprocess.check_output(['git', 'grep', 'author', '--', '*.geojson'])
    authors = set(re.findall(r'"author": "(.*?)"', gitgrep))
    for author in sorted(authors):
        append_to_file(' * ' + author, contribfile)

if __name__ == "__main__":
    build_contrib_file()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
