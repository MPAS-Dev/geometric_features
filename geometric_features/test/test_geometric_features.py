import os
import pytest

from geometric_features.test import TestCase, loaddatadir
from geometric_features import GeometricFeatures


@pytest.mark.usefixtures('loaddatadir')
class TestGeometricFeatures(TestCase):

    @staticmethod
    def check_feature(feature, expected_name='Celtic Sea',
                      expected_component='ocean',
                      expected_type='region'):
        """
        Check some properties of the feature

        Parameters
        ----------
        feature : dict
            A geojson feature to check

        expected_name : str
            The expected name of the feature

        expected_component : str, optional
            The component from which to retrieve the feature

        expected_type : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)
        """
        assert feature['properties']['name'] == expected_name
        assert feature['properties']['component'] == expected_component
        assert feature['properties']['object'] == expected_type

    def test_read_by_name(self, component='ocean', object_type='region',
                          feature='Celtic Sea'):
        """
        Read an example feature by name and test for a few expected
        attributes.

        Parameters
        ----------
         component : str, optional
            The component from which to retrieve the feature

        object_type : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        feature : str, optional
            The name of a geometric feature to read
        """
        gf = GeometricFeatures()
        fc = gf.read(componentName=component, objectType=object_type,
                     featureNames=[feature])
        self.check_feature(fc.features[0], expected_name=feature,
                           expected_component=component,
                           expected_type=object_type)

    def test_read_by_tag(self, component='ocean', object_type='region',
                         tag='Adriatic_Sea'):
        """
        Read an example feature by name and test for a few expected
        attributes.

        Parameters
        ----------
         component : str, optional
            The component from which to retrieve the feature

        object_type : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        tag : str, optional
            The name of a tag to read
        """
        gf = GeometricFeatures()
        fc = gf.read(componentName=component, objectType=object_type,
                     tags=[tag])
        self.check_feature(fc.features[0], expected_name='Adriatic Sea',
                           expected_component=component,
                           expected_type=object_type)

    def test_read_all_tag(self, component='ocean', object_type='region',
                          tags=('Adriatic_Sea', 'Mediterranean_Basin')):
        """
        Read an example feature by name and test for a few expected
        attributes.

        Parameters
        ----------
         component : str, optional
            The component from which to retrieve the feature

        object_type : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        tags : list of str, optional
            The names of tags to read
        """
        gf = GeometricFeatures()
        fc = gf.read(componentName=component, objectType=object_type,
                     tags=tags, allTags=True)
        assert len(fc.features) == 1
        self.check_feature(fc.features[0], expected_name='Adriatic Sea',
                           expected_component=component,
                           expected_type=object_type)

    def test_split(self, component='ocean', object_type='region',
                   tag='Mediterranean_Basin'):
        """
        Read an example feature by name and test for a few expected
        attributes.

        Parameters
        ----------
         component : str, optional
            The component from which to retrieve the feature

        object_type : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        tag : str, optional
            The name of a tag to read
        """
        gf = GeometricFeatures()
        fc = gf.read(componentName=component, objectType=object_type,
                     tags=[tag])

        gf.split(fc, destinationDir=self.datadir)

        for feature in fc.features:
            name = feature['properties']['name']
            subdir = name.replace(' ', '_')
            path = f'{self.datadir}/{component}/{object_type}/{subdir}/{object_type}.geojson'
            assert os.path.exists(path)
