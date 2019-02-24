#!/usr/bin/env python

"""
Determines contributors for geojson files and makes CONTRIBUTORS.md file

Phillip J. Wolfram, Xylar-Asay-Davis
02/23/2019
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
    args = ['git', 'rev-parse', '--show-toplevel']
    gitroot = subprocess.check_output(args).decode('utf-8').replace('\n', '')
    contribdir = gitroot + '/contributors'
    contribfile = contribdir + '/CONTRIBUTORS.md'

    # go to git root
    os.chdir(gitroot)

    # build up contrib file
    shutil.copyfile(contribdir + '/CONTRIBUTORS_HEADER', contribfile)

    append_to_file(
        'List populated on {}:'.format(
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
        contribfile)
    append_to_file('\n', contribfile)

    gitgrep = subprocess.check_output(
        ['git', 'grep', 'author', '--', '*.geojson']).decode('utf-8')
    authors = re.findall(r'"author": "(.*?)"', gitgrep)
    splitauthors = []
    for author in authors:
        split = author.replace('; ', ', ').split(', ')
        splitauthors.extend(split)
    authors = sorted(list(set(splitauthors)))
    for author in authors:
        append_to_file(' * ' + author, contribfile)


if __name__ == "__main__":
    build_contrib_file()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
