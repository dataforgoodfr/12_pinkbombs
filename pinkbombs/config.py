import pandas as pd
import graphs as pb


MAPPING = {
    "salmon-collapse": {
        "filename": "discrease_wild_salmon_1.1.csv",
        "function": pb.make_area_single_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Year",
            "Tons of wild salmon catch in Atlantic waters",
            "Tonnes of wild salmon catch in Atlantic waters",
            [
                '#151c97'
            ],
            "simple_white",
            "",
            True,
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
            "Farmed salmon production by country",
            "Tonnes of farmed salmon produced",
            1975,
            True,
            True,
        ],
    },
    "hyper-growth-grouped": {
        "filename": "numbers_salmons_farmed_1.0.csv",
        "function": pb.make_area_chart_options,
        "parser": pd.read_csv,
        "arguments": [
            "Year",
            "Number of salmons (5kg each)",
            "Production of farmed salmons",
            "Number of salmons produced every year",
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
            "Top 10 countries producing salmon by tonnes (2021)",
            None,
            None,
            [
                '#151c97', 
                '#ff4530'
            ],
            True,
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
            1980,
            50,
            True,
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
                "Revenues",
                "Employees",
                "Note",
            ],
            "Top 10 companies producing salmon by tonnes (2022)",
            None,
            None,
            "#151c97",
            True,
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
            "Top 10 land-based salmon productors (ambitions)",
            "Company ambition for salmon production in tonnes",
            None,
            "#151c97",
            True,
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
            "Mortality rates of farmed salmons by company (2014-2022)",
            None,
            "Mortality Rate (%)",
            True,
        ],
    },
    "alternatives": {
        "filename": "alternatives_text_7.csv",
        "function": pb.make_matrix_alternatives,
        "parser": pd.read_csv,
        "arguments": [
            60,
            None,
            None,
            None,
            "Very limited impact",
            "Very high impact",
            False,
        ],
    },
}

MAPS = {
    "ras-map": {
        "filename": "ras_projects_for_map_2.4.csv",
        "function": pb.make_ras_bubble_map,
        "parser": pd.read_csv,
        "arguments": [
            "Electricity consumption",
            "Carbon footprint",
            "Farms represented by estimated:",
            None,
            True,
            False,
        ],
    },
}

MAPPINGFR = {
    "salmon-collapse": {
        "filename": "discrease_wild_salmon_1.1_fr.csv",
        "function": pb.make_area_single_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Année",
            "Saumon pêché dans l'Atlantique en tonnes",
            "Saumon pêché dans l'Atlantique en tonnes",
            [
                '#151c97'
            ],
            "simple_white",
            "",
            True,
        ],
    },
    "hyper-growth": {
        "filename": "hyper_growth_salmon_farming_1.2_fr.csv",
        "function": pb.make_area_order_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Année",
            "Tonnes de saumon produit en élevage",
            "Pays",
            "Production de saumons atlantique d'élevage par pays",
            "Tonnes de saumons atlantique",
            1975,
            True,
            True,
        ],
    },
    "hyper-growth-grouped": {
        "filename": "numbers_salmons_farmed_1.0_fr.csv",
        "function": pb.make_area_chart_options,
        "parser": pd.read_csv,
        "arguments": [
            "Année",
            "Nombre de saumons (5kg chacun)",
            "Production de saumons d'élevage",
            "Nombre de saumons produits chaque année",
        ],
    },   
    "top-10": {
        "filename": "top_10_countries_producing_1.3_fr.csv",
        "function": pb.make_color_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Tonnes de saumon",
            "Pays",
            "Drapeau",
            "% du total",
            "Top 10 pays producteurs de saumon par tonnes (2021)",
            None,
            None,
            [
                '#151c97', 
                '#ff4530'
            ],
            True,
        ],
    },
    "evolution-map": {
        "filename": "evolution_salmon_farming_country_iso_1.4_fr.csv",
        "function": pb.make_animated_bubble_map,
        "parser": pd.read_csv,
        "arguments": [
            "alpha-3",
            "Pays",
            "Année",
            "Tonnes de saumon",
            "Evolution de l'élevage de saumons par pays",
            1980,
            50,
            True,
            [
                '#151c97',
            ],
        ],
    },
    "top-comp": {
        "filename": "top_10_companies_producing_2.1_fr.csv",
        "function": pb.make_simple_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Tonnes de saumon 2022",
            "Producteur",
            "Drapeau",
            "Revenus 2022",
            "Employés 2022",
            [
                "Nom commercial",
                "Date de création",
                "Siège",
                "Site internet",
                "Revenus",
                "Employés",
                "Note",
            ],
            "Top 10 des producteurs de saumons par tonnes (2022)",
            None,
            None,
            "#151c97",
            True,
        ],
    },
    "top-land": {
        "filename": "top_10_ras_companies_2.3_fr.csv",
        "function": pb.make_simple_bar_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Production en tonnes",
            "Producteur",
            "Drapeau",
            "Revenus 2022 dollars",
            "Employés 2022",
            [
                "Nombre de projets",
                "Pays des projets",
                "Note",
            ],
            "Top 10 producteurs de saumon d'élevage terrestre (ambitions)",
            "Ambitions des producteurs pour la production de saumon en tonnes",
            None,
            "#151c97",
            True,
            False,
        ],
    },
    "mortality-rates": {
        "filename": "mortality_rates_4.4_fr.csv",
        "function": pb.make_simple_box_chart,
        "parser": pd.read_csv,
        "arguments": [
            "Producteur",
            "Taux de mortalité",
            "Taux de mortalité des saumons d'élevage par producteur (2014-2022)",
            None,
            "Taux de mortalité (%)",
            True,
        ],
    },
    "alternatives": {
        "filename": "alternatives_text_7_fr.csv",
        "function": pb.make_matrix_alternatives,
        "parser": pd.read_csv,
        "arguments": [
            60,
            None,
            None,
            None,
            "Impact très réduit",
            "IImpact très fort",
            False,
        ],
    },
}

MAPSFR = {
    "ras-map": {
        "filename": "ras_projects_for_map_2.4_fr.csv",
        "function": pb.make_ras_bubble_map,
        "parser": pd.read_csv,
        "arguments": [
            "Consommation d'électricité",
            "Empreinte carbone",
            "Fermes-usines représentées par:",
            None,
            True,
            True
        ],
    },
}