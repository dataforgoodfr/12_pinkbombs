import dash_bootstrap_components as dbc
from dash import Dash

from src.layout import create_layout

if __name__ == "__main__":

    app = Dash(
        __name__, assets_folder="./assets", external_stylesheets=[dbc.themes.BOOTSTRAP]
    )
    app.layout = create_layout()

    app.run(debug=True)
