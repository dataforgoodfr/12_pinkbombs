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
            [
                '#151c97'
            ],
        ],
    },
    "salmon-collapse-fr": {
        "filename": "discrease_wild_salmon_1.1_fr.csv",
        "function": pb.make_area_single_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Année",
            "Saumon pêché dans l'Atlantique en tonnes",
            "Effondrement des stocks de saumon sauvage",
            [
                '#151c97'
            ],
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
    "hyper-growth-grouped": {
        "filename": "hyper_growth_salmon_farming_1.2.csv",
        "function": pb.make_area_order_chart_grouped,
        "parser": pd.read_csv,
        "arguments": [
            "Year",
            "Tonnes - live weight",
            "Hyper-growth in salmon farming",
            "#fd442f",
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
            "% of total",
            "Top 10 countries producing salmon (2021)",
            "Tonnes of farmed salmon produced",
            "Country",
            [
                '#151c97', 
                '#ff4530'
            ]
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
            [
                '#151c97',
            ],
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
        "filename": "top_10_ras_companies_2.3.csv",
        "function": pb.make_simple_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Production in tonnes",
            "Parent company",
            "Flag",
            "Revenues 2022 dollars",
            "Employees 2022",
            [
                "Number of projects",
                "Countries of projects",
                "Note",
            ],
            "Top 10 RAS companies producing salmon",
            "Company ambition for salmon production in tonnes",
            "Company",
            "#151c97",
            False,
        ],
    },
    "mortality-rates": {
        "filename": "mortality_rates_4.4.csv",
        "function": pb.make_simple_box_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Company",
            "Mortality_rate",
            "Mortality rate by Companies",
            "Company",
        ],
    },
    "alternatives": {
        "filename": "carbon_bombs_pie_chart_5.1.csv",
        "function": pb.make_matrix_alternatives,
        "parser": pd.read_csv,
        "arguments": [
            900,
            500,
            True,
        ],
    },
}

MAPS = {
    "ras-map": {
        "filename": "ras_projects_for_map_2.4.csv",
        "function": pb.make_ras_bubble_map,
        "parser": pd.read_csv,
        "arguments": [],
    },
}
