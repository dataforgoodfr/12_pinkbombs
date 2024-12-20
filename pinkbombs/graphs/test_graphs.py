# Temp file to generate the plotly charts into html
# for testing and iteration

import pinkbombs as pb
import pandas as pd
import plotly.express as px

# Graph 1.0 - Page Story production of salmons
data1_0_name = 'numbers_salmons_farmed_1.0'
data1_0_file = "data/"+data1_0_name+".csv"
df_data1_0 = pd.read_csv(data1_0_file)

g1_0 = pb.make_area_chart_options(
    df_data1_0,
    input_x="Year",
    input_y="Number of salmons (5kg each)",
    title="Farmed salmon production",
    legend_title="Number of salmon produced every year",
)

g1_0.write_html("pinkbombs/graphs/test_html/" + data1_0_name + ".html")

# Graph 1.0 - Page Story production of salmons - FRENCH
data1_0_file = "data/"+data1_0_name+"_fr.csv"
df_data1_0 = pd.read_csv(data1_0_file)

g1_0 = pb.make_area_chart_options(
    df_data1_0,
    input_x="Année",
    input_y="Nombre de saumons (5kg chacun)",
    title="Production de saumons d'élevage",
    legend_title="Nombre de saumons produits chaque année",
)

g1_0.write_html("pinkbombs/graphs/test_html/" + data1_0_name + "_fr.html")


# Graph 1.1 - Wild Altantic salmon collapse
data1_1_name = "discrease_wild_salmon_1.1"
data1_1_file = "data/" + data1_1_name + ".csv"
df_data1_1 = pd.read_csv(data1_1_file)
g1_1 = pb.make_area_single_chart(
    df_data1_1,
    "Year",
    "Tons of wild salmon catch in Atlantic waters",
    "Tonnes of wild salmon catch in Atlantic waters",
    palette=['#151c97'],
    block_zoom=True,
)

g1_1.write_html("pinkbombs/graphs/test_html/" + data1_1_name + ".html")

# Graph 1.1 - Wild Altantic salmon collapse - FRENCH
data1_1_file = "data/" + data1_1_name + "_fr.csv"
df_data1_1 = pd.read_csv(data1_1_file)
g1_1 = pb.make_area_single_chart(
    df_data1_1,
    "Année",
    "Saumons pêchés dans l'Atlantique en tonnes",
    "Saumons pêchés dans l'Atlantique en tonnes",
    palette=['#151c97'],
    block_zoom=True,
)

g1_1.write_html("pinkbombs/graphs/test_html/" + data1_1_name + "_fr.html")


# Graph 1.2 - Hyper growth salmon farming
data1_2_name = "hyper_growth_salmon_farming_1.2"
data1_2_file = "data/" + data1_2_name + ".csv"
df_data1_2 = pd.read_csv(data1_2_file)

g1_2 = pb.make_area_order_chart(
    df_data1_2,
    "Year",
    "Tonnes - live weight",
    "Country",
    title="Farmed salmon production by country",
    y_title="Tonnes of farmed salmon produced", 
    min_date = 1975,
    reorder=True,
    hide_zoom=True,
)

g1_2.write_html("pinkbombs/graphs/test_html/" + data1_2_name + ".html")

# Graph 1.2 - Wild Altantic salmon collapse - FRENCH
data1_2_file = "data/" + data1_2_name + "_fr.csv"
df_data1_2 = pd.read_csv(data1_2_file)

g1_2 = pb.make_area_order_chart(
    df_data1_2,
    "Année", 
    "Tonnes de saumons produits en élevage", 
    "Pays",
    title="Production de saumons atlantiques d'élevage par pays",
    y_title="Tonnes de saumons atlantiques", 
    min_date = 1975,
    reorder=True,
    hide_zoom=True,
)

g1_2.write_html("pinkbombs/graphs/test_html/" + data1_2_name + "_fr.html")

# Graph 1.3 - Main countries producing farmed salmon
data1_3_name = "top_10_countries_producing_1.3"
data1_3_file = "data/" + data1_3_name + ".csv"
df_data1_3 = pd.read_csv(data1_3_file)

g1_3 = pb.make_color_bar_chart(
    df_data1_3,
    input_x="Tons",
    input_y1="Country",
    input_y2="Flag",
    input_col="% of total",
    title="Top 10 salmon producing countries by tonnes (2021)",
    xtitle=None,
    ytitle=None,
    palette=['#151c97', '#ff4530'],
    block_zoom=True,
)

