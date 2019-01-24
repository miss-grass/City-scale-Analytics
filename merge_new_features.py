"""
CSE495
Hongbin Qu
This program incorporate new dataset with the existing dataset
"""

import csv
import rtree
import numpy as np
import geopandas as gpd

from shapely.geometry import Point
from timeit import default_timer as timer


def add_feature(sw, df, feature_file, feature_name):
	## New features
	new_col = np.empty((sw.shape[0],), object)
	sw_id = []
	point = []

	## Find closest
	for idx, row in df.iterrows():
		coords = list(row.geometry.coords)
		p = Point(coords[0])
		print(idx)
		print(p)

		r = 1e-5

		bbox = [p.x - r, p.y - r, p.x + r, p.y + r]
		query = sw.sindex.intersection(bbox, objects=True)
		sw_bbox = sw.loc[[q.object for q in query]].geometry
		while len(sw_bbox.distance(p).sort_values().index) == 0:
			r *= 5
			bbox = [p.x - r, p.y - r, p.x + r, p.y + r]
			query = sw.sindex.intersection(bbox, objects=True)
			sw_bbox = sw.loc[[q.object for q in query]].geometry
		closest_dist = sw_bbox.distance(p).sort_values().index[0]
		print('closest distance:', closest_dist)
		closest = sw.loc[closest_dist]
		new_point = closest.geometry.interpolate(closest.geometry.project(p))
		print('closest sw:', new_point)
		
		sw_id.append(closest_dist)
		point.append(new_point)
		new_col[closest_dist] = p
		print()

	df['closest_sidewalk_id'] = sw_id
	df['closest_sidewalk'] = point
	df.to_csv(feature_file, encoding='utf-8')

	sw[feature_name] = new_col
	sw.to_csv('data_table/sidewalks_with_new_features.csv', encoding='utf-8')



def main():
	## Set starting timer
	start = timer()
	
	## Read dataset
	sw = gpd.read_file('data_table/sidewalks.geojson')
	print(sw.shape)
	hosp = gpd.read_file('data_table/Hospitals.geojson')
	dola = gpd.read_file('data_table/Seattle Parks and Recreation GIS Map Layer Shapefile - Dog Off Leash Areas.geojson')

	add_feature(sw, hosp, 'data_table/Hospitals_with_sidewalk.csv', 
				'hospital')
	add_feature(sw, dola, 'data_table/Dog_Off_Leash_Areas_with_sidewalk.csv', 
				'dog_off_leash_areas')

	## Set ending timer
	end = timer()
	print('time:', end - start)

if __name__ == '__main__':
	main()