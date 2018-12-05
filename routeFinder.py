import csv
import networkx as nx
import matplotlib.pyplot as plt
import entwiner as ent
import math
import sys
from django.contrib.gis.geos import Polygon, Point, MultiPoint, GeometryCollection, LineString

# Upper left: 47.686957, -122.355331
#
# Upper right: 47.686790, -122.317615
#
# Lower right: 47.664945, -122.317377
#
# Lower left: 47.665010, -122.354551


G = nx.Graph()
offset = 200  # to deal with negative inclines
leftBoundary = -122.355331
rightBoundary = -122.317377
upperBoundary = 47.686790
lowerBoundary = 47.665010

def generate_sdwk_network(csv_file):
    '''
    Given sidewalk csv files, generates the network
    based on coordinates
    '''
    file = open(csv_file)
    #    G = nx.Graph()

    for row in csv.DictReader(file):
        # start node
        coordinates = row["v_coordinates"][1: -1].split(',')
        xv = "%.6f" % float(coordinates[0])
        yv = "%.6f" % float(coordinates[1])
        v = '(' + str(xv) + ',' + str(yv) + ')'

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.6f" % float(coordinates[0])
        yu = "%.6f" % float(coordinates[1])
        u = '(' + str(xu) + ',' + str(yu) + ')'

        # restrict to the Green Lake region
        if filter(float(xv), float(yv)) or filter(float(xu), float(yu)):
            if not G.has_node(v):
                G.add_node(v, pos_x=xv, pos_y=yv)

            if not G.has_node(u):
                G.add_node(u, pos_x=xu, pos_y=yu)

            # incline
            incline = float(row["incline"])
            # surface
            surface = str(row["surface"])
            # park
            park = str(row["adjacent_parks"]).strip("[]\'").split(",")
            # edge
            G.add_edge(v, u)
            G[v][u]['incline'] = incline + offset
            G[v][u]['surface'] = surface
            G[v][u]['park'] = len(park)
            G.add_edge(u, v)
            G[u][v]['incline'] = 0 - incline + offset
            G[u][v]['surface'] = surface
            G[u][v]['park'] = len(park)


    file.close()
    return G

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
        xv = "%.6f" % float(coordinates[0])
        yv = "%.6f" % float(coordinates[1])
        v = '(' + str(xv) + ',' + str(yv) + ')'

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.6f" % float(coordinates[0])
        yu = "%.6f" % float(coordinates[1])
        u = '(' + str(xu) + ',' + str(yu) + ')'

        # restrict to the Green Lake region
        if filter(float(xv), float(yv)) or filter(float(xu), float(yu)):
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
            G[v][u]['incline'] = incline + offset
            G[v][u]['surface'] = None
            G[v][u]['marked'] = marked
            G[v][u]['curbramps'] = curbramps
            G.add_edge(u, v)
            G[u][v]['incline'] = 0 - incline + offset
            G[u][v]['surface'] = None
            G[v][u]['marked'] = marked
            G[v][u]['curbramps'] = curbramps

    file.close()
    return G


def filter(x, y):
    return x >= leftBoundary and x <= rightBoundary and y >= lowerBoundary and y <= upperBoundary

def weight(u, v, d):
    #node_u_wt = G.nodes[u].get('node_weight', 1)
    #node_v_wt = G.nodes[v].get('node_weight', 1)
    park_list = d.get('park')
    edge_wt = len(park_list)
    return edge_wt

def use_ent():
    G_ent = ent.graphs.digraphdb.digraphdb('data_db/sidewalks.db')
    print(G_ent.nodes)
    # v = G_ent.node_by_id("1")
    # u = G_ent.node_by_id("10")
    # print(G_ent.edges_by_nodes("1", "2"))
    # path = dict(nx.all_pairs_dijkstra_path(G_ent, weight=weight))
    # for key in path.keys():
    #     print(str(key) + " --> " + str(path.get(key)))
    path = nx.algorithms.shortest_paths.dijkstra_path(G_ent, '-122.3129257, 47.5567878', '-122.3105936, 47.5567746', weight="park")
    print(path)

def find_closest_node(x, y):
    print("Finding closest node of location " + node_to_string(x, y))
    node_pos_x = nx.get_node_attributes(G, 'pos_x')
    node_pos_y = nx.get_node_attributes(G, 'pos_y')
    min_dist = sys.maxsize
    result = None
    for node in G.nodes:
        dist = calculate_distance(x, y, float(node_pos_x[node]), float(node_pos_y[node]))
        if dist < min_dist:
            min_dist = dist
            result = node
    print("Closest node: " + str(result))
    print("Min distance: " + str(min_dist))
    return result

def calculate_distance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

def find_shortest_path(src_x, src_y, dest_x, dest_y):
    node_src = find_closest_node(src_x, src_y)
    node_dest = find_closest_node(dest_x, dest_y)
    path = nx.dijkstra_path(G, node_src, node_dest, weight="park")
    return path

def node_to_string(x, y):
    return "(" + str(x) + "," + str(y) + ")"

def path_to_string(path):
    result = str(path[0]) + "\n"
    for i in range(1, len(path)):
        result = result + " --> " + str(path[i]) + "\n"
    return result

def path_to_geojson(path):
    line_lst = []
    for i in range(1, len(path)-1):
        coords1 = extract_node_from_string(str(path[i]))
        coords2 = extract_node_from_string(str(path[i+1]))
        line = LineString((float(coords1[0]), float(coords1[1])), (float(coords2[0]), float(coords2[1])))
        line_lst.append(line)
    gc = GeometryCollection(line_lst)
    return gc.geojson

def extract_node_from_string (node_str):
    coords = node_str.strip("()").split(",")
    print(coords)
    return coords



def main():
    G_sdw = generate_sdwk_network("data_table/new_small_sidewalks.csv")
    generate_crossing_network("data_table/crossings.csv")
    #print(G_sdw.nodes)
    src_x = -122.328380
    src_y = 47.665679
    dest_x = -122.328261
    dest_y = 47.674457
    path = find_shortest_path(src_x, src_y, dest_x, dest_y)
    # print("Path from " + node_to_string(src_x, src_y) + " to " + node_to_string(dest_x, dest_y) + " is: ")
    # print(path_to_string(path))
    print(path_to_geojson(path))

    # plt.figure()
    # nx.draw(G_sdw)
    # plt.show()
    # path = dict(nx.all_pairs_dijkstra_path(G_sdw, weight="incline"))
    # for key in path.keys():
    #     print(str(key) + " --> " + str(path.get(key)))

    # # plt.figure()
    # nx.draw_networkx(G_sdw, node_size=1)
    # plt.show()

    # A = to_agraph(G)
    # print(A)

    # use_ent()




if __name__ == "__main__":
    main()

