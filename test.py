import entwiner as ent
import networkx as nx
import sqlite3
G = ent.graphs.digraphdb.DiGraphDB(path='./18 AU/data_table/sidewalks.db')
path = nx.algorithms.shortest_paths.dijkstra_path(G, '-122.3317918, 47.61083', '-122.3324073, 47.6107093', 'length')
print(path)

# ent.build.create_graph('18 AU/data_table/sidewalks.geojson', '18 AU/data_table/sidewalks.db')
# conn = sqlite3.connect("./18 AU/data_table/sidewalks.db")
# conn.enable_load_extension(True)
# result = conn.execute("SELECT load_extension('mod_spatialite.so')")
# print(list(result))

