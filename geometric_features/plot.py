import cartopy.crs
import cartopy.feature
import matplotlib.pyplot as plt
import numpy as np
import shapely


def build_projections():
    """
    Create a list of projections for plotting features. Possible map types are
    'cyl', 'merc', 'mill', 'mill2', 'moll', 'moll2', 'robin', 'robin2',
    'ortho', 'northpole', 'southpole', 'atlantic', 'pacific', 'americas',
    'asia'
    """
    projections = dict()
    projections['cyl'] = cartopy.crs.PlateCarree()
    projections['merc'] = cartopy.crs.Mercator()
    projections['mill'] = cartopy.crs.Miller()
    projections['mill2'] = cartopy.crs.Miller(central_longitude=180.)
    projections['moll'] = cartopy.crs.Mollweide()
    projections['moll2'] = cartopy.crs.Mollweide(central_longitude=180.)
    projections['robin'] = cartopy.crs.Robinson()
    projections['robin2'] = cartopy.crs.Robinson(central_longitude=180.)

    projections['ortho'] = cartopy.crs.Orthographic(central_longitude=-100.,
                                                    central_latitude=45.)
    projections['northpole'] = cartopy.crs.Orthographic(central_longitude=0.,
                                                        central_latitude=90.)
    projections['southpole'] = cartopy.crs.Orthographic(central_longitude=0.,
                                                        central_latitude=-90.)
    projections['atlantic'] = cartopy.crs.Orthographic(central_longitude=0.,
                                                       central_latitude=0.)
    projections['pacific'] = cartopy.crs.Orthographic(central_longitude=180.,
                                                      central_latitude=0.)
    projections['americas'] = cartopy.crs.Orthographic(central_longitude=-90.,
                                                       central_latitude=0.)
    projections['asia'] = cartopy.crs.Orthographic(central_longitude=90.,
                                                   central_latitude=0.)

    return projections


def plot_base(mapType, projection):
    """
    Plot the background map on which to plot a feature collection
    """
    # Authors
    # -------
    # Xylar Asay-Davis, `Phillip J. Wolfram

    ax = plt.axes(projection=projection)
    resolution = '50m'

    ax.add_feature(cartopy.feature.NaturalEarthFeature(
        'physical', 'land', resolution, edgecolor='face',
        facecolor=cartopy.feature.COLORS['land']), zorder=1)

    ax.add_feature(cartopy.feature.NaturalEarthFeature(
        'physical', 'coastline', resolution,
        edgecolor='black', facecolor='none'), zorder=2)

    draw_labels = mapType in ['merc', 'cyl']

    ax.gridlines(crs=cartopy.crs.PlateCarree(), draw_labels=draw_labels,
                 linewidth=0.5, color='gray', linestyle='--')

    return ax, projection


def subdivide_geom(geometry, geomtype, maxLength):
    """
    Subdivide the line segments for a given set of geometry so plots are
    smoother
    """
    # Authors
    # -------
    # Xylar Asay-Davis, `Phillip J. Wolfram

    def subdivide_line_string(lineString, periodic=False):
        coords = list(lineString.coords)
        if periodic:
            # add periodic last entry
            coords.append(coords[0])

        outCoords = [coords[0]]
        for iVert in range(len(coords)-1):
            segment = shapely.geometry.LineString([coords[iVert],
                                                   coords[iVert+1]])
            if segment.length < maxLength:
                outCoords.append(coords[iVert+1])
            else:
                # we need to subdivide this segment
                subsegment_count = int(np.ceil(segment.length/maxLength))
                for index in range(subsegment_count):
                    point = segment.interpolate(
                        float(index+1)/float(subsegment_count),
                        normalized=True)
                    outCoords.append(point.coords[0])

        if periodic:
            # remove the last entry
            outCoords.pop()
        return outCoords

    if geomtype == 'LineString':
        newGeometry = shapely.geometry.LineString(
            subdivide_line_string(geometry))
    elif geomtype == 'MultiLineString':
        outStrings = [subdivide_line_string(inLineString) for inLineString
                      in geometry]
        newGeometry = shapely.geometry.MultiLineString(outStrings)
    elif geomtype == 'Polygon':
        exterior = subdivide_line_string(geometry.exterior, periodic=True)
        interiors = [subdivide_line_string(inLineString, periodic=True)
                     for inLineString in geometry.interiors]
        newGeometry = shapely.geometry.Polygon(exterior, interiors)
    elif geomtype == 'MultiPolygon':
        polygons = []
        for polygon in geometry.geoms:
            exterior = subdivide_line_string(polygon.exterior, periodic=True)
            interiors = [subdivide_line_string(inLineString, periodic=True)
                         for inLineString in polygon.interiors]
            polygons.append((exterior, interiors))

        newGeometry = shapely.geometry.MultiPolygon(polygons)
    elif geomtype == 'Point':
        newGeometry = geometry
    else:
        print(f"Warning: subdividing geometry type {geomtype} is not supported.")
        newGeometry = geometry

    return newGeometry
