from __future__ import absolute_import, division, print_function, \
    unicode_literals

import json
from collections import OrderedDict
import shapely.geometry
import shapely.ops
import cartopy
import matplotlib.pyplot as plt
import numpy as np
import progressbar
import copy

from geometric_features.utils import provenance_command

from geometric_features.plot import build_projections, subdivide_geom, \
    plot_base


def read_feature_collection(fileName):
    '''
    Read a feature collection from a geojson file.

    Parameters
    ----------
    fileName : str
        The path to the geojson file

    Returns
    -------
    fc : ``FeatureCollection``
        The feature collection read in
    '''
    # Authors
    # -------
    # Xylar Asay-Davis
    fc = FeatureCollection()
    with open(fileName) as f:
        featuresDict = json.load(f)
        for feature in featuresDict['features']:
            fc.add_feature(feature)
        for key in sorted(list(featuresDict.keys())):
            if key not in ['features', 'type']:
                fc.otherProperties[key] = featuresDict[key]
    return fc


class FeatureCollection(object):
    '''
    An object for representing and manipulating a collection of geoscientific
    geometric features.

    Attributes
    ----------
    features : list of dict
        A list of python dictionaries describing each feature, following the
        geojson convention

    otherProperties : dict
        Other properties of the feature collection such as ``type`` and
        ``groupName``
    '''
    # Authors
    # -------
    # Xylar Asay-Davis

    def __init__(self, features=None, otherProperties=None):
        '''
        Construct a new feature collection

        Parameteres
        -----------
        features : list of dict, optional
            A list of python dictionaries describing each feature, following
            the geojson convention

        otherProperties : dict
            Other properties of the feature collection such as ``type`` and
            ``groupName``
        '''
        # Authors
        # -------
        # Xylar Asay-Davis
        if features is None:
            self.features = []
        else:
            self.features = features
        self.otherProperties = OrderedDict()
        self.otherProperties['type'] = 'FeatureCollection'
        self.otherProperties['groupName'] = 'enterGroupName'
        if otherProperties is not None:
            self.otherProperties.update(otherProperties)

    def add_feature(self, feature):
        '''
        Add a feature to the feature collection if it isn't alerady present

        Parameters
        ----------
        feature : dict
            The feature to add
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        feature = _validate_feature(feature)
        if not self.feature_in_collection(feature):
            self.features.append(feature)

    def merge(self, other):
        '''
        Merge another feature collection into this one

        Parameters
        ----------
        other : ``FeatureCollection``
            The other feature collection
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        for feature in other.features:
            self.add_feature(feature)

        for key in sorted(list(other.otherProperties.keys())):
            if key not in ['features', 'type'] and key not in \
                    self.otherProperties:
                self.otherProperties[key] = other.otherProperties[key]

    def tag(self, tags, remove=False):
        '''
        Add tags to all features in the collection

        Parameters
        ----------
        tags : list of str
            Tags to be added
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        for feature in self.features:
            featureTags = feature['properties']['tags'].split(';')
            for tag in tags:
                if remove and tag in featureTags:
                    featureTags.pop(tag)
                elif not remove and tag not in featureTags:
                    featureTags.append(tag)
            feature['properties']['tags'] = ';'.join(featureTags)

    def set_group_name(self, groupName):
        '''
        Set the group name of a feature collection

        Parameters
        ----------
        groupName : str
            The group name
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        self.otherProperties['groupName'] = groupName

    def combine(self, featureName):
        '''
        Combines the geometry of the feature collection into a single feature

        Parameters
        ----------
        featureName : str
            The name of the new, combined feature

        Returns
        -------
        fc : ``FeatureCollection``
            A new feature collection with a single feature with the combined
            geometry

        Raises
        ------
        ValueError
           If the combined geometry is of an unsupported type (typically
           ``GeometryCollection``)
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        featureShapes = []
        authors = []
        featureNames = []
        for feature in self.features:
            featureShapes.append(shapely.geometry.shape(feature['geometry']))
            authors.append(feature['properties']['author'])
            featureNames.append(feature['properties']['name'])

        combinedShape = shapely.ops.cascaded_union(featureShapes)

        geometry = shapely.geometry.mapping(combinedShape)

        try:
            objectType = _get_geom_object_type(geometry['type'])
        except KeyError:
            raise ValueError('combined geometry is of unsupported type '
                             '{}. Most likely cause is that '
                             'multiple feature types (regions, points and '
                             'transects) are being cobined.'.format(
                                 geometry['type']))

        feature = {}
        feature['properties'] = {}
        feature['properties']['name'] = featureName
        feature['properties']['component'] = \
            self.features[0]['properties']['component']
        feature['properties']['object'] = objectType
        feature['properties']['tags'] = ''
        feature['properties']['author'] = '; '.join(list(set(authors)))
        feature['properties']['constituents'] = \
            '; '.join(list(set(featureNames)))
        feature['geometry'] = geometry

        fc = FeatureCollection([feature])
        return fc

    def difference(self, maskingFC):
        '''
        Use features from a masking collection to mask out (remove part of
        the geometry from) this collection.

        Parameters
        ----------
        maskingFC : ``FeatureCollection```
            Another collection of one or more features to use as masks

        Returns
        -------
        fc : ``FeatureCollection``
            A new feature collection with a single feature with the geometry
            masked
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        featureCount = len(self.features)
        maskCount = len(maskingFC.features)

        totalCount = featureCount*maskCount

        print('Masking features...')
        widgets = ['', progressbar.Percentage(), ' ', progressbar.Bar(),
                   ' ', progressbar.ETA()]
        bar = progressbar.ProgressBar(widgets=widgets,
                                      maxval=totalCount).start()

        maskedFeatures = []
        maskedCount = 0
        droppedCount = 0
        for featureIndex, feature in enumerate(self.features):
            name = feature['properties']['name']
            widgets[0] = '{}: '.format(name)
            featureShape = shapely.geometry.shape(feature['geometry'])
            add = True
            masked = False
            for maskIndex, maskFeature in enumerate(maskingFC.features):
                bar.update(maskIndex + featureIndex*maskCount)
                maskShape = shapely.geometry.shape(maskFeature['geometry'])
                if featureShape.intersects(maskShape):
                    masked = True
                    featureShape = featureShape.difference(maskShape)
                    if featureShape.is_empty:
                        add = False
                        break

            if(add):
                newFeature = copy.deepcopy(feature)
                if(masked):
                    maskedCount += 1
                    newFeature['geometry'] = \
                        shapely.geometry.mapping(featureShape)
                maskedFeatures.append(newFeature)
            else:
                droppedCount += 1

        bar.finish()

        print('  {} features unchanged, {} masked and {} dropped.'.format(
            featureCount - maskedCount - droppedCount, maskedCount,
            droppedCount))

        fc = FeatureCollection(maskedFeatures, self.otherProperties)
        return fc

    def fix_antimeridian(self):
        '''
        Split features at +/-180 degrees (the antimeridian) to make them valid
        geojson geometries

        Returns
        -------
        fc : ``FeatureCollection``
            A new feature collection with the antimeridian handled correctly
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        newFeatures = []
        for feature in self.features:
            geometry = _split_geometry_crossing_antimeridian(
                feature['geometry'])
            if geometry is None:
                # no change
                newFeature = OrderedDict(feature)
            else:
                newFeature = OrderedDict()
                newFeature['properties'] = OrderedDict(feature['properties'])
                newFeature['geometry'] = geometry
            newFeatures.append(newFeature)

        fc = FeatureCollection(newFeatures, self.otherProperties)
        return fc

    def simplify(self, tolerance=0.0):
        '''
        Features in the collection are simplified using ``shapely``

        Parameters
        ----------
        tolerance : float, optional
            The tolerance in degrees lon/lat allowed when simplifying shapes

        Returns
        -------
        fc : ``FeatureCollection``
            A new feature collection with simplified geometries
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        newFeatures = []
        for feature in self.features:
            featureShape = shapely.geometry.shape(feature['geometry'])
            simplifiedFeature = featureShape.simplify(tolerance)
            newFeature = copy.deepcopy(feature)
            newFeature['geometry'] = \
                shapely.geometry.mapping(simplifiedFeature)
            newFeatures.append(newFeature)

        fc = FeatureCollection(newFeatures, self.otherProperties)
        return fc

    def feature_in_collection(self, feature):
        '''
        Is this feature already in the collection?

        Parameters
        ----------
        feature : dict
            The feature to check

        Returns
        -------
        inCollection : bool
            Whether the feature is in the collection
        '''
        # Authors
        # -------
        # Xylar Asay-Davis

        featureNames = [f['properties']['name'] for f in self.features]
        return feature['properties']['name'] in featureNames

    def to_geojson(self, fileName, stripHistory=False, indent=4):
        '''
        Write the feature collection to a geojson file

        Parameters
        ----------
        fileName : str
            A geojson file to write to

        stripHistory : bool, optional
            Whether to remove the history attribute (e.g. when splitting
            features for inclusion in the ``geometric_features`` repo)

        indent : int, optional
            The number of spaces to use for indentation when formatting the
            geojson file
        '''
        # Authors
        # -------
        # Douglas Jacobsen, Xylar Asay-Davis, Phillip J. Wolfram

        outFeatures = OrderedDict(self.otherProperties)
        # features go last for readability
        outFeatures['features'] = copy.deepcopy(self.features)

        if stripHistory:
            # remove provenance from the output
            for feature in outFeatures['features']:
                # pop (with default so no exception is raised if no history)
                feature['properties'].pop('history', None)
        else:
            # provenance the output
            command = provenance_command()
            for feature in outFeatures['features']:
                if 'history' in feature['properties']:
                    history = feature['properties']['history'] + ' ' + command
                    feature['properties']['history'] = history
                else:
                    feature['properties']['history'] = command

        outFile = open(fileName, 'w')

        for feature in outFeatures['features']:
            feature['geometry']['coordinates'] = \
                _round_coords(feature['geometry']['coordinates'])

        json.dump(outFeatures, outFile, indent=indent)

    def plot(self, projection, maxLength=4.0, figsize=None, colors=None,
             dpi=200):
        '''
        Plot the features on a map using cartopy.

        Parameters
        ----------
        projection : str or ``cartopy.crs.Projection``
            A cartopy projection object or one of the internally defined
            map names:

                'cyl', 'merc', 'mill', 'mill2', 'moll', 'moll2', 'robin',
                'robin2', 'ortho', 'northpole', 'southpole', 'atlantic',
                'pacific', 'americas', 'asia'

        maxLength : float, optional
            Maximum allowed segment length after subdivision for smoother
            plotting (0.0 indicates skip subdivision)

        figsize : tuple of float
            Size of the figure in inches

        colors : list of str
            Colors to cycle through for the shapes

        dpi : int
            Dots per inch for the figure

        Returns
        -------
        fig : ``matplotlib.figure.Figure``
            The figure
        '''
        # Authors
        # -------
        # Xylar Asay-Davis, `Phillip J. Wolfram

        projectionName = 'custom'

        if isinstance(projection, str):
            projections = build_projections()
            projectionName = projection
            projection = projections[projectionName]

        if figsize is None:
            if projectionName in ['cyl', 'merc', 'mill', 'mill2', 'moll',
                                  'moll2', 'robin', 'robin2']:
                figsize = (12, 6)
            else:
                figsize = (12, 9)

        fig = plt.figure(figsize=figsize, dpi=dpi)
        (ax, projection) = plot_base(projectionName, projection)

        if colors is None:
            # use colorbrewer qualitative 7 data class colors,
            # "7-class Accent": http://colorbrewer2.org/
            colors = ['#7fc97f', '#beaed4', '#fdc086', '#ffff99', '#386cb0',
                      '#f0027f', '#bf5b17']

        bounds = None

        for featureIndex, feature in enumerate(self.features):
            geomType = feature['geometry']['type']
            shape = shapely.geometry.shape(feature['geometry'])
            if(maxLength > 0.0):
                shape = subdivide_geom(shape, geomType, maxLength)

            refProjection = cartopy.crs.PlateCarree()

            color = colors[featureIndex % len(colors)]

            if geomType in ['Polygon', 'MultiPolygon']:
                props = {'linewidth': 2.0, 'edgecolor': color, 'alpha': 0.4,
                         'facecolor': color}
            elif geomType in ['LineString', 'MultiLineString']:
                props = {'linewidth': 4.0, 'edgecolor': color, 'alpha': 1.,
                         'facecolor': 'none'}

            if bounds is None:
                bounds = list(shape.bounds)
            else:
                # expand the bounding box
                bounds[:2] = np.minimum(bounds[:2], shape.bounds[:2])
                bounds[2:] = np.maximum(bounds[2:], shape.bounds[2:])

            if geomType == 'Point':
                ax.scatter(shape.coords[0][0], shape.coords[0][1], s=9,
                           transform=cartopy.crs.PlateCarree(), marker='o',
                           color='blue', edgecolor='blue')
            else:
                ax.add_geometries((shape,), crs=refProjection, **props)

        box = shapely.geometry.box(*bounds)
        if(maxLength > 0.0):
            box = subdivide_geom(box, 'Polygon', maxLength)

        boxProjected = projection.project_geometry(box, src_crs=refProjection)
        try:
            x1, y1, x2, y2 = boxProjected.bounds
            ax.set_xlim([x1, x2])
            ax.set_ylim([y1, y2])
        except ValueError:
            print("Warning: bounding box could not be projected into "
                  "projection {}".format(projectionName))
            print("Defaulting to global bounds.")
            ax.set_global()

        fig.canvas.draw()
        plt.tight_layout(pad=4.)

        return fig


