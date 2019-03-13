#!/usr/bin/env python
"""
A script for converting the README.md to a quick-start guide for inclusion
in the documentation
"""

from m2r import convert


def build_quick_start():

    replace = {}
    outContent = 'Quick Start\n'
    outContent = outContent + '=============\n'
    with open('../README.md', 'r') as inFile:
        for line in inFile.readlines():
            for replaceString in replace:
                if replaceString in line:
                    line = replace[replaceString]
                    break
            outContent = outContent + line

    outContent = convert(outContent)

    with open('quick_start.rst', 'w') as outFile:
        outFile.write('.. _quick_start:\n\n')
        outFile.write(outContent)
