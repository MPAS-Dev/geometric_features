from __future__ import absolute_import, division, print_function, \
    unicode_literals

from geometric_features.geometric_features import GeometricFeatures

from geometric_features.feature_collection import FeatureCollection, \
     read_feature_collection

from geometric_features.__main__ import combine_features, difference_features, \
    fix_features_at_antimeridian, merge_features, plot_features, \
    set_group_name, split_features, simplify_features, tag_features

from geometric_features.utils import write_feature_names_and_tags


__version_info__ = (1, 4, 0)
__version__ = '.'.join(str(vi) for vi in __version_info__)
