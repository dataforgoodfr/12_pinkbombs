import dash_bootstrap_components as dbc
from dash import dcc, html


def create_layout() -> dbc.Container:
    """Create main layout container with callbacks

    Returns:
        dbc.Container: Layout container
    """

    layout = dbc.Container(
        children=[
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="L'histoire",
                        children=generate_history_tab(),
                        tab_style={"marginLeft": "auto"},
                    ),
                    dbc.Tab(label="Les chiffres", children=generate_figures_tab()),
                ]
            )
        ],
        style={"margin-top": "20px"},
    )

    return layout


def generate_history_tab() -> dbc.Container:
    """Generate the History tab with images and text."""

    history_tab = dbc.Container(
        children=[
            dbc.Container(
                dbc.Row(
                    id="landing_frame",
                    children=[html.Img(src="assets/salmon_01.png")],
                    class_name="flex-grow-1",
                ),
                style={"height": "100vh"},
            ),
            dbc.Container(
                dbc.Row(
                    id="intro_frame",
                    children=[
                        dbc.Row(html.Img(src="assets/salmon_02.png")),
                        dbc.Row(
                            html.P(
                                """Son nom est Salmo Salar. Il y a moins de 100 ans,
                                il était le poisson sauvage le plus répandu de
                                l’hémisphère nord et constituait
                                l’une de nos principales sources sauvages de nourriture
                                pendant des milliers d’années.
                                """
                            )
                        ),
                    ],
                    class_name="flex-grow-1",
                ),
                style={"height": "100vh"},
            ),
            dbc.Row(
                id="planet_frame",
                children=[
                    dbc.Col(
                        html.P(
                            """En moins de 50 ans, il est devenu le poisson
                            d’élevage le plus consommé de notre planète. 
                            En 2021, 80 milliards de portions individuelles
                            ont été produites, et ce chiffre augmente chaque année.
                            """
                        ),
                        class_name="col-6",
                    )
                ],
                class_name="bg-image flex-grow-1 text-light",
                style={
                    "background-image": "url(/assets/salmon_03.png)",
                    "height": "683px",
                },
            ),
        ]
    )

    return history_tab


def generate_figures_tab() -> dbc.Container:
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
                                        dbc.Col(dbc.DropdownMenu(label="Plus"), class_name="text-right", width="auto"),
                                    ]
                                ),
                                dbc.CardBody([
                                    html.P("Le texte de description blablabla"),
                                    html.Img(src="./assets/graph_01.png")
                                ]),
                            ],
                        class_name="p-3"
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
                                        dbc.Col(dbc.DropdownMenu(label="Plus"), class_name="text-right", width="auto"),
                                    ]
                                ),
                                dbc.CardBody([
                                    html.P("Le texte de description blablabla"),
                                    html.Img(src="./assets/graph_01.png")
                                ]),
                            ],
                        class_name="p-3"
                        ),
                    )
                ]
            ),
        ],
    )
    return figures_tab
