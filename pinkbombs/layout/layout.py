import dash_bootstrap_components as dbc

from pinkbombs.layout.figures_tab import generate_figures_tab
from pinkbombs.layout.story_tab import generate_story_tab


def create_layout() -> dbc.Container:
    """Create main layout container with callbacks

    Returns:
        dbc.Container: Layout container
    """

    layout = dbc.Container(
        children=[
            dbc.Tabs(
                active_tab="story",
                children=[
                    dbc.Tab(
                        label="L'histoire",
                        children=generate_story_tab(),
                        tab_style={"marginLeft": "auto"},
                        tab_id="story",
                    ),
                    dbc.Tab(
                        label="Les chiffres",
                        children=generate_figures_tab(),
                        tab_id="figures",
                    ),
                ],
            )
        ],
        style={"margin-top": "20px"},
    )

    return layout