g1_3.write_html("pinkbombs/graphs/test_html/" + data1_3_name + ".html")

# Graph 1.3 - Main countries producing farmed salmon - FRENCH
data1_3_file = "data/" + data1_3_name + "_fr.csv"
df_data1_3 = pd.read_csv(data1_3_file)

g1_3 = pb.make_color_bar_chart(
    df_data1_3,
    input_x="Tonnes de saumon", 
    input_y1='Pays', 
    input_y2='Drapeau',
    input_col="% du total",
    title='Top 10 pays producteurs de saumons par tonnes (2021)',
    xtitle=None,
    ytitle=None,
    palette = ['#151c97', '#ff4530'],
    block_zoom=True,
)

g1_3.write_html("pinkbombs/graphs/test_html/" + data1_3_name + "_fr.html")

# Graph 1.4 -  Evolution of salmon farming by country
data1_4_name = "evolution_salmon_farming_country_iso_1.4"
data1_4_file = "data/" + data1_4_name + ".csv"
df_data1_4 = pd.read_csv(data1_4_file)

g1_4 = pb.make_animated_bubble_map(
    df_data1_4,
    input_loc="alpha-3",
    input_hover="Country",
    input_time="Year",
    input_size="Tonnes - live weight",
    title=None,
    min_year=1980,
    palette=['#151c97'],
)

func1_4 = open("pinkbombs/graphs/test_html/" + data1_4_name + ".html","w") 
func1_4.write(g1_4) 
func1_4.close()

# Graph 1.4 -  Evolution of salmon farming by country - FRENCH
data1_4_file = "data/" + data1_4_name + "_fr.csv"
df_data1_4 = pd.read_csv(data1_4_file)

g1_4 = pb.make_animated_bubble_map(
    df_data1_4,
    input_loc="alpha-3",
    input_hover="Pays",
    input_time="Année",
    input_size="Tonnes de saumons",
    title=None,
    min_year=1980,
    palette=['#151c97'],
)

func1_4 = open("pinkbombs/graphs/test_html/" + data1_4_name + "_fr.html","w") 
func1_4.write(g1_4) 
func1_4.close()

# Graph 1.5 - Top 15 countries consuming salmon
data1_5_name = 'top_15_countries_consuming_1.5'
data1_5_file = "data/"+data1_5_name+".csv"
df_data1_5 = pd.read_csv(data1_5_file)

g1_5=pb.make_double_yaxis_bar_chart(
    df_data1_5,
    input_x1="Country",
    input_x2="Flag",
    input_y1="Apparent consumption",
    input_y2="Apparent consumption per capita",
    input_other=[
            "Production (Capture + Aquaculture)",
            "Export",
            "Import"],
    title="Top 15 countries consuming salmon",
    mycolor_bar='#151c97',
    bar_hover_legend="Consumption",
    mycolor_point="#FF4530",
    point_hover_legend="Consumption per capita",
    xtitle="Country",
    ytitle1="Apparent consumption in tonnes (2021)",
    ytitle2="Apparent consumption per capita in kilos (2021)",
    block_zoom=True
)

g1_5.write_html("pinkbombs/graphs/test_html/" + data1_5_name + ".html")

# Graph 1.5 - Top 15 countries consuming salmon - FRENCH
data1_5_name = 'top_15_countries_consuming_1.5'
data1_5_file = "data/"+data1_5_name+"_fr.csv"
df_data1_5 = pd.read_csv(data1_5_file)

g1_5=pb.make_double_yaxis_bar_chart(
    df_data1_5,
    input_x1="Pays",
    input_x2="Drapeau",
    input_y1="Consommation apparente",
    input_y2="Consommation apparente par habitant",
    input_other=[
            "Production (Capture + Aquaculture)",
            "Export",
            "Import"],
    title="Top 15 des pays consommateurs de saumons",
    mycolor_bar='#151c97',
    bar_hover_legend="Consommation",
    mycolor_point="#FF4530",
    point_hover_legend="Consommation par habitant",
    xtitle="Pays",
    ytitle1="Consommation apparente en tonnes (2021)",
    ytitle2="Consommation apparente par habitant en kilos (2021)",
    block_zoom=True
)

g1_5.write_html("pinkbombs/graphs/test_html/" + data1_5_name + "_fr.html")

# Graph 2.1 -  Top 10 companies producing salmon
data2_1_name = "top_10_companies_producing_2.1"
data2_1_file = "data/" + data2_1_name + ".csv"
df_data2_1 = pd.read_csv(data2_1_file)

