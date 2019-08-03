#!/usr/bin/env python
"""
A script for converting the README.md to a quick-start guide for inclusion
in the documentation
"""

from m2r import convert


def build_quick_start():

    replace = {'# Geometric Features': '# Quick Start',
               '[![Documentation Status]': '',
               '## Quick Start': ''}

    skip = [('## Documentation', '## Quick Start')]
    outContent = ''
    skipMode = False
    with open('../README.md', 'r') as inFile:
        for line in inFile.readlines():
            for skipStart, skipEnd in skip:
                if not skipMode and skipStart in line:
                    skipMode = True
                if skipMode and skipEnd in line:
                    skipMode = False
            if not skipMode:
                for replaceString in replace:
                    if replaceString in line:
                        line = replace[replaceString]
                        break
                outContent = outContent + line

    outContent = convert(outContent)

    with open('quick_start.rst', 'w') as outFile:
        outFile.write('.. _quick_start:\n\n')
        outFile.write(outContent)
