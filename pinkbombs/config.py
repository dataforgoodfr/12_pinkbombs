import pinkbombs as pb
import pandas as pd

MAPPING = {
    "salmon-collapse": {
        "filename": "discrease_wild_salmon_1.1.csv",
        "function": pb.make_area_single_chart,
        "parser": pd.read_csv,
        "arguments": ['Year', 'Tons of wild salmon catch in Atlantic waters', 'Wild Altantic salmon collapse']
    }
}