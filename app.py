import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import flask


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True
server = app.server


# returns top indicator div
def indicator(color, text, id_value):
    return html.Div(
        [

            html.P(
                text,
                className="twelve columns indicator_text"
            ),
            html.P(
                id=id_value,
                className="indicator_value"
            ),
        ],
        className="four columns indicator",

    )
