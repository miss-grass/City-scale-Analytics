import csv
import networkx as nx
import matplotlib.pyplot as plt
import entwiner as ent
import pylab as plt
from networkx.drawing.nx_agraph import graphviz_layout, to_agraph


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
                G.add_node(v, pos=(xv, yv))

            if not G.has_node(u):
                G.add_node(u, pos=(xu, yu))

            # incline
            incline = float(row["incline"])
            # surface
            surface = str(row["surface"])
            # edge
            G.add_edge(v, u)
            G[v][u]['incline'] = incline + offset
            G[v][u]['surface'] = surface
            G.add_edge(u, v)
            G[u][v]['incline'] = 0 - incline + offset
            G[u][v]['surface'] = surface

    file.close()
    return G

def filter(x, y):
    return x >= leftBoundary and x <= rightBoundary and y >= lowerBoundary and y <= upperBoundary

# def weight(u, v, d):
#     #node_u_wt = G.nodes[u].get('node_weight', 1)
#     #node_v_wt = G.nodes[v].get('node_weight', 1)
#     edge_wt = d.get('incline', 1)
#     return edge_wt

def use_ent():
    G_ent = ent.database.DiGraphDB('data_db/sidewalks.db')
    v = G_ent.node_by_id("1")
    u = G_ent.node_by_id("10")
    print(G_ent.edges_by_nodes("1", "2"))
    path = nx.algorithms.shortest_paths.dijkstra_path(G_ent, v, u, weight="inline")

def main():
    G_sdw = generate_sdwk_network("data_table/sidewalks.csv")
    # path = nx.dijkstra_path(G_sdw, "(-122.310990,47.554803)", "(122.310992,47.554803)", weight="incline")
    # print(path)
    # plt.figure()
    # nx.draw(G_sdw)
    # plt.show()
    path = dict(nx.all_pairs_dijkstra_path(G_sdw, weight="incline"))
    for key in path.keys():
        print(str(key) + " --> " + str(path.get(key)))

    # plt.figure()
    # nx.draw_networkx(G_sdw, node_size=1)
    # plt.show()

    # A = to_agraph(G)
    # print(A)

    #use_ent()




if __name__ == "__main__":
    main()

