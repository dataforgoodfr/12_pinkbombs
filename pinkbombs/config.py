import pinkbombs as pb
import pandas as pd

MAPPING = {
    "salmon-collapse": {
        "filename": "discrease_wild_salmon_1.1.csv",
        "function": pb.make_area_single_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Year",
            "Tons of wild salmon catch in Atlantic waters",
            "Wild Altantic salmon collapse",
        ],
    },
    "hyper-growth": {
        "filename": "hyper_growth_salmon_farming_1.2.csv",
        "function": pb.make_area_order_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Year",
            "Tonnes - live weight",
            "Country",
            "Hyper-growth in salmon farming",
            True,
        ],
    },
    "top-10": {
        "filename": "top_10_countries_producing_1.3.csv",
        "function": pb.make_color_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Tons",
            "Country",
            "Flag",
            "\% of total",
            "Top 10 countries producing salmon (2021)",
            "Tonnes of farmed salmon produced",
            "Country",
        ],
    },
    "evolution-map": {
        "filename": "evolution_salmon_farming_country_iso_1.4.csv",
        "function": pb.make_animated_bubble_map,
        "parser": pd.read_csv,
        "arguments": [
            "alpha-3",
            "Country",
            "Year",
            "Tonnes - live weight",
            "Evolution of salmon farming by country",
        ],
    },
    "top-comp": {
        "filename": "top_10_companies_producing_2.1.csv",
        "function": pb.make_simple_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Volume, in tons, 2022",
            "Company",
            "Flag",
            "Revenues 2022",
            "Employees 2022",
            [
                "Country",
                "Commercial name",
                "Creation date",
                "Headquarters",
                "Website",
                "Revenues 2022",
                "Employees 2022",
                "Note",
            ],
            "Top 10 companies producing salmon",
            "Volume of salmon produced in tonnes (2022)",
            "Company",
            "#151c97",
        ],
    },
    "top-land": {
        "filename": "top_10_land_based_companies_2.3.csv",
        "function": pb.make_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Production Capacity in tons",
            "Company",
            "Countries",
            "Top 10 companies producing salmon on land",
            "Planned production capacity per year in tonnes",
        ],
    },
}
