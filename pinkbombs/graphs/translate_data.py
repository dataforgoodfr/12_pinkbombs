import pandas as pd

# Load dataset translating countries into french
data_pays_file = 'data/country_pays.csv'
df_pays = pd.read_csv(data_pays_file)

# Data for Graph 1.1
data1_1_name = "discrease_wild_salmon_1.1"
data1_1_file = "data/" + data1_1_name + ".csv"
df_data1_1 = pd.read_csv(data1_1_file)

df_data1_1_fr = df_data1_1.rename(columns = {
    'Year':"Année",
    'Tons of wild salmon catch in Atlantic waters': "Saumon pêché dans l'Atlantique en tonnes"})

data1_1_file_out = "data/" + data1_1_name + "_fr.csv"
df_data1_1_fr.to_csv(data1_1_file_out)

# Data for Graph 1.2
data1_2_name = "hyper_growth_salmon_farming_1.2"
data1_2_file = "data/" + data1_2_name + ".csv"
df_data1_2 = pd.read_csv(data1_2_file)

df_data1_2.loc[df_data1_2.Country == "Korea, Dem. People's Rep", 
               "Country"]	= "Democratic People's Republic of Korea"
df_data1_2.loc[df_data1_2.Country == "Türkiye", "Country"]	= "Turkey"
df_data1_2 = df_data1_2.merge(df_pays, left_on='Country', right_on='name_eng', how = 'left')

df_data1_2_fr = df_data1_2.rename(columns = {
    'Year':"Année",
    'Tonnes - live weight': "Tonnes de saumon produit en élevage",
    'name_fr': "Pays"})

data1_2_file_out = "data/" + data1_2_name + "_fr.csv"
col_1_2_fr = ["Année", "Tonnes de saumon produit en élevage", "Pays"]
df_data1_2_fr[col_1_2_fr].to_csv(data1_2_file_out)

# Data for Graph 1.3
data1_3_name = "top_10_countries_producing_1.3"
data1_3_file = "data/" + data1_3_name + ".csv"
df_data1_3 = pd.read_csv(data1_3_file)

df_data1_3 = df_data1_3.merge(df_pays, left_on='Country', right_on='name_eng', how = 'left')

df_data1_3_fr = df_data1_3.rename(columns={
    "Flag": "Drapeau",
    "name_fr": "Pays",
    "Tons": "Tonnes de saumon",
    "% of total": "% du total"})

data1_3_file_out = "data/" + data1_3_name + "_fr.csv"
col_1_3_fr = ["Drapeau", "Pays",	"Tonnes de saumon", "% du total"]
df_data1_3_fr[col_1_3_fr].to_csv(data1_3_file_out)


# Data for Graph 1.4
data1_4_name = "evolution_salmon_farming_country_iso_1.4"
data1_4_file = "data/" + data1_4_name + ".csv"
df_data1_4 = pd.read_csv(data1_4_file)

df_data1_4.loc[df_data1_4.Country == "Korea, Dem. People's Rep", 
               "Country"]	= "Democratic People's Republic of Korea"
df_data1_4.loc[df_data1_4.Country == "Türkiye", "Country"]	= "Turkey"
df_data1_4 = df_data1_4.merge(df_pays, left_on='Country', right_on='name_eng', how = 'left')

df_data1_4_fr = df_data1_4.rename(columns={
    "Year": "Année",
    "name_fr": "Pays",
    "Tonnes - live weight": "Tonnes de saumon"})

data1_4_file_out = "data/" + data1_4_name + "_fr.csv"
col_1_4_fr = ["Année", "Pays", "Tonnes de saumon", "alpha-3"]
df_data1_4_fr[col_1_4_fr].to_csv(data1_4_file_out)


# Data for Graph 2.1 
data2_1_name = "top_10_companies_producing_2.1"
data2_1_file = "data/" + data2_1_name + ".csv"
df_data2_1 = pd.read_csv(data2_1_file)

df_data2_1_fr = df_data2_1.rename(columns={
    "Company": "Producteur",
    "Country": "Pays",
    "Flag": "Drapeau",
    "Volume, in tons, 2022": "Tonnes de saumon 2022",
    "Revenues 2022": "Revenus 2022",
    "Employees 2022": "Employés 2022",
    "Commercial name": "Nom commercial",
    "Website": "Site internet",
    "Creation date": "Date de création",
    "Headquarters": "Siège",
    })

data2_1_file_out = "data/" + data2_1_name + "_fr.csv"
df_data2_1_fr.to_csv(data2_1_file_out)


# Data for Graph 2.3 - translated in Google sheet