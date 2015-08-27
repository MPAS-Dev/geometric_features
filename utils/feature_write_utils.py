#!/use/bin/env python
import json

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

	if not feature_type == "Point":
		out_file.write('%s\t\t[\n'%(base_indent))

	if feature_type == "MultiPolygon" or feature_type == "MultiLineString":
		out_file.write('%s\t\t\t[\n'%(base_indent))
		indentation = '%s\t\t\t\t'%(base_indent)
		poly_list = feature['geometry']['coordinates']
	elif feature_type == "Point":
		indentation = '\t\t\t'
		poly_list = []
		point_list = []
		point_list.append(feature['geometry']['coordinates'])
		poly_list.append(point_list)
		del point_list
	else:
		indentation = '\t\t\t'
		poly_list = []
		poly_list.append(feature['geometry']['coordinates'])

	write_poly_seps = False

	for poly in poly_list:
		if write_poly_seps:
			out_file.write('%s%s],\n'%(base_indent, indentation))
			out_file.write('%s%s[\n'%(base_indent, indentation))
		else:
			write_poly_seps = True

		write_comma = False
		for coord in poly:
			if write_comma:
				out_file.write(',\n')
			else:
#				out_file.write('\n')
				write_comma = True

			out_file.write('%s%s[ %f, %f]'%(base_indent, indentation, coord[0], coord[1]))

		out_file.write('\n')


	if feature_type == "MultiPolygon" or feature_type == "MultiLineString":
		out_file.write('%s\t\t\t]\n'%(base_indent))

	if not feature_type == "Point":
		out_file.write('%s\t\t]\n'%(base_indent))
	out_file.write('%s\t}\n'%(base_indent))
	out_file.write('%s}'%(base_indent))

#}}}
