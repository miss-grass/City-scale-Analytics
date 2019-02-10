import csv
import networkx as nx
import matplotlib.pyplot as plt
import math
import sys
import json

G = nx.Graph()
offset = 200


def generate_graph(csv_file, type):
    file = open(csv_file)

    for row in csv.DictReader(file):
        v = row['v_coordinates'][1: -1].split(',')
        vx = float(v[0])
        vy = float(v[1])
        new_v = '(' + str(vx) + ',' + str(vy) + ')'

        u = row['u_coordinates'][1: -1].split(',')
        ux = float(u[0])
        uy = float(u[1])
        new_u = '(' + str(ux) + ',' + str(uy) + ')'

        if not G.has_node(new_v):
            G.add_node(new_v, pos_x=vx, pos_y=vy)

        if not G.has_node(new_u):
            G.add_node(new_u, pos_x=ux, pos_y=uy)

        G.add_edge(new_v, new_u)

        G.add_edge(new_u, new_v)

        if type == 'sidewalk':
            incline = float(row['incline'])
            G[new_v][new_u]['incline'] = incline + offset
            G[new_u][new_v]['incline'] = incline + offset

            surface = row['surface']
            G[new_v][new_u]['surface'] = surface
            G[new_u][new_v]['surface'] = surface
        elif type == 'crossing':
            cr = int(row['curbramps'])
            marked = int(row['marked'])
            G[new_v][new_u]['surface'] = None
            G[new_u][new_v]['surface'] = None
            G[new_u][new_v]['curbramp'] = cr
            G[new_v][new_u]['curbramp'] = cr
            G[new_u][new_v]['marked'] = marked
            G[new_u][new_v]['marked'] = marked

    file.close()


def add_external_data(csv_file, json_file1, json_file2):
    file = open(csv_file)
    for row in csv.DictReader(file):
        if len(row['drinking_fountain']) != 0:
            id_lst = row['drinking_fountain'][1:-1].strip(' ')
            print(type(id_lst))
    file.close()

def main():
    # generate_graph('./18 AU/data_table/new_sidewalks.csv', 'sidewalk')
    # generate_graph('./18 AU/data_table/new_crossings.csv', 'crossing')
    add_external_data('./output/new_sw_wth_fountain_restroom.csv', 'a', 'b')

if __name__ == '__main__':
    main()