def _get_geom_object_type(geomType):
    '''
    Get the object type for a given geometry type
    '''
    geomObjectTypes = {'Polygon': 'region',
                       'MultiPolygon': 'region',
                       'LineString': 'transect',
                       'MultiLineString': 'transect',
                       'Point': 'point',
                       'MultiPoint': 'point'}
    return geomObjectTypes[geomType]


def _validate_feature(feature):
    '''
    Validate the geometric feature to ensure that it has all required keys:
        - properties
          - name
          - tags
          - object
          - component
          - author
        - geometry
          - type
          - coordinates

    Parameters
    ----------
    feature : dict
        The feature to check

    Raises
    ------
    KeyError
        If the feature is missing required keys

    ValueError
        If the geometry type doesn't match the object type
    '''
    # Authors
    # -------
    # Xylar Asay-Davis, Phillip J. Wolfram

    required = {
        'properties': ['name', 'object', 'component'],
        'geometry': ['type', 'coordinates']}

    try:
        name = feature['properties']['name']
    except KeyError:
        name = 'unknown'
    for outerKey in required:
        if outerKey not in feature:
            raise KeyError('Feature {} missing [{}] key'.format(
                name, outerKey))
        for innerKey in required[outerKey]:
            if innerKey not in feature[outerKey]:
                raise KeyError('Feature {} missing [{}][{}] key'.format(
                    name, outerKey, innerKey))

    geomType = feature['geometry']['type']
    objectType = feature['properties']['object']
    if _get_geom_object_type(geomType) != objectType:
        raise ValueError('Object type {} and geometry type {} '
                         'are incompatible'.format(objectType, geomType))

    if 'author' in feature['properties']:
        author = feature['properties']['author']
    else:
        author = ''

    if 'tags' in feature['properties']:
        tags = feature['properties']['tags']
    else:
        tags = ''

    # Make the properties an ordered dictionary so they can be sorted
    outProperties = OrderedDict(
            (('name', feature['properties']['name']),
             ('tags', tags),
             ('object', feature['properties']['object']),
             ('component', feature['properties']['component']),
             ('author', author)))
    for key in sorted(feature['properties']):
        if key not in outProperties.keys():
            outProperties[key] = feature['properties'][key]

    # Make the geometry an ordered dictionary so they can keep it in the
    # desired order
    outGeometry = OrderedDict(
        (('type', feature['geometry']['type']),
         ('coordinates', feature['geometry']['coordinates'])))
    for key in sorted(feature['geometry']):
        if key not in outGeometry.keys():
            outGeometry[key] = feature['geometry'][key]

    # Make the feature an ordered dictionary so properties come before geometry
    # (easier to read)
    outFeature = OrderedDict((('type', 'Feature'),
                             ('properties', outProperties)))
    # Add the rest
    for key in sorted(feature):
        if key not in ['geometry', 'type', 'properties']:
            outFeature[key] = feature[key]

    # geometry goes last for readability
    outFeature['geometry'] = outGeometry

    return outFeature


