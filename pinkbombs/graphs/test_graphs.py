# Temp file to generate the plotly charts into html
# for testing and iteration

import pinkbombs as pb
import pandas as pd
import plotly.express as px

# Graph 1.1 - Wild Altantic salmon collapse
data1_1_name = "discrease_wild_salmon_1.1"
data1_1_file = "data/" + data1_1_name + ".csv"
df_data1_1 = pd.read_csv(data1_1_file)
g1_1 = pb.make_area_single_chart(
    df_data1_1,
    "Year",
    "Tons of wild salmon catch in Atlantic waters",
    "Wild Altantic salmon collapse",
)

g1_1.write_html("pinkbombs/graphs/test_html/" + data1_1_name + ".html")

# Graph 1.2 - Wild Altantic salmon collapse
data1_2_name = "hyper_growth_salmon_farming_1.2"
data1_2_file = "data/" + data1_2_name + ".csv"
df_data1_2 = pd.read_csv(data1_2_file)

g1_2 = pb.make_area_order_chart(
    df_data1_2,
    "Year",
    "Tonnes - live weight",
    "Country",
    title="Hyper-growth in salmon farming",
    reorder=True,
)

g1_2.write_html("pinkbombs/graphs/test_html/" + data1_2_name + ".html")

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
    title="Top 10 countries producing salmon (2021)",
    xtitle="Tonnes of farmed salmon produced",
    ytitle="Country",
)

g1_3.write_html("pinkbombs/graphs/test_html/" + data1_3_name + ".html")

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
    title="Evolution of salmon farming by country",
)

g1_4.write_html("pinkbombs/graphs/test_html/" + data1_4_name + ".html")

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
        "Country",
        "Commercial name",
        "Creation date",
        "Headquarters",
        "Website",
        "Revenues 2022",
        "Employees 2022",
        "Note",
    ],
    title="Top 10 companies producing salmon",
    xtitle="Volume of salmon produced in tonnes (2022)",
    ytitle="Company",
    mycolor="#151c97",  # Seastemik dark blue
)

g2_1.write_html("pinkbombs/graphs/test_html/" + data2_1_name + ".html")

# Graph 2.3 -  Top 10 land-based companies producing salmon
data2_3_name = "top_10_land_based_companies_2.3"
data2_3_file = "data/" + data2_3_name + ".csv"
df_data2_3 = pd.read_csv(data2_3_file)

g2_3 = pb.make_bar_chart(
    df_data2_3,
    input_x="Production Capacity in tons",
    input_y="Company",
    input_other="Countries",
    title="Top 10 companies producing salmon on land",
    xtitle="Planned production capacity per year in tonnes",
    palette=px.colors.qualitative.Prism,
)

g2_3.write_html("pinkbombs/graphs/test_html/" + data2_3_name + ".html")

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
    ytitle='Antibiotics usage (tonnes)')

g4_2.write_html("pinkbombs/graphs/test_html/" + data4_2_name + ".html")

