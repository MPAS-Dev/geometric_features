#!/usr/bin/env python

import os
import re
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'geometric_features', '__init__.py')) as f:
    init_file = f.read()

version = re.search(r'{}\s*=\s*[(]([^)]*)[)]'.format('__version_info__'),
                    init_file).group(1).replace(', ', '.')

setup(name='geometric_features',
      version=version,
      description='Tools for manipulating regions, transects, and points '
                  'in geojson format associated with climate modeling.',
      url='https://github.com/MPAS-Dev/geometric_features',
      author='MPAS-Analysis Developers',
      author_email='mpas-developers@googlegroups.com',
      license='BSD',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Topic :: Scientific/Engineering',
      ],
      packages=find_packages(include=['geometric_features',
                                      'geometric_features.*']),
      package_data={'geometric_features': ['features_and_tags.json']},
      install_requires=['numpy', 'matplotlib', 'cartopy', 'shapely',
                        'requests', 'progressbar2'],
      entry_points={'console_scripts':
                    ['combine_features = '
                     'geometric_features.__main__:combine_features',
                     'difference_features = '
                     'geometric_features.__main__:difference_features',
                     'fix_features_at_antimeridian = '
                     'geometric_features.__main__:fix_features_at_antimeridian',
                     'merge_features = '
                     'geometric_features.__main__:merge_features',
                     'plot_features = '
                     'geometric_features.__main__:plot_features',
                     'set_group_name = '
                     'geometric_features.__main__:set_group_name',
                     'simplify_features = '
                     'geometric_features.__main__:simplify_features',
                     'split_features = '
                     'geometric_features.__main__:split_features',
                     'tag_features = '
                     'geometric_features.__main__:tag_features']})
