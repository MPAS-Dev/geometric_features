from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json
import os

from importlib.resources import files as imp_res_files

import geometric_features

from geometric_features.feature_collection import FeatureCollection, \
    read_feature_collection

from geometric_features.download import download_files


class GeometricFeatures(object):
    """
    An object for keeping track of where geometric features are cached and
    downloading missing features as needed.

    Attributes
    ----------
    allFeaturesAndTags : dict of dict
        A cache of all the feature names and tags in the ``geometric_features``
        repo used to determine which features need to be downloaded into the
        local cache

    remoteBranch : str, optional
        The branch or tag from the ``geometric_features`` repo to download
        from if files are missing from the local cache

    """
    # Authors
    # -------
    # Xylar Asay-Davis

    def __init__(self, cacheLocation=None, remoteBranchOrTag=None):
        """
        The constructor for the GeometricFeatures object

        Parameters
        ----------
        cacheLocation : str, optional
            The location of the local geometric features cache.  If not
            specified, the environment variable ``$GEOMETRIC_DATA_DIR`` is
            used if it is set and ``./geometric_data`` is used otherwise.

        remoteBranchOrTag : str, optional
            The branch or tag from the ``geometric_features`` repo to download
            from if files are missing from the local cache, with default to
            a tag the same as this version of ``geometric_features``
        """

        if cacheLocation is None:
            if 'GEOMETRIC_DATA_DIR' in os.environ:
                self.cacheLocation = os.environ['GEOMETRIC_DATA_DIR']
            else:
                self.cacheLocation = './geometric_data'
        else:
            self.cacheLocation = cacheLocation
        if remoteBranchOrTag is None:
            self.remoteBranch = geometric_features.__version__
        else:
            self.remoteBranch = remoteBranchOrTag

        features_file = (imp_res_files('geometric_features') /
                         'features_and_tags.json')
        with features_file.open('r') as file:
            self.allFeaturesAndTags = json.load(file)

    def read(self, componentName, objectType, featureNames=None, tags=None,
             allTags=True):
        """
        Read one or more features from the cached collection of geometric
        features. If any of the requested features have not been cached, they
        are downloaded from the ``geometric_features`` GitHub repository.  If
        neither ``featureNames`` nor ``tags`` are specified, all features of
        the component and object type are read in.

        Parameters
        ----------
        componentName : {'bedmachine', 'bedmap2', 'iceshelves', 'landice', 
        'natural_earth', 'ocean','seaice'}
            The component from which to retrieve the geometric features

        objectType : {'point', 'transect', 'region'}
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        featureNames : list of str, optional
            The names of geometric features to read

        tags : list of str, optional
            A list of tags to check for.  When ``allTags=True``, a feature is
            only read in if it has all tags.  Otherwise, features with any of
            the tags are read.

        allTags : bool, optional
            Whether a feature must have all tags (instead of any of the tags)

        Returns
        -------
        fc : geometric_features.FeatureCollection
            The feature collection read in
        """
        # Authors
        # -------
        # Xylar Asay-Davis

        featureNames = self._get_feature_names(componentName, objectType,
                                               featureNames, tags, allTags)
        fileList = self._download_geometric_features(componentName, objectType,
                                                     featureNames)

        fc = FeatureCollection()
        for fileName in fileList:
            fc.merge(read_feature_collection(fileName))

        return fc

    def split(self, fc, destinationDir=None):
        """
        Split a feature collection into individual files for each feature. This
        is how new geometry should be added to the ``geometric_features`` repo.

        Parameters
        ----------
        fc : geometric_features.FeatureCollection
            The feature collection to split

        destinationDir : str, optional
            The root path where the split geometry will be stored,
            ``cacheLocation`` by default

        Returns
        -------
        fc : geometric_features.FeatureCollection
            The feature collection read in
        """
        # Authors
        # -------
        # Xylar Asay-Davis

        if destinationDir is None:
            destinationDir = self.cacheLocation

        for feature in fc.features:
            featureName = feature['properties']['name']
            componentName = feature['properties']['component']
            objectType = feature['properties']['object']

            relativePath = _get_file_name(componentName, objectType,
                                          featureName)
            fullPath = os.path.join(destinationDir, relativePath)

            path, file = os.path.split(fullPath)

            try:
                os.makedirs(path)
            except OSError:
                pass

            singleFC = FeatureCollection([feature])
            singleFC.otherProperties.pop('groupName', None)

            singleFC.to_geojson(fullPath, stripHistory=True)

    def _download_geometric_features(self, componentName, objectType,
                                     featureNames):
        """
        Determine a list of requested files and download the any that are
        missing from the repo

        Parameters
        ----------
        componentName : {'bedmachine', 'bedmap2', 'iceshelves', 'landice', 
        'natural_earth', 'ocean','seaice'}
            The component from which to retrieve the geometric features

        objectType : {'point', 'transect', 'region'}
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        featureNames : list of str
            The names of geometric features to read

        Returns
        -------
        fileList : list of str
            File names of the features


        """
        # Authors
        # -------
        # Xylar Asay-Davis
        try:
            os.makedirs(self.cacheLocation)
        except OSError:
            pass

        fileList = []
        filesToDownload = []
        for featureName in featureNames:
            relativePath = _get_file_name(componentName, objectType,
                                          featureName)
            fullPath = os.path.join(self.cacheLocation, relativePath)
            fileList.append(fullPath)
            if not os.path.exists(fullPath):
                filesToDownload.append(relativePath)

        if len(filesToDownload) > 0:
            baseURL = 'https://raw.githubusercontent.com/MPAS-Dev/' \
                'geometric_features/{}/geometric_data'.format(
                    self.remoteBranch)
            download_files(filesToDownload, baseURL, self.cacheLocation)

        return fileList

    def _get_feature_names(self, componentName, objectType, featureNames,
                           tags, allTags):
        """
        Find features by name or tags, reporting errors in the process

        Parameters
        ----------
        componentName : {'bedmachine', 'bedmap2', 'iceshelves', 'landice', 
        'natural_earth', 'ocean','seaice'}
            The component from which to retrieve the geometric features

        objectType : {'point', 'transect', 'region'}
            The type of geometry to load, a point (0D), transect (1D) or region
            (2D)

        featureNames : list of str
            The names of geometric features to read

        tags : list of str
            A list of tags to check for.  A feature is only read in if it has
            all tags.

        allTags : bool, optional
            Whether a feature must have all tags (instead of any of the tags)

        Returns
        -------
        featureNames : list of str
            The names of features found either explicitly by name or by tags

        Raises
        ------
        KeyError
            If the component is not in the geometric features repo, if the
            object type is not in the component, or if one or more feature
            names are not found
        """
        # Authors
        # -------
        # Xylar Asay-Davis

        if componentName not in self.allFeaturesAndTags:
            raise KeyError('invalid component {}'.format(componentName))

        component = self.allFeaturesAndTags[componentName]

        if objectType not in component:
            raise KeyError('invalid object {} in component {}'.format(
                objectType, componentName))

        availableFeaturesAndTags = component[objectType]

        if featureNames is None and tags is None:
            outFeatureNames = list(availableFeaturesAndTags.keys())

        else:
            outFeatureNames = []
            if featureNames is not None:
                for featureName in featureNames:
                    if featureName not in availableFeaturesAndTags:
                        raise KeyError('invalid feature {}'.format(
                            featureName))
                    outFeatureNames.append(featureName)

            if tags is not None:
                if allTags:
                    op = all
                else:
                    op = any
                for featureName in availableFeaturesAndTags:
                    featureTags = availableFeaturesAndTags[featureName]
                    if op([tag in featureTags for tag in tags]):
                        outFeatureNames.append(featureName)
        return outFeatureNames


def _get_file_name(componentName, objectType, featureName):
    """
    Get the relative path of a cached geometric feature from its component,
    object type and feature name.

    Parameters
    ----------
    componentName : {'bedmachine', 'bedmap2', 'iceshelves', 'landice', 
    'natural_earth', 'ocean','seaice'}
        The component from which to retrieve the geometric features

    objectType : {'point', 'transect', 'region'}
        The type of geometry to load, a point (0D), transect (1D) or region
        (2D)

    featureName : str
        The names of a geometric feature

    Returns
    -------
    fileName : str
        The relative path to that feature
    """
    # Authors
    # -------
    # Douglas Jacobsen, Xylar Asay-Davis

    badCharacters = '<>:"/\\|?*\',;'
    featureDir = featureName.strip().replace(' ', '_').strip('.')
    for char in badCharacters:
        featureDir = featureDir.replace(char, '')
    fileName = os.path.join(componentName, objectType, featureDir,
                            '{}.geojson'.format(objectType))

    return fileName
