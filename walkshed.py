import networkx as nx
# import entwiner as ent
import math
import pandas as pd
import csv
import json

# art, drinking_fountain, public_restroom, hospital, dog_off_leash_areas
# dataset
sidewalk_csv = "output/new_sw_collection.csv"
crossing_csv = "18 AU/data_table/new_crossings.csv"
sw = pd.read_csv(sidewalk_csv)
G = nx.Graph()


def generate_sdwk_network(csv_file):
    """
    Given sidewalk csv files, add them into networkx graph.
    based on coordinates.
    :param csv_file: a csv file which stores all the sidewalks
    in Seattle.
    :return: None
    """

    file = open(csv_file)

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
        G[v][u]['type'] = 'sidewalk'
        G[v][u]['incline'] = incline
        G[v][u]['surface'] = surface
        G[v][u]['length'] = length

        G.add_edge(u, v)
        G[u][v]['type'] = 'sidewalk'
        G[u][v]['incline'] = 0 - incline
        G[u][v]['surface'] = surface
        G[u][v]['length'] = length
    file.close()
    return G


def generate_crossing_network(csv_file):
    """
    Given crossing csv files, add them into networkx graph.
    based on coordinates
    :param csv_file: a csv file which stores all the crossings
    in Seattle
    :return: None
    """
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
        G[v][u]['type'] = 'crossing'
        G[v][u]['incline'] = incline

        # G[v][u]['surface'] = None


        G[v][u]['surface'] = 'Asphalt'
        G[v][u]['marked'] = marked
        G[v][u]['curbramps'] = curbramps


        G.add_edge(u, v)

        G[u][v]['type'] = 'crossing'
        G[u][v]['incline'] = 0 - incline
        # G[u][v]['surface'] = None

        G[u][v]['surface'] = 'Asphalt'
        G[u][v]['marked'] = marked
        G[u][v]['curbramps'] = curbramps

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

    distance = d.get("length", 0.1)  # FIXME: no paths should have length zero

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
def walkshed(G, node, max_cost=15):
    """
    Use single_source_dijkstra to calculate all the
    paths that a people can reach within max_cost time
    starting from a node.
    :param G: networkx graph
    :param node: starting point
    :param max_cost: time threshold (unit: minutes)
    :return: paths: all the edges that a people can reach within
    max_cost time.
    sums: sum of the attributes along the path.
    """
    sum_columns = ["length", "art_num", 'fountain_num', 'restroom_num', 'dog_num', 'hospital_num']
    # Use Dijkstra's method to get the below-400 walkshed paths
    distances, paths = nx.algorithms.shortest_paths.single_source_dijkstra(
        G,
        node,
        weight="time",
        cutoff=max_cost
    )
    # for it in paths.items():
    #     print(it[1])

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
            # print(d.get(column, 0))
            sums[column] += d.get(column, 0)

    # TODO: add in fringes!
    # for (n1, n2), fraction in fringe_edges.items():
    #     d = G[n1][n2]
    #     for column in sum_columns:
    #         sums[column] += d.get(column, 0) * fraction

    # return sums, list(zip(*paths))[1]
    return sums, paths


def extract_node_from_string(node_str):
    """
    Convert node from string type to a list.
    :param node_str: nodes in the path
    :return: a list which represents the
    coordinates of a node.
    """
    coords = node_str.strip("()").split(",")
    return coords


