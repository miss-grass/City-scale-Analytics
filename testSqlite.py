import sqlite3

conn = sqlite3.connect("sidewalks.db")
conn.enable_load_extension(True)
result = conn.execute("SELECT load_extension('mod_spatialite.so')")
print(list(result))
