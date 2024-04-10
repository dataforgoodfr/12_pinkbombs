import pinkbombs as pb
import pandas as pd

MAPPING = {
    "salmon-collapse": {
        "filename": "discrease_wild_salmon_1.1.csv",
        "function": pb.make_area_single_chart,
        "parser": pd.read_csv,
        "arguments": ['Year', 'Tons of wild salmon catch in Atlantic waters', 'Wild Altantic salmon collapse']
    },
    "hyper-growth": {
        "filename": "hyper_growth_salmon_farming_1.2.csv",
        "function": pb.make_area_order_chart,
        "parser": pd.read_csv,
        "arguments": ['Year', 'Tonnes - live weight', 'Country', 'Hyper-growth in salmon farming', True]
    },
    "top-10": {
        "filename": "top_10_countries_producing_1.3.csv",
        "function": pb.make_bar_chart,
        "parser": pd.read_csv,
        "arguments": ['Tons', 'Country', '\% of total', 'Top 10 countries producing salmon (2021)', 'Tonnes of farmed salmon produced',]
    }
}