g2_1 = pb.make_simple_bar_chart(
    df_data2_1,
    input_x="Volume, in tons, 2022",
    input_y1="Company",
    input_y2="Flag",
    input_n1="Revenues 2022",
    input_n2="Employees 2022",
    input_other=[
        "Commercial name",
        "Creation date",
        "Headquarters",
        "Website",
        "Revenues",
        "Employees",
        "Note",
    ],
    title="Top 10 companies producing salmon by tonnes (2022)",
    xtitle=None,
    ytitle=None,
    mycolor="#151c97",  # Seastemik dark blue
    block_zoom=True,
)

g2_1.write_html("pinkbombs/graphs/test_html/" + data2_1_name + ".html")

# Graph 2.1 -  Top 10 companies producing salmon - FRENCH
data2_1_file = "data/" + data2_1_name + "_fr.csv"
df_data2_1 = pd.read_csv(data2_1_file)

g2_1 = pb.make_simple_bar_chart(
    df_data2_1,
    input_x="Tonnes de saumon 2022",
    input_y1="Producteur",
    input_y2="Drapeau",
    input_n1="Revenus 2022",
    input_n2="Employés 2022",
    input_other=[
        "Nom commercial",
        "Date de création",
        "Siège",
        "Site internet",
        "Revenus",
        "Employés",
        "Note",
    ],
    title="Top 10 des producteurs de saumons par tonnes (2022)",
    xtitle=None,
    ytitle=None,
    mycolor="#151c97",  # Seastemik dark blue
    block_zoom=True,
)

g2_1.write_html("pinkbombs/graphs/test_html/" + data2_1_name + "_fr.html")

# Graph 2.3 -  Top 10 RAS companies producing salmon
data2_3_name = "top_10_ras_companies_2.3"
data2_3_file = "data/" + data2_3_name + ".csv"
df_data2_3 = pd.read_csv(data2_3_file)

g2_3 = pb.make_simple_bar_chart(
    df_data2_3,
    input_x='Production in tonnes',
    input_y1='Parent company',
    input_y2='Flag',
    input_n1='Revenues 2022 dollars',
    input_n2='Employees 2022',
    input_other=['Number of projects', 'Countries of projects', "Headquarters",
                 "Website",'Note'],
    title="Top 10 land-based salmon productors (ambitions)",
    xtitle='Company ambition for salmon production in tonnes',
    ytitle=None,
    mycolor='#151c97',
    block_zoom=True,
    fix_approx=False,
    )

g2_3.write_html("pinkbombs/graphs/test_html/" + data2_3_name + ".html")

# Graph 2.3 -  Top 10 RAS companies producing salmon - FRENCH
data2_3_file = "data/" + data2_3_name + "_fr.csv"
df_data2_3 = pd.read_csv(data2_3_file)

g2_3 = pb.make_simple_bar_chart(
    df_data2_3,
    input_x='Production en tonnes',
    input_y1='Producteur',
    input_y2='Drapeau',
    input_n1='Revenus 2022 dollars',
    input_n2='Employés 2022',
    input_other=['Nombre de projets', 'Pays des projets', "Siège",
                 "Site internet",'Note'],
    title="Top 10 producteurs de saumons d'élevage terrestre (ambitions)",
    xtitle='Ambitions des producteurs pour la production de saumons en tonnes',
    ytitle=None,
    mycolor='#151c97', 
    block_zoom=True,
    fix_approx=False
    )

g2_3.write_html("pinkbombs/graphs/test_html/" + data2_3_name + "_fr.html")

# Graph 2.4 - Map of RAS projects
data2_4_name = "ras_projects_for_map_2.4"
data2_4_file = "data/" + data2_4_name + ".csv"
df_data2_4 = pd.read_csv(data2_4_file)

g2_4 = pb.make_ras_bubble_map(
    df_data2_4, 
    title_layer1="Electricity consumption",
    title_layer2="Carbon footprint",
    legend_title="Farms represented by estimated:",
    title=None,
    add_title_legend=True,
    french=False,
    )

#g2_4.save("pinkbombs/graphs/test_html/" + data2_4_name + ".html")
func = open("pinkbombs/graphs/test_html/" + data2_4_name + ".html","w") 
func.write(g2_4) 
func.close()

# Graph 2.4 - Map of RAS projects - FRENCH
data2_4_file = "data/" + data2_4_name + "_fr.csv"
df_data2_4 = pd.read_csv(data2_4_file)

