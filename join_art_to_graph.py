import csv
import networkx as nx
import matplotlib.pyplot as plt

import math
import sys
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString
from math import e
import numpy as np

def main():
    artfilename = "external data/Public_Art_Data.csv"
    art = pd.read_csv(artfilename)

    swfilename = "18 AU/data_table/new_sidewalks.csv"
    sw = pd.read_csv(swfilename)

    coords = []
    for idx, row in sw.iterrows():
        # start node
        coordinates = row["v_coordinates"][1: -1].split(',')
        xv = float(coordinates[0])
        yv = float(coordinates[1])
        p1 = Point(xv, yv)

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = float(coordinates[0])
        yu = float(coordinates[1])
        p2 = Point(xu, yu)

        line = LineString([p1, p2])
        coords.append(line)

    sw['geometry'] = coords
    art_array = np.empty((sw.shape[0],), object)


    # sw['Coordinates'] = list(zip(sw.v_coordinates, sw.u_coordinates))
    # sw['Coordinates'] = sw['Coordinates'].apply(LineString)
    gdf = gpd.GeoDataFrame(sw, geometry='geometry')

    id = []
    pt = []
    #Find closest sidewalk
    for idx, row in art.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        p = Point((lon, lat))

        r = 1e-3

        bbox = [p.x - r, p.y - r, p.x + r, p.y + r]
        query = gdf.sindex.intersection(bbox, objects=True)
        sw_bbox = gdf.loc[[q.object for q in query]].geometry
        while len(sw_bbox.distance(p).sort_values().index) == 0:
            r *= e
            bbox = [p.x - r, p.y - r, p.x + r, p.y + r]
            query = gdf.sindex.intersection(bbox, objects=True)
            sw_bbox = gdf.loc[[q.object for q in query]].geometry
        # print(str(idx) + ": " + str(sw_bbox))
        closest_dist = sw_bbox.distance(p).sort_values().index[0]
        closest = gdf.loc[closest_dist]
        print(str(idx) + " closest: " + str(closest_dist))
        new_point = closest.geometry.interpolate(closest.geometry.project(p))
        print(str(idx) + ": " + str(tuple(new_point.coords[0])))
        pt.append(new_point)
        id.append(closest_dist)

        if art_array[closest_dist] is None:
            art_array[closest_dist] = []
        art_array[closest_dist].append(idx)

    art['closest sidewalk id'] = id
    art['closest sidewalk point'] = pt
    art.to_csv("output/art_mapping_sw", encoding='utf-8')
    sw['art'] = art_array
    sw.to_csv("output/new_sw_wth_art", encoding='utf-8')



if __name__ == "__main__":
    main()