from __future__ import absolute_import, division, print_function, \
    unicode_literals

from geometric_features.geometric_features import GeometricFeatures

from geometric_features.feature_collection import FeatureCollection, \
     read_feature_collection

__version_info__ = (0, 1, 10)
__version__ = '.'.join(str(vi) for vi in __version_info__)
