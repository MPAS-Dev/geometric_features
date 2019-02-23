from __future__ import absolute_import, division, print_function, \
    unicode_literals

import geometric_features

import argparse
import sys


def main():
    """
    Entry point for the main script ``geometric_features``
    """

    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version',
                        action='version',
                        version='mpas_analysis {}'.format(
                                geometric_features.__version__),
                        help="Show version number and exit")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()

# vim: foldmethod=marker ai ts=4 sts=4 et sw=4 ft=python
