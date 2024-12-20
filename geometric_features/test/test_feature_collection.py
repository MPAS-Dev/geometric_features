import json
import os

import pytest
import shapely
import shapely.geometry

from geometric_features import (FeatureCollection, GeometricFeatures,
                                read_feature_collection)
from geometric_features.test import TestCase, loaddatadir


@pytest.mark.usefixtures('loaddatadir')
class TestFeatureCollection(TestCase):

    @staticmethod
    def read_feature(region='Adriatic_Sea'):
        """
        Read an example feature collection for testing

        Parameters
        ----------
        region : str, optional
            The name of an ocean region to read

        Returns
        -------
        fc : geometric_features.FeatureCollection
            The feature collection
        """
        if 'GEOMETRIC_DATA_DIR' in os.environ:
            cache_location = os.environ['GEOMETRIC_DATA_DIR']
        else:
            cache_location = './geometric_data'

        filename = f'{cache_location}/ocean/region/{region}/region.geojson'

        fc = read_feature_collection(filename)
        return fc

    @staticmethod
    def check_feature(feature, expected_name='Adriatic Sea',
                      expected_type='Polygon'):
        """
        Check some properties of the feature

        Parameters
        ----------
        feature : dict
            A geojson feature to check

        expected_name : str
            The expected name of the feature

        expected_type : str
            The expected geometry type of the feature
        """
        assert feature['properties']['name'] == expected_name
        assert feature['properties']['component'] == 'ocean'
        assert feature['geometry']['type'] == expected_type

    def test_read_feature_collection(self):
        """
        Test reading a feature collection from a file
        """
        fc = self.read_feature()
        assert len(fc.features) == 1
        feature = fc.features[0]
        self.check_feature(feature)

    def test_copy_features(self):
        """
        Test copying the features in a feature collection
        """
        fc = self.read_feature()
        other = FeatureCollection(features=fc.features,
                                  otherProperties=fc.otherProperties)
        assert len(other.features) == 1
        feature = other.features[0]

        self.check_feature(feature)

    def test_add_feature(self):
        """
        Test adding a feature to a collection
        """
        fc1 = self.read_feature()
        fc2 = self.read_feature('Aegean_Sea')

        # add a feature already in the feature collection
        fc1.add_feature(fc1.features[0])
        assert len(fc1.features) == 1

        # add a new feature to the feature collection
        fc1.add_feature(fc2.features[0])
        assert len(fc1.features) == 2

        self.check_feature(fc1.features[0])
        self.check_feature(fc1.features[1], expected_name='Aegean Sea')

    def test_merge(self):
        """
        Test merging 2 feature collections
        """
        fc1 = self.read_feature()
        fc2 = self.read_feature('Aegean_Sea')

        # add a feature already in the feature collection
        fc1.merge(fc1)
        assert len(fc1.features) == 1

        # add a new feature to the feature collection
        fc1.merge(fc2)
        assert len(fc1.features) == 2

        self.check_feature(fc1.features[0])
        self.check_feature(fc1.features[1], expected_name='Aegean Sea')

    def test_add_tag(self):
        """
        Test adding a tag to the features in a collection
        """
        fc = self.read_feature(region='Adriatic_Sea')

        fc.tag(tags=['tag1', 'tag2', 'Mediterranean_Basin'])
        assert (fc.features[0]['properties']['tags'] ==
                'Adriatic_Sea;Mediterranean_Basin;tag1;tag2')

        self.check_feature(fc.features[0])

    def test_remove_tag(self):
        """
        Test removing a tag from the features in a collection
        """
        fc = self.read_feature(region='Adriatic_Sea')

        fc.tag(tags=['Mediterranean_Basin', 'tag1'], remove=True)
        assert (fc.features[0]['properties']['tags'] == 'Adriatic_Sea')

        self.check_feature(fc.features[0])

    def test_set_group_name(self, componentName='ocean', objectType='region',
                            featureName='Celtic Sea',
                            groupName='testGroupName'):
        """
        Write example file to test groupName functionality.

        Parameters
        ----------
         componentName : str, optional
            The component from which to retrieve the feature

        objectType : {'point', 'transect', 'region'}, optional
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        featureName : str, optional
            The name of a geometric feature to read

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
                    f'groupName does not exist in {destfile}'
                assert filevals['groupName'] == groupName, \
                    'Incorrect groupName of {} specified instead of ' \
                    '{}.'.format(filevals['groupName'], groupName)

        gf = GeometricFeatures()
        fc = gf.read(componentName, objectType, [featureName])
        fc.set_group_name(groupName)
        assert fc.otherProperties['groupName'] == groupName, \
            'groupName not assigned to FeatureCollection'
        destfile = str(self.datadir.join('test.geojson'))
        fc.to_geojson(destfile)
        verify_groupName(destfile, groupName)

    def test_combine(self):
        """
        Test combining the features in a collection into a single feature
        """
        fc1 = self.read_feature()
        fc2 = self.read_feature('Aegean_Sea')
        fc1.merge(fc2)
        name = 'Weird Disjoint Regions'
        combined = fc1.combine(name)
        assert len(combined.features) == 1
        self.check_feature(combined.features[0], expected_name=name,
                           expected_type='MultiPolygon')

    def test_difference(self):
        """
        Test removing a mask feature from another feature
        """
        fc = self.read_feature('Global_Ocean')
        mask = self.read_feature()
        difference = fc.difference(maskingFC=mask)
        assert len(difference.features) == 1
        self.check_feature(difference.features[0],
                           expected_name='Global Ocean',
                           expected_type='Polygon')

        # make sure the original global ocean and mask have no holes
        for fc_test in [fc, mask]:
            geom = fc_test.features[0]['geometry']
            shape = shapely.geometry.shape(geom)
            assert isinstance(shape, shapely.geometry.Polygon)
            assert len(shape.interiors) == 0

        geom = difference.features[0]['geometry']
        shape = shapely.geometry.shape(geom)
        assert isinstance(shape, shapely.geometry.Polygon)
        assert len(shape.interiors) == 1

    def test_fix_antimeridian(self):
        """
        Test splitting a feature that crosses the antimeridian (date line) into
        multiple polygons
        """
        globe = self.read_feature('Global_Ocean')
        fc = FeatureCollection()
        name = 'Antarctic Box'
        feature = {
            'type': 'Feature',
            'properties': {
                'name': name,
                'tags': '',
                'object': 'region',
                'component': 'ocean',
                'author': 'Xylar Asay-Davis'
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [
                            190.000000,
                            -70.000000
                        ],
                        [
                            190.000000,
                            -90.000000
                        ],
                        [
                            180.000000,
                            -90.000000
                        ],
                        [
                            170.000000,
                            -90.000000
                        ],
                        [
                            170.000000,
                            -70.000000
                        ],
                        [
                            180.000000,
                            -70.000000
                        ],
                        [
                            190.000000,
                            -70.000000
                        ]
                    ]
                ]
            }
        }
        fc.add_feature(feature=feature)
        self.check_feature(fc.features[0],
                           expected_name=name,
                           expected_type='Polygon')
        fixed = fc.fix_antimeridian()
        self.check_feature(fixed.features[0],
                           expected_name=name,
                           expected_type='MultiPolygon')

        geom = globe.features[0]['geometry']
        globe_shape = shapely.geometry.shape(geom)

        geom = fixed.features[0]['geometry']
        shape = shapely.geometry.shape(geom)
        assert isinstance(shape, shapely.geometry.MultiPolygon)
        # make sure the fixed polygons are within -180 to 180 deg. lon.
        assert shapely.covers(globe_shape, shape)

    def test_simplify(self):
        """
        Test simplifying a feature to remove redundant points
        """
        name = 'Antarctic Box'
        feature = {
            'type': 'Feature',
            'properties': {
                'name': name,
                'tags': '',
                'object': 'region',
                'component': 'ocean',
                'author': 'Xylar Asay-Davis'
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [
                            90.000000,
                            -70.000000
                        ],
                        [
                            90.000000,
                            -80.000000
                        ],
                        [
                            90.000000,
                            -80.000000
                        ],
                        [
                            70.000000,
                            -80.000000
                        ],
                        [
                            70.000000,
                            -70.000000
                        ],
                        [
                            90.000000,
                            -70.000000
                        ],
                        [
                            90.000000,
                            -70.000000
                        ]
                    ]
                ]
            }
        }
        fc = FeatureCollection()
        fc.add_feature(feature=feature)
        self.check_feature(fc.features[0],
                           expected_name=name,
                           expected_type='Polygon')

        # verify that the original shape has 7 coordinates (with 2 redundant
        # points)
        geom = fc.features[0]['geometry']
        orig_shape = shapely.geometry.shape(geom)
        assert len(orig_shape.exterior.coords) == 7

        simplified = fc.simplify(tolerance=0.0)

        # verify that the simplified shape has 5 coordinates (with the 2
        # redundant points removed)
        geom = simplified.features[0]['geometry']
        simplified_shape = shapely.geometry.shape(geom)
        assert len(simplified_shape.exterior.coords) == 5

    def test_feature_in_collection(self):
        """
        Test whether a given feature is in a feature collection
        """
        fc1 = self.read_feature()
        fc2 = self.read_feature('Aegean_Sea')

        feature = fc1.features[0]
        assert fc1.feature_in_collection(feature)

        feature = fc2.features[0]
        assert not fc1.feature_in_collection(feature)

    def test_to_geojson(self):
        """
        Test writing a feature to a geojson file and reading it back
        """
        fc = self.read_feature()
        dest_filename = str(self.datadir.join('test.geojson'))
        fc.to_geojson(dest_filename)
        fc_check = read_feature_collection(dest_filename)
        self.check_feature(fc_check.features[0])

    def test_plot(self):
        fc = self.read_feature()

        colors = ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0',
                  '#f0027f', '#bf5b17']

        projection = 'cyl'

        fig = fc.plot(projection, maxLength=4.0, figsize=(12,12),
                      colors=colors, dpi=200)

        dest_filename = str(self.datadir.join('plot.png'))
        fig.savefig(dest_filename)
