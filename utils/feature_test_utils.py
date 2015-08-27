#!/use/bin/env python
import json

def match_tag_list(feature, master_tags):#{{{
	try:
		feature_tags = feature['properties']['tags']
	except:
		return True
	
	feature_tag_list = feature_tags.split(';')

	test = True
	for tag in master_tags:
		if tag in feature_tag_list:
			test = test and True
		else:
			test = test and False

	return test
#}}}

def feature_already_exists(existing_features, adding_feature):#{{{
	try:
		feature_name = adding_feature['properties']['name']
	except:
		print "Current feature doesn't have a name property. Exiting..."
		quit(1)

	for feature in existing_features['features']:
		try:
			test_name = feature['properties']['name']
		except:
			print "A feature in the existing features file does not have a name property. Exiting..."
			quit(1)

		if test_name == feature_name:
			print " A feature already exists with the name '%s', either use that one, or change the name before adding it."%(feature_name)
			return True

	return False
#}}}
