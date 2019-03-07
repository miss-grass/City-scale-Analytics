import csv
import json
from geojson import Feature, FeatureCollection, Point
from collections import OrderedDict


features = []
csv_file = open('./external_data/Public_Art_Data.csv')
for row in csv.DictReader(csv_file):
    latitude = row['latitude']
    longitude = row['longitude']
    title = row['title']
    address = row['address']
    d = OrderedDict()
    d['type'] = 'Feature'

    d['properties'] = {
        'title': title,
        'address': address
    }

    d['geometry'] = {
        'type': 'Point',
        'coordinates': [longitude, latitude]
    }

    features.append(d)

d = OrderedDict()
d['type'] = 'FeatureCollection'
d['features'] = features
with open("./external_data/public_arts.geojson", 'w') as f:
    f.write(json.dumps(d, sort_keys=False, indent=4))

f.close()
print('finished')