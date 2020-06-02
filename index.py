import dash_core_components as dcc
import dash_html_components as html
from app import app
from apps import production, stoptime
from dash.dependencies import Input, Output

app.layout = html.Div(
    [
        # header
        html.Div([

            html.Span("PLTCM  DashBorad", className='app-title'),

            html.Div(
                html.Img(
                    src='assets/logo.png',
                    height="100%")
                , style={"float": "right", "height": "80%", "padding": "5px"})
        ],
            className="row header"
        ),

        # tabs
        html.Div([

            dcc.Tabs(
                id="tabs",
                style={"height": "20", "verticalAlign": "middle"},
                children=[
                    dcc.Tab(label="Production", value="production_tab"),
                    # dcc.Tab(label="Coil Report", value="coilreport_tab"),
                    dcc.Tab(id="stoptime_tab", label="Stop Times", value="stoptime_tab"),
                ],
                value="production_tab",
            )

        ],
            className="row tabs_div"
        ),
        # Tab content
        html.Div(id="tab_content", className="row", style={"margin": "2% 3%"}),

    ],
    className="row",
    style={"margin": "0%"},
)


@app.callback(Output("tab_content", "children"), [Input("tabs", "value")])
def render_content(tab):
    if tab == "production_tab":
        return production.serve_layout()
    elif tab == "stoptime_tab":
        return stoptime.serve_layout()
    else:
        return production.serve_layout()


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
