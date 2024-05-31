
import pandas as pd

data1_0_name = 'numbers_salmons_farmed_1.0'
data1_0_file = "data/"+data1_0_name+".csv"
df_data1_0 = pd.read_csv(data1_0_file)

df_data1_0.to_csv("download/csv/"+data1_0_name+".csv.zip", 
                  compression='zip')