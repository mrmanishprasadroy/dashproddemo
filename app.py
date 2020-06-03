import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import flask


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.DARKLY])
app.config.suppress_callback_exceptions = True
