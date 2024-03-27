import dash_bootstrap_components as dbc
import flask
from dash import Dash

from pinkbombs.layout.layout import create_layout


server = flask.Flask(__name__)
app = Dash(
    __name__,
    assets_folder="./assets",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    server=server,
)
app.layout = create_layout()


@server.route("/")
def index():
    return app.index()


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
