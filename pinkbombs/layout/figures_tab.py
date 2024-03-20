import dash_bootstrap_components as dbc
import pandas as pd
from dash import html
from loguru import logger


# def generate_figures_layout(df: pd.DataFrame) -> dbc.Container:
def generate_figures_layout() -> dbc.Container:

    """Generate Figures tab with graphs and figures

    Returns:
        dbc.Container: Contents of the Figures tab
    """

    figures_tab = dbc.Container(
        children=[
            dbc.Row(
                dbc.Col(
                    children=[
                        dbc.Card(
                            children=[
                                html.H4("En un coup d'oeil", className="m-2"),
                                dbc.Row(
                                    children=[
                                        dbc.Col(
                                            dbc.CardBody(
                                                children=[
                                                    html.P("1500", className="fs-3"),
                                                    html.P(
                                                        "Saumons consommés depuis"
                                                        " que vous êtes sur le site internet"
                                                    ),
                                                ]
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.CardBody(
                                                children=[
                                                    html.P(
                                                        "13 000 000", className="fs-3"
                                                    ),
                                                    html.P(
                                                        "Saumons consommés en France"
                                                        " cette année"
                                                    ),
                                                ]
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.CardBody(
                                                children=[
                                                    html.P("11.1%", className="fs-3"),
                                                    html.P(
                                                        "Croissance de la consommation en France"
                                                        " depuis 10 ans"
                                                    ),
                                                ]
                                            )
                                        ),
                                        dbc.Col(
                                            dbc.CardBody(
                                                children=[
                                                    html.P(
                                                        "120 Gt eCO2", className="fs-3"
                                                    ),
                                                    html.P(
                                                        "Impact carbone de l'industrie du"
                                                        " saumon l'année passée"
                                                    ),
                                                ]
                                            )
                                        ),
                                    ]
                                ),
                            ],
                            class_name="p-3",
                        )
                    ],
                    width=12,
                ),
                class_name="my-2",
            ),
            dbc.Row(
                children=[
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.H4("État des populations de poisson"),
                                        ),
                                        dbc.Col(
                                            dbc.DropdownMenu(label="Plus"),
                                            class_name="text-right",
                                            width="auto",
                                        ),
                                    ]
                                ),
                                dbc.CardBody(
                                    [
                                        html.P("Le texte de description blablabla"),
                                        html.Img(src="./assets/graph_01.png"),
                                    ]
                                ),
                                # dbc.CardBody(
                                #     [
                                #         html.P("Le texte de description blablabla"),
                                #         dcc.Graph(
                                #             id="population_stock",
                                #             figure=make_area_chart(
                                #                 df, "iso2", "tonnes"
                                #             ),
                                #         ),
                                #     ]
                                # ),
                            ],
                            class_name="p-3",
                        ),
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.H4("État des populations de poisson"),
                                        ),
                                        dbc.Col(
                                            dbc.DropdownMenu(label="Plus"),
                                            class_name="text-right",
                                            width="auto",
                                        ),
                                    ]
                                ),
                                dbc.CardBody(
                                    [
                                        html.P("Le texte de description blablabla"),
                                        html.Img(src="./assets/graph_01.png"),
                                    ]
                                ),
                            ],
                            class_name="p-3",
                        ),
                    ),
                ]
            ),
        ],
    )
    return figures_tab


def get_data():
    logger.info("Fetching data...")
    # try:
    #     from pinkbombs.database.connect import engine
    #     connect = True
    # except Exception as e:
    #     logger.info(f"Could not connect to database: {e}")
    #     connect = False
    # if connect:
    #     try:
    #         return pd.read_sql(sql="aquaculture_weight_by_country", con=engine)
    #     except Exception as e:
    #         logger.info(f"Couldn't load data: {e}")
    return pd.DataFrame(columns=["year", "tonnes", "iso2"])


def generate_figures_tab():

    # df = get_data()
    layout = generate_figures_layout()

    return layout