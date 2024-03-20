import dash_bootstrap_components as dbc
from dash import html


def generate_story_tab() -> dbc.Col:
    """Generate the History tab with images and text."""

    story_tab = dbc.Col(
        children=[
            dbc.Row(
                id="landing_frame",
                children=[html.Img(src="assets/salmon_01.png")],
                class_name="flex-grow-1",
                style={"height": "100vh"},
            ),
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

    return story_tab
