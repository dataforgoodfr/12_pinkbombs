import pandas as pd

# Data for Graph 1.1
data1_1_name = "discrease_wild_salmon_1.1"
data1_1_file = "data/" + data1_1_name + ".csv"
df_data1_1 = pd.read_csv(data1_1_file)

df_data1_1_fr = df_data1_1.rename(columns = {'Year':"Année",
                             'Tons of wild salmon catch in Atlantic waters':
                             "Saumon pêché dans l'Atlantique en tonnes"})

data1_1_file_out = "data/" + data1_1_name + "_fr.csv"
df_data1_1_fr.to_csv(data1_1_file_out)

# Data for Graph 1.2
data1_2_name = "hyper_growth_salmon_farming_1.2"
data1_2_file = "data/" + data1_2_name + ".csv"
df_data1_2 = pd.read_csv(data1_2_file)

# Read country in french and correct some countries
data_pays_file = 'data/country_pays.csv'
df_pays = pd.read_csv(data_pays_file)

df_data1_2.loc[df_data1_2.Country == "Korea, Dem. People's Rep", 
               "Country"]	= "Democratic People's Republic of Korea"
df_data1_2.loc[df_data1_2.Country == "Türkiye", 
               "Country"]	= "Turkey"
df_data1_2.loc[df_data1_2.Country == "United States of America", 
               "Country"]	= "United States"
df_data1_2 = df_data1_2.merge(df_pays, left_on='Country', right_on='name_eng', how = 'left')

df_data1_2_fr = df_data1_2.rename(columns = {
    'Year':"Année",
    'Tonnes - live weight': "Tonnes de saumon produit en élevage",
    'name_fr': "Pays"})

data1_2_file_out = "data/" + data1_2_name + "_fr.csv"
col_1_2_fr = ["Année", "Tonnes de saumon produit en élevage", "Pays"]
df_data1_2_fr[col_1_2_fr].to_csv(data1_2_file_out)