def _split_geometry_crossing_antimeridian(geometry):
    def _to_polar(lon, lat):
        phi = np.pi/180.*(np.mod(lon + 180., 360.) - 180.)
        radius = np.pi/180.*(90. - sign*lat)

        # nudge points at +/- 180 out of the way so they don't intersect the
        # testing wedge
        phi = np.sign(phi) * \
            np.where(np.abs(phi) > np.pi - 1.5*epsilon,
                     np.pi - 1.5*epsilon, np.abs(phi))
        # radius = np.where(radius < 1.5*epsilon, 1.5*epsilon, radius)

        x = radius*np.sin(phi)
        y = radius*np.cos(phi)
        if(isinstance(lon, list)):
            x = x.tolist()
            y = y.tolist()
        elif(isinstance(lon, tuple)):
            x = tuple(x)
            y = tuple(y)

        return (x, y)

    def _from_polar(x, y):
        radius = np.sqrt(np.array(x)**2+np.array(y)**2)
        phi = np.arctan2(x, y)

        # close up the tiny gap
        radius = np.where(radius < 2*epsilon, 0., radius)
        phi = np.sign(phi) * \
            np.where(np.abs(phi) > np.pi - 2*epsilon,
                     np.pi, np.abs(phi))

        lon = 180./np.pi*phi
        lat = sign*(90. - 180./np.pi*radius)

        if(isinstance(x, list)):
            lon = lon.tolist()
            lat = lat.tolist()
        elif(isinstance(x, tuple)):
            lon = tuple(lon)
            lat = tuple(lat)
        return (lon, lat)

    epsilon = 1e-14
    antimeridianWedge = shapely.geometry.Polygon([(epsilon, -np.pi),
                                                  (epsilon**2, -epsilon),
                                                  (0, epsilon),
                                                  (-epsilon**2, -epsilon),
                                                  (-epsilon, -np.pi),
                                                  (epsilon, -np.pi)])

    featureShape = shapely.geometry.shape(geometry)
    sign = (2.*(0.5*(featureShape.bounds[1] + featureShape.bounds[3]) >= 0.) -
            1.)
    polarShape = shapely.ops.transform(_to_polar, featureShape)

    if(not polarShape.intersects(antimeridianWedge)):
        # this feature doesn't corss the antimeridian
        return

    difference = polarShape.difference(antimeridianWedge)

    outShape = shapely.ops.transform(_from_polar, difference)

    return shapely.geometry.mapping(outShape)


def _round_coords(coordinates, digits=6):
    '''
    Round the coordinates of geojson geometry data before writing to a file
    '''
    if isinstance(coordinates, float):
        return round(coordinates, digits)
    if isinstance(coordinates, int):
        return float(coordinates)
    elif isinstance(coordinates, list):
        return [_round_coords(c, digits) for c in coordinates]
    elif isinstance(coordinates, tuple):
        return tuple([_round_coords(c, digits) for c in coordinates])
    else:
        raise TypeError('Unexpected type for coordinates {}'.format(
                coordinates))
