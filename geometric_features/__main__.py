import argparse
import os

import geometric_features
from geometric_features import GeometricFeatures
from geometric_features.feature_collection import (FeatureCollection,
                                                   read_feature_collection)


def combine_features():
    """
    Entry point for combining features from a file
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="feature file with features to be combined",
                        metavar="FILE",
                        required=True)
    parser.add_argument("-n", "--new_feature_name", dest="new_feature_name",
                        help="The new name of the combined feature",
                        metavar="NAME", required=True)
    parser.add_argument("-o", "--output", dest="output_file_name",
                        help="Output file, e.g., features.geojson.",
                        metavar="PATH", default="features.geojson")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")

    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    fc = fc.combine(args.new_feature_name)
    fc.to_geojson(args.output_file_name)


def difference_features():
    """
    Entry point for differencing features from a file
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="Feature file to be clipped", metavar="FILE1",
                        required=True)
    parser.add_argument("-m", "--mask_file", dest="mask_file",
                        help="Feature file with one or more features whose "
                             "overlap with features in feature_file should be "
                             "removed",
                        metavar="FILE2", required=True)
    parser.add_argument("-o", "--output", dest="output_file_name",
                        help="Output file, e.g., features.geojson.",
                        metavar="PATH", default="features.geojson")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")

    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    maskingFC = read_feature_collection(args.mask_file)
    fc = fc.difference(maskingFC)
    fc.to_geojson(args.output_file_name)


def fix_features_at_antimeridian():
    """
    Entry point for splitting features that cross +/- 180 degrees
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="Feature file to be clipped", metavar="FILE1",
                        required=True)
    parser.add_argument("-o", "--output", dest="output_file_name",
                        help="Output file, e.g., features.geojson.",
                        metavar="PATH", default="features.geojson")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")

    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    fc = fc.fix_antimeridian()
    fc.to_geojson(args.output_file_name)


def merge_features():
    """
    Entry point for merging features from the geometric_data cache
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="Single feature file to append to "
                             "output_file_name",
                        metavar="FILE")
    parser.add_argument("-c", "--component", dest="component",
                        help="The component (ocean, landice, etc.) from which "
                             "to retrieve the geometric features",
                        metavar="COMP")
    parser.add_argument("-b", "--object_type", dest="object_type",
                        help="The type of geometry to load, a point (0D), "
                             "transect (1D) or region (2D)",
                        metavar="TYPE")
    parser.add_argument("-n", "--feature_names", dest="feature_names",
                        help="Semicolon separated list of features",
                        metavar='"FE1;FE2;FE3"')
    parser.add_argument("-t", "--tags", dest="tags",
                        help="Semicolon separated list of tags to match "
                             "features against.", metavar='"TAG1;TAG2;TAG3"')
    parser.add_argument("-o", "--output", dest="output_file_name",
                        help="Output file, e.g., features.geojson.",
                        metavar="PATH", default="features.geojson")
    parser.add_argument("--cache", dest="cache_location",
                        help="Location of local geometric_data cache.",
                        metavar="PATH")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")

    args = parser.parse_args()

    fc = FeatureCollection()
    if os.path.exists(args.output_file_name):
        fc = read_feature_collection(args.output_file_name)
    if args.feature_file:
        fc.merge(read_feature_collection(args.feature_file))

    if args.component and args.object_type:
        gf = GeometricFeatures(args.cache_location)
        if args.feature_names:
            featureNames = args.feature_names.split(';')
        else:
            featureNames = None
        if args.tags:
            tags = args.tags.split(';')
        else:
            tags = None
        fc.merge(gf.read(args.component, args.object_type, featureNames, tags))

    fc.to_geojson(args.output_file_name)


def plot_features():
    """
    Entry point for plotting features from a file
    """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="Feature file to be clipped", metavar="FILE1",
                        required=True)
    parser.add_argument("-m", "--map_type", dest="map_type",
                        help="The map type on which to project",
                        metavar="FILE")
    parser.add_argument("--max_length", dest="max_length", type=float,
                        default=4.0,
                        help="Maximum allowed segment length after subdivision"
                        " (0.0 indicates skip subdivision)")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")

    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    if not args.map_type:
        mapTypes = ['cyl', 'merc', 'mill', 'mill2',
                    'moll', 'moll2', 'robin', 'robin2', 'ortho', 'northpole',
                    'southpole', 'atlantic', 'pacific', 'americas', 'asia']
    else:
        mapTypes = args.map_type.split(',')

    for mapType in mapTypes:
        print(f'plot type: {mapType}')
        if mapType in ['cyl', 'merc', 'mill', 'mill2', 'moll', 'moll2',
                       'robin', 'robin2']:
            figsize = (12, 6)
        else:
            figsize = (12, 9)
        fig = fc.plot(mapType, args.max_length, figsize)

        plotFileName = f'{os.path.splitext(args.feature_file)[0]}_{mapType}.png'

        fig.savefig(plotFileName)


def set_group_name():
    """
    Set the group name of the feature collection
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        required=True,
                        help="Input and output feature file where group name "
                             "is to be set", metavar="FILE")
    parser.add_argument("-g", "--group", dest="groupName",
                        help="Feature group name", metavar="GROUPNAME",
                        required=True)
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")

    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    fc.set_group_name(args.groupName)
    fc.to_geojson(args.feature_file)


def simplify_features():
    """
    Features in the collection are simplified using ``shapely``
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="Feature file to be simplified", metavar="FILE",
                        required=True)
    parser.add_argument("-t", "--tolerance", dest="tolerance", type=float,
                        default=0.0,
                        help="A distance in deg lon/lat by which each point "
                             "in a feature can be moved during simplification",
                        metavar="TOLERANCE")
    parser.add_argument("-o", "--output", dest="output_file_name",
                        help="Output file, e.g., features.geojson.",
                        metavar="PATH", default="features.geojson")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")
    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    fc = fc.simplify(args.tolerance)
    fc.to_geojson(args.output_file_name)


def split_features():
    """
    Features in the collection are split into individual files in the
    geometric_data cache
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="File containing features to split up",
                        metavar="FILE", required=True)
    parser.add_argument("-o", "--output_dir", dest="output_dir_name",
                        help="Output directory, default is determined by the "
                             "component property",
                        metavar="PATH", default="./geometric_data")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")
    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    gf = GeometricFeatures()
    gf.split(fc, args.output_dir_name)


def tag_features():
    """
    Features in the collection are tagged with the given tag(s)
    """
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-f", "--feature_file", dest="feature_file",
                        help="Features collection file to be tagged",
                        metavar="FILE", required=True)
    parser.add_argument("-t", "--tag", dest="tag",
                        help="Tag to add to all features",
                        metavar="TAG", required=True)
    parser.add_argument("-r", "--remove", dest="remove", action='store_true',
                        help="Use this flag to signal removing a tag instead "
                             "of adding")
    parser.add_argument("-o", "--output", dest="output_file_name",
                        help="Output file, e.g., features.geojson.",
                        metavar="PATH", default="features.geojson")
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'geometric_features {geometric_features.__version__}',
                        help="Show version number and exit")
    args = parser.parse_args()

    fc = read_feature_collection(args.feature_file)
    fc.tag(args.tag.split(';'), args.remove)
    fc.to_geojson(args.output_file_name)
