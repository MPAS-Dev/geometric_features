#!/usr/bin/env python

"""
This script creates region groups for ice shelves

Author: Xylar Asay-Davis
"""

import os
import os.path
import subprocess


def build_ice_shelves():  # {{{
    groupName = 'IceShelvesRegionsGroup'
    iceShelvesFileName = 'iceShelves.geojson'

    # temp file names that we delete later
    tempSeparateFileName = 'temp_separate_shelves.geojson'
    tempCombinedFileName = 'temp_combined_shelves.geojson'

    # remove old files so we don't unintentionally append features
    for fileName in [iceShelvesFileName,
                     tempSeparateFileName,
                     tempCombinedFileName]:
        if os.path.exists(fileName):
            os.remove(fileName)

    iceShelfNames = ['Abbot',
                     'Amery',
                     'Atka',
                     'Aviator',
                     'Bach',
                     'Baudouin',
                     'Borchgrevink',
                     'Brahms',
                     'Brunt_Stancomb',
                     'Campbell',
                     'Cheetham',
                     'Conger_Glenzer',
                     'Cook',
                     'Cosgrove',
                     'Crosson',
                     'Dennistoun',
                     'Dibble',
                     'Dotson',
                     'Drygalski',
                     'Edward_VIII',
                     'Ekstrom',
                     'Ferrigno',
                     'Filchner',
                     'Fimbul',
                     'Fitzgerald',
                     'Frost',
                     'GeikieInlet',
                     'George_VI',
                     'Getz',
                     'Gillet',
                     'Hamilton',
                     'Hannan',
                     'HarbordGlacier',
                     'Helen',
                     'Holmes',
                     'HolmesWest',
                     'Hull',
                     'Jelbart',
                     'Land',
                     'Larsen_B',
                     'Larsen_C',
                     'Larsen_D',
                     'Larsen_E',
                     'Larsen_F',
                     'Larsen_G',
                     'Lazarev',
                     'Lillie',
                     'Mariner',
                     'Matusevitch',
                     'Mendelssohn',
                     'Mertz',
                     'Moscow_University',
                     'Moubray',
                     'Mulebreen',
                     'Myers',
                     'Nansen',
                     'Nickerson',
                     'Ninnis',
                     'Nivl',
                     'Noll',
                     'Nordenskjold',
                     'Pine_Island',
                     'PourquoiPas',
                     'Prince_Harald',
                     'Publications',
                     'Quar',
                     'Rayner_Thyer',
                     'Rennick',
                     'Richter',
                     'Riiser-Larsen',
                     'Ronne',
                     'Ross_East',
                     'Ross_West',
                     'Shackleton',
                     'Shirase',
                     'Slava',
                     'SmithInlet',
                     'Stange',
                     'Sulzberger',
                     'Suvorov',
                     'Swinburne',
                     'Thwaites',
                     'Tinker',
                     'Totten',
                     'Tracy_Tremenchus',
                     'Tucker',
                     'Underwood',
                     'Utsikkar',
                     'Venable',
                     'Verdi',
                     'Vigrid',
                     'Vincennes',
                     'Voyeykov',
                     'West',
                     'Wilkins',
                     'Wilma_Robert_Downer',
                     'Withrow',
                     'Wordie',
                     'Wylde',
                     'Zubchatyy']

    combinedIceShelves = {'Filchner-Ronne': ['Filchner', 'Ronne'],
                          'Ross': ['Ross_East', 'Ross_West'],
                          'Antarctica': ['AntarcticPenninsulaIMBIE',
                                         'WestAntarcticaIMBIE',
                                         'EastAntarcticaIMBIE'],
                          'Peninsula': ['AntarcticPenninsulaIMBIE'],
                          'West Antarctica': ['WestAntarcticaIMBIE'],
                          'East Antarctica': ['EastAntarcticaIMBIE']}

    nIMBIEBasins = 27
    for basinNumber in range(1, nIMBIEBasins+1):
        basinName = 'Antarctica_IMBIE{}'.format(basinNumber)
        combinedIceShelves['IMBIE{}'.format(basinNumber)] = [basinName]

    # build analysis regions from combining ice shelves from regions with the
    # appropriate tags
    for shelfName in combinedIceShelves:
        subNames = combinedIceShelves[shelfName]

        print " * merging features to make {}".format(shelfName)
        for subName in subNames:
            subprocess.check_call(['./merge_features.py',
                                   '-d', 'iceshelves/region', '-t', subName,
                                   '-o', tempSeparateFileName])

        # merge the the features into a single file
        print " * combining features into single feature named " \
            "{}".format(shelfName)
        subprocess.check_call(['./combine_features.py',
                               '-f', tempSeparateFileName,
                               '-n', shelfName,
                               '-o', tempCombinedFileName])

        subprocess.check_call(['./merge_features.py',
                               '-f', tempCombinedFileName,
                               '-o', iceShelvesFileName])

        # remove temp files
        for fileName in [tempSeparateFileName, tempCombinedFileName]:
            os.remove(fileName)

    # build ice shelves from regions with the appropriate tags
    for shelfName in iceShelfNames:

        print " * merging features to make {}".format(shelfName)
        subprocess.check_call(['./merge_features.py',
                               '-d', 'iceshelves/region', '-t', shelfName,
                               '-o', tempSeparateFileName])

        # merge the the features into a single file
        print " * combining features into single feature named " \
            "{}".format(shelfName)
        subprocess.check_call(['./combine_features.py',
                               '-f', tempSeparateFileName,
                               '-n', shelfName,
                               '-o', tempCombinedFileName])

        subprocess.check_call(['./merge_features.py',
                               '-f', tempCombinedFileName,
                               '-o', iceShelvesFileName])

        # remove temp files
        for fileName in [tempSeparateFileName, tempCombinedFileName]:
            os.remove(fileName)

    subprocess.check_call(['./set_group_name.py',
                           '-f', iceShelvesFileName,
                           '-g', groupName])
    # }}}


build_ice_shelves()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