g2_4 = pb.make_ras_bubble_map(
    df_data2_4, 
    title_layer1="Consommation d'électricité",
    title_layer2="Empreinte carbone",
    legend_title="Fermes-usines représentées par:",
    title=None,
    add_title_legend=True,
    french=True,
    )

#g2_4.save("pinkbombs/graphs/test_html/" + data2_4_name + "_fr.html")
func = open("pinkbombs/graphs/test_html/" + data2_4_name + "_fr.html","w") 
func.write(g2_4) 
func.close()

# Graph 3.5 -  Escapes from marine cages
data3_5_name = "escapes_marine_cages_3.5"
data3_5_file = "data/" + data3_5_name + ".csv"
df_data3_5 = pd.read_csv(data3_5_file)

g3_5 = pb.make_treemap_chart(
    df_data3_5, 
    input_x1='n_escape', 
    input_x2='n_salmon_produced',
    input_x3='escape_rate', 
    input_y='production (t)',
    input_n='Company',
    title='More than 4 millions fish escaped since 2018'
    )

g3_5.write_html("pinkbombs/graphs/test_html/" + data3_5_name + ".html")

# Graph 4.2 - Antibiotics consumption
data4_2_name = "antibiotic_consumption_chile_4.2"
data4_2_file = "data/" + data4_2_name + ".csv"
df_data4_2 = pd.read_csv(data4_2_file)

g4_2 = pb.make_color_bar_chart2(
    df_data4_2,
    input_x='year',
    input_y='consom_atb_ton',
    input_col='biomass_harvested_ton', 
    col_rename={'consom_atb_ton': 'Antibiotics usage (tonnes)',
                'biomass_harvested_ton': 'Harvested biomass (tonnes)'},
    title="Antibiotic usage in Chile (2007-2021)",
    ytitle='Antibiotics usage (tonnes)'
    )

g4_2.write_html("pinkbombs/graphs/test_html/" + data4_2_name + ".html")

# Graph 4.4 - Escapes from marine cages
data4_4_name = "mortality_rates_4.4"
data4_4_file = "data/" + data4_4_name + ".csv"
df_data4_4 = pd.read_csv(data4_4_file)

g4_4 = pb.make_simple_box_chart(
    input_df=df_data4_4,
    input_x="Company",
    input_y="Mortality_rate",
    title="Mortality rates of farmed salmons by producers*",
    xtitle="*selected years between 2011-2022 where available",
    ytitle="Mortality Rate (%)",
    block_zoom=True,
)

g4_4.write_html("pinkbombs/graphs/test_html/" + data4_4_name + ".html")

# Graph 4.4 - Escapes from marine cages - FRENCH
data4_4_file = "data/" + data4_4_name + "_fr.csv"
df_data4_4 = pd.read_csv(data4_4_file)

g4_4 = pb.make_simple_box_chart(
    input_df=df_data4_4,
    input_x="Producteur",
    input_y="Taux de mortalité",
    title="Taux de mortalité des saumons d'élevage par producteurs*",
    xtitle="*années sélectionnées entre 2011-2022, lorsque disponibles",
    ytitle="Taux de mortalité (%)",
    block_zoom=True,
)

g4_4.write_html("pinkbombs/graphs/test_html/" + data4_4_name + "_fr.html")


# Graph 7 - Alternatives 
data7_name = "alternatives_text_7"
data7_file = "data/" + data7_name + ".csv"
df_data_7 = pd.read_csv(data7_file)

g7 = pb.make_matrix_alternatives(df_data_7, 
                                 max_len=60,
                                 max_len_col=11, #11
                                 width=None, 
                                 height=None,
                                 legend_green="Very limited impact",
                                 legend_red="Exces- sively high impact",
                                 hover_disable=False)

g7.write_html("pinkbombs/graphs/test_html/alternatives_7.html")

# Graph 7 - Alternatives - FRENCH
data7_file = "data/" + data7_name + "_fr.csv"
df_data_7 = pd.read_csv(data7_file)

g7 = pb.make_matrix_alternatives(df_data_7, 
                                 max_len=60,
                                 max_len_col=11, #11
                                 width=None, 
                                 height=None,
                                 legend_green="Impact très réduit",
                                 legend_red="Impact excessi- vement fort",
                                 hover_disable=False)

g7.write_html("pinkbombs/graphs/test_html/alternatives_7_fr.html")
