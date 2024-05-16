import pandas as pd

data1_1_name = "discrease_wild_salmon_1.1"
data1_1_file = "data/" + data1_1_name + ".csv"
df_data1_1 = pd.read_csv(data1_1_file)

df_data1_1_fr = df_data1_1.rename(columns = {'Year':"Année",
                             'Tons of wild salmon catch in Atlantic waters':
                             "Saumon pêché dans l'Atlantique en tonnes"})

data1_1_file_out = "data/" + data1_1_name + "_fr.csv"
df_data1_1_fr.to_csv(data1_1_file_out)