import dash_core_components as dcc
import dash_html_components as html
from app import app, dbc
from apps import production, stoptime
from dash.dependencies import Input, Output

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "300px",
    "padding": "2rem 1rem",
    "background-color": "#2e3135",
    "color":"#fff"
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "35rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": "#f3f4f6",
}
logo_url = "https://www.sms-group.com/typo3conf/ext/bm_client/Resources/Public/Assets/img/Logo_SMSGroup.svg"
sidebar = html.Div(
    [
        dbc.CardImg(src=logo_url, top=True),
        html.H2("Production Data", className="display-4"),
        html.Hr(className="sms-navigation-divider"),
        dbc.Nav(
            [
                dbc.NavItem(dbc.NavLink('Production Data ', href='/apps/prod_data', active=True)),
                dbc.NavItem(dbc.NavLink('Stop Data ', href='/apps/stop_data', active=True)),
            ],
            vertical=True,
            pills=True,
        ),
        html.H2("Machine Data", className="display-4"),
                html.Hr(),
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink('Segment Data ', href='/apps/prod_data', active=True)),
                        dbc.NavItem(dbc.NavLink('Process Data ', href='/apps/stop_data', active=True)),
                    ],
                    vertical=True,
                    pills=True,
                ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/apps/prod_data"]:
        return production.serve_layout()
    elif pathname == "/apps/stop_data":
        return stoptime.serve_layout()
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
