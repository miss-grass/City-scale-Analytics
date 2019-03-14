#!flask/bin/python

import sys

from flask import Flask, render_template, request, redirect, Response
import random, json
import networkx as nx
import entwiner as ent
import math
import pandas as pd
import csv
import json


app = Flask(__name__)

# dataset
sidewalk_csv = "output/new_sw_collection.csv"
crossing_csv = "18 AU/data_table/new_crossings.csv"
sw = pd.read_csv("output/new_sw_collection.csv", index_col=0)
G = nx.Graph()


def generate_sdwk_network(csv_file):
    '''
    Given sidewalk csv files, generates the network
    based on coordinates
    '''
    file = open(csv_file)

    for row in csv.DictReader(file):
        # start node
        coordinates = row["v_coordinates"][1: -1].split(',')
        xv = "%.7f" % float(coordinates[0])
        yv = "%.7f" % float(coordinates[1])
        v = str(xv) + ', ' + str(yv)

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.7f" % float(coordinates[0])
        yu = "%.7f" % float(coordinates[1])
        u = str(xu) + ', ' + str(yu)

        if not G.has_node(v):
            G.add_node(v, pos_x=xv, pos_y=yv)

        if not G.has_node(u):
            G.add_node(u, pos_x=xu, pos_y=yu)

        # incline
        incline = float(row["incline"])
        # surface
        surface = str(row["surface"])
        #length
        length = float(row["length"])

        # edge
        G.add_edge(v, u)
        G[v][u]['incline'] = incline
        G[v][u]['surface'] = surface
        G[v][u]['length'] = length
        G.add_edge(u, v)
        G[u][v]['incline'] = 0 - incline
        G[u][v]['surface'] = surface
        G[u][v]['length'] = length
    file.close()


def generate_crossing_network(csv_file):
    '''
    Given sidewalk csv files, generates the network
    based on coordinates
    '''
    file = open(csv_file)
    #    G = nx.Graph()

    for row in csv.DictReader(file):
        # start node
        coordinates = row["v_coordinates"][1: -1].split(',')
        xv = "%.7f" % float(coordinates[0])
        yv = "%.7f" % float(coordinates[1])
        v = str(xv) + ', ' + str(yv)

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.7f" % float(coordinates[0])
        yu = "%.7f" % float(coordinates[1])
        u = str(xu) + ', ' + str(yu)

        if not G.has_node(v):
            G.add_node(v, pos_x=xv, pos_y=yv)

        if not G.has_node(u):
            G.add_node(u, pos_x=xu, pos_y=yu)

        # incline
        incline = 0
        # marked
        marked = int(row["marked"])
        # curbramps
        curbramps = int(row["curbramps"])

        # edge
        G.add_edge(v, u)
        G[v][u]['incline'] = incline
        G[v][u]['surface'] = None
        G[v][u]['marked'] = marked
        G[v][u]['curbramps'] = curbramps
        G.add_edge(u, v)
        G[u][v]['incline'] = 0 - incline
        G[u][v]['surface'] = None
        G[v][u]['marked'] = marked
        G[v][u]['curbramps'] = curbramps

    file.close()


def walkshed(G, node, max_cost=5, sum_columns=["length", "drinking_fountain_num"]):
    # Use Dijkstra's method to get the below-400 walkshed paths
    distances, paths = nx.algorithms.shortest_paths.single_source_dijkstra(
        G=G,
        source=node,
        weight="time",
        cutoff=max_cost
    )

    # Create the sum total of every attribute in sum_columns
    edges = []
    for destination, path in paths.items():
        for node1, node2 in zip(path, path[1:]):
            edges.append((node1, node2))

    # All unique edges for which to sum attributes
    edges = set(edges)
    print("unique edges: ")
    print(edges)
    print(len(edges))

    sums = {k: 0 for k in sum_columns}
    for n1, n2 in edges:
        d = G[n1][n2]
        for column in sum_columns:
            sums[column] += d.get(column, 0)
    return sums, paths


def paths_to_geojson(paths):
    output = {}
    output["type"] = "FeatureCollection"
    output['features'] = []


    for it in paths.items():
        path = it[1]
        one_path = {}
        one_path['type'] = 'Feature'
        one_path['geometry'] = {}
        one_path['geometry']['type'] = 'LineString'
        line_lst = []
        for i in range(0, len(path)):
            coords = extract_node_from_string(str(path[i]))
            line = [float(coords[0]), float(coords[1])]
            line_lst.append(line)

        one_path['geometry']['coordinates'] = line_lst

        output['features'].append(one_path)

    return json.dumps(output)


def extract_node_from_string (node_str):
    coords = node_str.strip("()").split(",")
    return coords


def compute_distance(x_lon, x_lat, y_lon, y_lat):
    return math.pow(x_lon - y_lon, 2) + math.pow(x_lat - y_lat, 2)


@app.route("/")
def output():
    return render_template('index.html', name='Joe')


@app.route('/receiver', methods=['GET', 'POST'])
def worker():
    # read json + reply
    data = request.get_json()
    print(data)
    max_time = data['max_time']
    feature = data['feature']

    start_lat = round(float(data['start_lat']), 7)
    lon = float(data['start_lon'])
    start_lon = round(lon - (360 if lon > 0 else 0), 7)
    start_node = str(start_lon) + ", " + str(start_lat)

    # find closest node in G for start node
    if start_node not in G.nodes:
        min_dist = math.inf
        for node in G.nodes:
            coords = node.split(', ')
            dist = compute_distance(start_lon, start_lat, float(coords[0]), float(coords[1]))
            if dist < min_dist:
                min_dist = dist
                start_node = node

    if feature == "Drinking Fountains":
        col = "drinking_fountain_num"
    elif feature == "Public Restrooms":
        col = "public_restroom_num"
    elif feature == "Hospitals":
        col = "hospital_num"
    elif feature == "Dog Off Leash Areas":
        col = "dola_num"
    else:
        raise ValueError("Invalid feature requested!")


    sums, paths = walkshed(G, start_node, max_cost=int(max_time), sum_columns=["length", col])
    print("sum of utilities: ", sums[col])
    result = paths_to_geojson(paths)
    return result


# generic method for joining feature
def join_feature_to_graph(feature_name, attr_name):
    for idx, row in sw.iterrows():
        if pd.notna(row[feature_name]):
            # print(row["art"])
            # start node
            coordinates = row["v_coordinates"][1: -1].split(',')
            xv = "%.7f" % float(coordinates[0])
            yv = "%.7f" % float(coordinates[1])
            v = str(xv) + ', ' + str(yv)

            # end node
            coordinates = row["u_coordinates"][1: -1].split(',')
            xu = "%.7f" % float(coordinates[0])
            yu = "%.7f" % float(coordinates[1])
            u = str(xu) + ', ' + str(yu)

            # art number
            art = str(row[feature_name]).strip("[]\'").split(",")
            # print(art)
            art_num = len(art)

            G[v][u][attr_name] = art_num
            G[u][v][attr_name] = art_num


def main():
    #preprocess
    print("loading data...")
    generate_sdwk_network(sidewalk_csv)
    generate_crossing_network(crossing_csv)

    # join features to network
    #join_feature_to_graph("art", "art_num")
    join_feature_to_graph("drinking_fountain", "drinking_fountain_num")
    join_feature_to_graph("public_restroom", "public_restroom_num")
    join_feature_to_graph("hospital", "hospital_num")
    join_feature_to_graph("dog_off_leash_areas", "dola_num")



if __name__ == '__main__':
    main()
    # run!
    app.run(host='localhost', port=5001)
