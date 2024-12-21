import difflib
import os

import pytest

from geometric_features.test import TestCase, loaddatadir
from geometric_features.utils import write_feature_names_and_tags


@pytest.mark.usefixtures('loaddatadir')
class TestFeaturesAndTags(TestCase):

    def test_features_and_tags(self):
        if 'GEOMETRIC_DATA_DIR' in os.environ:
            cache_location = os.environ['GEOMETRIC_DATA_DIR']
        else:
            cache_location = './geometric_data'
        write_feature_names_and_tags(cacheLocation=cache_location, quiet=True)
        assert os.path.exists('features_and_tags.json')

        filename1 = 'geometric_features/features_and_tags.json'
        filename2 = 'features_and_tags.json'
        with open(filename1, 'r') as f:
            lines1 = f.readlines()

        with open(filename2, 'r') as f:
            lines2 = f.readlines()

        diff = difflib.unified_diff(lines1, lines2, fromfile=filename1,
                                    tofile=filename2)

        count = 0
        for line in diff:
            print(line)
            count + 1

        if count != 0:
            raise ValueError(
                'Unexpected differences in geometric_features/features_and_tags.json '
                'compared with the results of geometric_features.utils.write_feature_names_and_tags()')
