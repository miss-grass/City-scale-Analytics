import pandas as pd
import csv
import numpy as np

file1 = './output/new_sw_wth_fountain_restroom.csv'
file2 = './output/new_sw_collection.csv'

def join_dataframe(file1, file2):
    df1 = pd.read_csv(file1, index_col='Unnamed: 0')
    df1 = df1.iloc[:, [-2, -1]]

    df2 = pd.read_csv(file2, index_col='Unnamed: 0')
    df2.drinking_fountain = df1.drinking_fountain
    df2.public_restroom = df1.public_restroom

    df2.to_csv('./output/renewed_sw_collection.csv')



join_dataframe(file1, file2)

