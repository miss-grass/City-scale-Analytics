import geojson
import csv
import json
import pygeoj
import geopandas as gpd
import geojsonio

# testfile = pygeoj.load('./data/sidewalks.geojson')
#
# print('total num of data:', len(testfile))
# print('all attributes:', testfile.all_attributes)
# print('bounding region', testfile.bbox)
# print(testfile.common_attributes)

fileInput = './data/sidewalks.geojson'
fileOutput = './data/sidewalks.csv'

states = gpd.read_file(fileInput)
print(states.head())
geojsonio.display(states)