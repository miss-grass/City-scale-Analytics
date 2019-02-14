import sqlite3
import entwiner as ent

# conn = sqlite3.connect("test.db")
# conn.enable_load_extension(True)
# result = conn.execute("SELECT load_extension('mod_spatialite.so')")
# print(list(result))
conn = sqlite3.connect("18 AU/data_db/sidewalks.db")
conn.enable_load_extension(True)
result = conn.execute("SELECT load_extension('mod_spatialite.so')")
G = ent.graphs.digraphdb.DiGraphDB('18 AU/data_db/sidewalks.db')