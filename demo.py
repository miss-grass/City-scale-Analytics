import entwiner as ent

import networkx as nx

G = ent.graphs.digraphdb.DiGraphDB(path='test.db')
path = nx.algorithms.shortest_paths.dijkstra_path(G, '-122.5049849, 48.7798528', '-122.5074134, 48.7798173', 'length')
print(path)
