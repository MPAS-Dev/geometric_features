"""
Unit test infrastructure for set_group_name.py

Phillip J. Wolfram
03/16/2017
"""

import pytest
from test import TestCase, loaddatadir

import subprocess
import shutil
import json

@pytest.mark.usefixtures("loaddatadir")
class TestSetGroupName(TestCase):

    def test_assign_groupname(self,
            srctest='ocean/region/Celtic_Sea/region.geojson',
            groupName='testGroupName'):
        """
        Write example file to test groupName functionality.

        Parameters
        ----------
        srctest : location of geojson file to test
                  addition of groupName

        Phillip J. Wolfram
        Last Modified: 03/16/2017
        """

        # verification that groupName is in file
        def verify_groupName(destfile, groupName):
            with open(destfile) as f:
                filevals = json.load(f)
                assert 'groupName' in filevals, \
                        'groupName does not exist in {}'.format(destfile)
                assert filevals['groupName'] == groupName, \
                       'Incorrect groupName of {} specified instead of {}.'\
                       .format(filevals['groupName'], groupName)

        # test via shell script
        destfile = bytes(self.datadir.join('test.geojson'))
        shutil.copyfile(srctest, destfile)
        subprocess.check_call(['./set_group_name.py',
                '-f', destfile,'-g', groupName])
        verify_groupName(destfile, groupName)

        # test via function
        destfile = bytes(self.datadir.join('test.geojson'))
        shutil.copyfile(srctest, destfile)
        from set_group_name import write_group_name
        write_group_name(destfile, groupName)
        verify_groupName(destfile, groupName)



# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
