import dash_bootstrap_components as dbc
from dash import Dash
from loguru import logger

from pinkbombs.layout.layout import create_layout

if __name__ == "__main__":

    logger.info("App started.")
    app = Dash(
        __name__,
        assets_folder="./assets",
        external_stylesheets=[dbc.themes.BOOTSTRAP],
    )
    app.layout = create_layout()

    app.run(debug=True, host="0.0.0.0")
