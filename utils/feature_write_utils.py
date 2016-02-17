#!/use/bin/env python
import json
import sys

def write_all_features(features, out_file, base_indent):#{{{
	first_feature = True
	for feature in features['features']:
		if not first_feature:
			out_file.write(',\n')
		write_single_feature(feature, out_file, base_indent)
		first_feature = False
#}}}

def write_single_feature(feature, out_file, base_indent):#{{{
	# Write properties first

	out_file.write('%s{"type": "Feature",\n'%(base_indent))
	out_file.write('%s "properties": {\n'%(base_indent))

	# Write out properties
	try:
		out_file.write('%s\t"name": "%s",\n'%(base_indent, feature['properties']['name']))
	except:
		print "There was an error getting the name property from a feature. Existing...\n"
		quit(1)

	try:
		out_file.write('%s\t"component": "%s",\n'%(base_indent, feature['properties']['component']))
	except:
		print "Feature %s has an issue with the component property. Exiting...\n"%(feature['properties']['component'])
		quit(1)

	try:
		out_file.write('%s\t"tags": "%s",\n'%(base_indent, feature['properties']['tags']))
	except:
		out_file.write('%s\t"tags": "",\n'%(base_indent))

	try:
		out_file.write('%s\t"author": "%s",\n'%(base_indent, feature['properties']['author']))
	except:
		out_file.write('%s\t"author": "http://www.marineregions.org/downloads.php#iho",\n'%(base_indent))

	try:
		feature_type = feature['geometry']['type']
	except:
		print "Feature: %s has an issue with the type of geometry. Exiting...\n"%(feature['properties']['name'])
		quit(1)
	
	# Determine object property value based on feature type.
	if feature_type == "Polygon" or feature_type == "MultiPolygon":
		out_file.write('%s\t"object": "region"\n'%(base_indent))
	elif feature_type == "LineString" or feature_type == "MultiLineString":
		out_file.write('%s\t"object": "transect"\n'%(base_indent))
	elif feature_type == "Point":
		out_file.write('%s\t"object": "point"\n'%(base_indent))
		
	out_file.write('%s },\n'%(base_indent))

	# Write out geometry
	out_file.write('%s "geometry":\n'%(base_indent))
	out_file.write('%s\t{"type": "%s",\n'%(base_indent, feature_type))
	out_file.write('%s\t "coordinates":\n'%(base_indent))

	if feature_type == "MultiPolygon":
		# An array of polygons
		# Each polygon is an array of shapes
		# Each The first shape in a polygon is an array describing the vertices of the exterior of the polygon
		# Each other shape in a polygon is an array describing the vertices of each hole in the interior of the polygon
		coords_list = feature['geometry']['coordinates']

		out_file.write('%s\t\t[\n'%(base_indent))
 		out_file.write('%s\t\t\t[\n'%(base_indent))
 		write_poly_seps = False
		for poly in coords_list:
			write_shape_seps = False
			if write_poly_seps:
				out_file.write('%s\t\t\t],\n'%(base_indent))
				out_file.write('%s\t\t\t[\n'%(base_indent))
			else:
				write_poly_seps = True

			out_file.write('%s\t\t\t\t[\n'%(base_indent))
			for shape in poly:
				if write_shape_seps:
					out_file.write('%s\t\t\t\t],\n'%(base_indent))
					out_file.write('%s\t\t\t\t[\n'%(base_indent))
				else:
					write_shape_seps = True		
	 
				write_coordinates(shape, out_file, '%s\t\t\t\t\t'%(base_indent))

			out_file.write('%s\t\t\t\t]\n'%(base_indent))
 		out_file.write('%s\t\t\t]\n'%(base_indent))
		out_file.write('%s\t\t]\n'%(base_indent))

	elif feature_type == "Polygon":
		# One large array
		# Inside, any number of arrays
		# First array is an array of points representing the exterior of the polygon
		# Any after the first are arrays of points representing the holes within the polygon

		coords_list = feature['geometry']['coordinates']

		out_file.write('%s\t\t[\n'%(base_indent))
 		out_file.write('%s\t\t\t[\n'%(base_indent))
 		write_poly_seps = False
 		for shape in coords_list:
 			if write_poly_seps:
 				out_file.write('%s\t\t\t],\n'%(base_indent))
 				out_file.write('%s\t\t\t[\n'%(base_indent))
 			else:
 				write_poly_seps = True		
 
 			write_coordinates(shape, out_file, '%s\t\t\t\t'%(base_indent))
 		out_file.write('%s\t\t\t]\n'%(base_indent))
		out_file.write('%s\t\t]\n'%(base_indent))

	elif feature_type == "MultiLineString":
		# An array of lines
		# Each line is an array of coordinates for each line segment
		coords_list = feature['geometry']['coordinates']

		out_file.write('%s\t\t[\n'%(base_indent))
 		out_file.write('%s\t\t\t[\n'%(base_indent))
 		write_line_seps = False
 		for line in coords_list:
 			if write_line_seps:
 				out_file.write('%s\t\t\t],\n'%(base_indent))
 				out_file.write('%s\t\t\t[\n'%(base_indent))
 			else:
 				write_line_seps = True		
 
 			write_coordinates(line, out_file, '%s\t\t\t\t'%(base_indent))
 		out_file.write('%s\t\t\t]\n'%(base_indent))
		out_file.write('%s\t\t]\n'%(base_indent))

	elif feature_type == "LineString":
		# An single line
		# Made up of an array of points
		coords_list = feature['geometry']['coordinates']

		out_file.write('%s\t\t[\n'%(base_indent))
 		write_coordinates(coords_list, out_file, '%s\t\t\t'%(base_indent))
		out_file.write('%s\t\t]\n'%(base_indent))

	elif feature_type == "Point":
		coords_list = feature['geometry']['coordinates']
		out_file.write('%s\t[ %f, %f]\n'%(base_indent, coords_list[0], coords_list[1]))
	else:
		print "ERROR: Unsupported feature type: %s"%(feature_type)
		sys.exit(1)

	out_file.write('%s\t}\n'%(base_indent))
	out_file.write('%s}'%(base_indent))

#}}}

def write_coordinates(coords, out_file, base_indent):#{{{
	write_comma = False
	for coord in coords:
		if write_comma:
			out_file.write(',\n')
		else:
			write_comma = True

		out_file.write('%s[ %f, %f]'%(base_indent, coord[0], coord[1]))

	out_file.write('\n')
#}}}
