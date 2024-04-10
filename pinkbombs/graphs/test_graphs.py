# Temp file to generate the plotly charts into html 
# for testing and iteration

import pinkbombs as pb
import pandas as pd

# Graph 1.1 - Wild Altantic salmon collapse
data1_1_name = 'discrease_wild_salmon_1.1'
data1_1_file = "data/"+data1_1_name+".csv" 
df_data1_1 = pd.read_csv(data1_1_file)
g1_1 = pb.make_area_single_chart(
    df_data1_1, 'Year', 
    'Tons of wild salmon catch in Atlantic waters',
    'Wild Altantic salmon collapse'
    )  

g1_1.write_html("pinkbombs/graphs/test_html/"+data1_1_name+".html")

# Graph 1.2 - Wild Altantic salmon collapse
data1_2_name = 'hyper_growth_salmon_farming_1.2'
data1_2_file = "data/"+data1_2_name+".csv" 
df_data1_2 = pd.read_csv(data1_2_file)

g1_2 = pb.make_area_order_chart(
    df_data1_2, 'Year', 
    'Tonnes - live weight', 'Country', 
    title='Hyper-growth in salmon farming', 
    reorder=True
    )

g1_2.write_html("pinkbombs/graphs/test_html/"+data1_2_name+".html")

# Graph 1.3 - Main countries producing farmed salmon
data1_3_name = 'top_10_countries_producing_1.3'
data1_3_file = "data/"+data1_3_name+".csv" 
df_data1_3 = pd.read_csv(data1_3_file)

g1_3 = pb.make_bar_chart(
    df_data1_3, 
    input_x='Tons', input_y='Country', 
    input_col='% of total', 
    title='Top 10 countries producing salmon (2021)',
    xtitle='Tonnes of farmed salmon produced',
    )

g1_3.write_html("pinkbombs/graphs/test_html/"+data1_3_name+".html")
