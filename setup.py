#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.1'

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
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Scientific/Engineering',
      ],
      packages=find_packages(),
      package_data={'geometric_features': ['features_and_tags.json']},
      install_requires=['numpy', 'matplotlib', 'cartopy', 'shapely',
                        'requests', 'progressbar2'],
      entry_points={})
