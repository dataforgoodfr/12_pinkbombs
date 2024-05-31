
import pandas as pd
import os

# Script to read the csv files and save them as zip for download from pinkbombs.org

path = "data/"
dir_list = os.listdir(path)

for el in dir_list:
    if el[-3:] == 'csv':
        df = pd.read_csv(path+el)
        df.to_csv("download/csv/"+el+".zip", compression='zip')
        print("Files converted: ", el)