def join_attributes_to_node(G):
    """
    From the new_sw_collections.csv, extract the attribute of
    each sidewalk and add them onto the relative edges.
    :param G: networkx Graph
    :return: None
    """
    for idx, row in sw.iterrows():
        coordinates = row["v_coordinates"][1: -1].split(',')
        xv = "%.7f" % float(coordinates[0])
        yv = "%.7f" % float(coordinates[1])
        v = '(' + str(xv) + ', ' + str(yv) + ')'

        # end node
        coordinates = row["u_coordinates"][1: -1].split(',')
        xu = "%.7f" % float(coordinates[0])
        yu = "%.7f" % float(coordinates[1])
        u = '(' + str(xu) + ', ' + str(yu) + ')'

        # fountain number
        if pd.notna(row['drinking_fountain']):
            fountain = row['drinking_fountain'].strip('[]').split(',')
            fountain_num = len(fountain)
        else:
            fountain_num = 0

        # restroom number
        if pd.notna(row['public_restroom']):
            restroom = row['public_restroom'].strip('[]').split(',')
            restroom_num = len(restroom)
        else:
            restroom_num = 0

        # hospital number
        if pd.notna(row['hospital']):
            hospital = row['hospital'].strip('[]').split(',')
            hospital_num = len(hospital)
        else:
            hospital_num = 0

        # dog off leash area number
        if pd.notna(row['dog_off_leash_areas']):
            dog = row['dog_off_leash_areas'].strip('[]').split(',')
            dog_num = len(dog)
        else:
            dog_num = 0

        # art number
        if pd.notna(row['art']):
            art = row['art'].strip('[]').split(',')
            art_num = len(art)
        else:
            art_num = 0

        # add the attributes to each edge
        G[v][u]['art_num'] = art_num
        G[u][v]['art_num'] = art_num

        G[v][u]['fountain_num'] = fountain_num
        G[u][v]['fountain_num'] = fountain_num

        G[v][u]['restroom_num'] = restroom_num
        G[u][v]['restroom_num'] = restroom_num

        G[v][u]['hospital_num'] = hospital_num
        G[u][v]['hospital_num'] = hospital_num

        G[v][u]['dog_num'] = dog_num
        G[u][v]['dog_num'] = dog_num


def paths_to_geojson(paths, filename):
    """
    Store the path into a geojson file.
    :param paths: the path which calculate by
    single_source_dijkstra algorithm.
    :param filename: directory of the output file
    :return: None
    """
    output = dict()
    output["type"] = "FeatureCollection"
    output['features'] = []

    for it in paths.items():
        path = it[1]
        one_path = dict()
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

    with open(filename, 'w') as outfile:
        json.dump(output, outfile)
    outfile.close()


def start_pt_to_geojson(start_node, filename):
    """
    Store the start point to a geojson file.
    :param start_node: start point node (coordinate)
    :param filename: directory of the file
    :return: None
    """
    node = start_node.strip('()').split(', ')
    for i in range(len(node)):
        node[i] = float(node[i])
    vis_point_d = dict()
    vis_point_d['type'] = "FeatureCollection"
    vis_point_d['features'] = []
    geometry = dict()
    geometry['geometry'] = dict()
    geometry['geometry']['type'] = 'Point'
    geometry['geometry']['coordinates'] = node
    vis_point_d['features'].append(geometry)

    with open(filename, 'w') as outfile:
        json.dump(vis_point_d, outfile)
    outfile.close()


def main():
    print("preparing graph...")
    generate_sdwk_network(sidewalk_csv)
    
    generate_crossing_network(crossing_csv)
    #G = ent.graphs.digraphdb.DiGraphDB('18 AU/data_db/sidewalks.db')
    join_attributes_to_node(G)
    # nx.write_edgelist(G, 'edgelist.txt')

    print("finished preparing graph!")
    print()

    # edge_gen(G)
    start_node = "(-122.3323077, 47.6105820)"
    print("computing walkshed starting from ", start_node)
    sums, paths = walkshed(G, start_node)

    print("Number of arts: ", sums["art_num"])
    print('Number of public restrooms: ', sums['restroom_num'])
    print('Number of drinking fountains: ', sums['fountain_num'])
    print("Total length: ", sums["length"])

    print("output paths in walkshed...")

    path_filename = './walkshed test/test_walkshed.geojson'
    paths_to_geojson(paths, path_filename)
    start_pt_filename = './walkshed test/start_node.geojson'
    start_pt_to_geojson(start_node, start_pt_filename)

    print('Done!')


if __name__ == "__main__":
    main()
