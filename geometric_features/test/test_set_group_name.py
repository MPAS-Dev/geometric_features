"""
Unit test infrastructure for FeatureCollection.set_group_name

Phillip J. Wolfram
"""

import pytest
import json

from geometric_features.test import TestCase, loaddatadir
from geometric_features import GeometricFeatures


@pytest.mark.usefixtures("loaddatadir")
class TestSetGroupName(TestCase):

    def test_assign_groupname(self, componentName='ocean', objectType='region',
                              featureName='Celtic Sea',
                              groupName='testGroupName'):
        """
        Write example file to test groupName functionality.

        Parameters
        ----------
         componentName : {'bedmachine', 'bedmap2', 'iceshelves', 'landice', 'natural_earth', 'ocean'}, optional
            The component from which to retieve the feature

        objectType : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        featureName : str, optional
            The names of geometric feature to read

        groupName : str, optional
            The group name to assign
        """
        # Authors
        # -------
        # Phillip J. Wolfram
        # Xylar Asay-Davis

        # verification that groupName is in file
        def verify_groupName(destfile, groupName):
            with open(destfile) as f:
                filevals = json.load(f)
                assert 'groupName' in filevals, \
                    'groupName does not exist in {}'.format(destfile)
                assert filevals['groupName'] == groupName, \
                    'Incorrect groupName of {} specified instead of ' \
                    '{}.'.format(filevals['groupName'], groupName)

        # test via shell script
        gf = GeometricFeatures(cacheLocation=str(self.datadir),
                               remoteBranchOrTag='master')
        fc = gf.read(componentName, objectType, [featureName])
        fc.set_group_name(groupName)
        assert fc.otherProperties['groupName'] == groupName, \
            'groupName not assigned to FeatureCollection'
        destfile = str(self.datadir.join('test.geojson'))
        fc.to_geojson(destfile)
        verify_groupName(destfile, groupName)


# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
