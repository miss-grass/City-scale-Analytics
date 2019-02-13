import networkx as nx
import entwiner as ent
import math
import pandas as pd
import csv
import json


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
    #    G = nx.Graph()

    for row in csv.DictReader(file):
        # start node
        coordinates = row["v_coordinates"][1: -1].split(',')
        xv = "%.7f" % float(coordinates[0])
        yv = "%.7f" % float(coordinates[1])
        v = '(' + str(xv) + ', ' + str(yv) + ')'

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.7f" % float(coordinates[0])
        yu = "%.7f" % float(coordinates[1])
        u = '(' + str(xu) + ', ' + str(yu) + ')'

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
        xv = "%.7f" % float(coordinates[0])
        yv = "%.7f" % float(coordinates[1])
        v = '(' + str(xv) + ', ' + str(yv) + ')'

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.7f" % float(coordinates[0])
        yu = "%.7f" % float(coordinates[1])
        u = '(' + str(xu) + ', ' + str(yu) + ')'

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
    return G


# An edge generator - takes input edges and creates transformed (and lower-memory) ones
def edge_gen(G):
    for u, v, d in G.edges_iter():
        yield u, v, cost_fun(d)


BASE_SPEED = 0.6
IDEAL_INCLINE = -0.0087
DIVISOR = 5


def find_k(g, m, n):
    return math.log(n) / abs(g - m)


k_up = find_k(0.08, IDEAL_INCLINE, DIVISOR)
k_down = find_k(0.1, IDEAL_INCLINE, DIVISOR)


def cost_fun(d, ideal_incline=IDEAL_INCLINE, base=BASE_SPEED):
    def tobler(grade, k=3.5, m=-0.0087, base=0.6):
        return base * math.exp(-k * abs(grade - m))

    if "curbramps" in d:
        if d["curbramps"] == 0:
            return None

    distance = d.get("length", 0)  # FIXME: no paths should have length zero

    if "incline" in d:
        incline = d["incline"] / 1000.
        if incline > ideal_incline:
            k = k_up
        else:
            k = k_down
        speed = tobler(incline, k=k, m=ideal_incline, base=base)
    else:
        speed = base

    time = distance / speed
    d["time"] = time

    return time


# Walksheds:
def walkshed(G, node, max_cost=600, sum_columns=["length", "art_num"]):
    # Use Dijkstra's method to get the below-400 walkshed paths
    distances, paths = nx.algorithms.shortest_paths.single_source_dijkstra(
        G,
        node,
        weight="time",
        cutoff=max_cost
    )
    for it in paths.items():
        print(it[1])

    # We need to do two things:
    # 1) Grab any additional reachable fringe edges. The user cannot traverse them in their
    #    entirety, but if they are traversible at all we still want to sum up their attributes
    #    in the walkshed. In particular, we're using "length" in this example. It is not obvious
    #    how we should assign "partial" data to these fringes, we will will just add the fraction
    #    to get to max_cost.
    #
    # 2) Sum up the attributes of the walkshed, assigning partial data on the fringes proportional
    #    to the fraction of marginal cost / edge cost.

    # Enumerate the fringes along with their fractional costs.
    # fringe_edges = {}
    # for n, distance in distances.items():
    #     for successor in G.successors(n):
    #         if successor not in distances:
    #             cost = G[n][successor]["time"]
    #             if cost is not None:
    #                 marginal_cost = max_cost - distance
    #                 fraction = marginal_cost / cost
    #                 fringe_edges[(n, successor)] = fraction

    # Create the sum total of every attribute in sum_columns
    edges = []
    for destination, path in paths.items():
        for node1, node2 in zip(path, path[1:]):
            edges.append((node1, node2))

    # All unique edges for which to sum attributes
    edges = set(edges)

    sums = {k: 0 for k in sum_columns}
    for n1, n2 in edges:
        d = G[n1][n2]
        for column in sum_columns:
            sums[column] += d.get(column, 0)

    # TODO: add in fringes!
    # for (n1, n2), fraction in fringe_edges.items():
    #     d = G[n1][n2]
    #     for column in sum_columns:
    #         sums[column] += d.get(column, 0) * fraction

    # return sums, list(zip(*paths))[1]
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

    # line_lst = []
    # for i in range(1, len(path)-1):
    #     coords1 = extract_node_from_string(str(path[i]))
    #     coords2 = extract_node_from_string(str(path[i+1]))
    #     line = LineString((float(coords1[0]), float(coords1[1])), (float(coords2[0]), float(coords2[1])))
    #     line_lst.append(line)
    # gc = GeometryCollection(line_lst)
    # return gc.geojson

    filename = 'test_walkshed.geojson'
    with open(filename, 'w') as outfile:
        json.dump(output, outfile)


def extract_node_from_string (node_str):
    coords = node_str.strip("()").split(",")
    print(coords)
    return coords


def join_art_to_graph(G):
    for idx, row in sw.iterrows():
        if row["art"] is not None:
            # start node
            coordinates = row["v_coordinates"][1: -1].split(',')
            xv = "%.7f" % float(coordinates[0])
            yv = "%.7f" % float(coordinates[1])
            v = '(' + str(xv) + ', ' + str(yv) + ')'

            # end node
            coordinates = row["u_coordinates"][1: -1].split(',')
            xu = "%.7f" % float(coordinates[0])
            yu = "%.7f" % float(coordinates[1])
            u = '(' + str(xu) + ', ' + str(yu) + ')'

            # art number
            art = str(row["art"]).strip("[]\'").split(",")
            art_num = len(art)

            G[v][u]['art_num'] = art_num
            G[u][v]['art_num'] = art_num


def main():
    print("preparing graph...")
    generate_sdwk_network(sidewalk_csv)
    generate_crossing_network(crossing_csv)
    #G = ent.graphs.digraphdb.DiGraphDB('18 AU/data_db/sidewalks.db')
    join_art_to_graph(G)
    # print(G.nodes)
    print("finished preparing graph!")
    print()

    # edge_gen(G)
    start_node = "(-122.3897940, 47.5191858)"
    print("computing walkshed starting from ", start_node)
    sums, paths = walkshed(G, start_node)

    print("Number of arts: ", sums["art_num"])
    print("Total length: ", sums["length"])

    print("output paths in walkshed...")
    paths_to_geojson(paths)

    vis_point_d = {}
    vis_point_d['type'] = "Feature"
    vis_point_d['geometry'] = {}
    vis_point_d['geometry']['type'] = 'Point'
    vis_point_d['geometry']['coordinates'] = [-122.3897940, 47.5191858]
    filename = 'start_node.geojson'
    with open(filename, 'w') as outfile:
        json.dump(vis_point_d, outfile)


if __name__ == "__main__":
    main()
