# -*- coding: utf-8 -*-

from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go
from dash.exceptions import PreventUpdate
from app import app, dbc
from datamanager import get_stop_time
import random


def date_source(df, time):
    types = df[time]
    values = df["mean"]
    if time == "HOUR":
        data = [go.Scatter(x=types, y=values, fill='tozeroy', line=dict(dash='solid', width=2),
                           marker_color='rgb(55, 83, 109)')]
        layout = dict(
            xaxis={"title": "Hours"},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    else:
        color_range = []
        for i in types:
            r = lambda: random.randint(0, 255)
            color = '#{:02x}{:02x}{:02x}'.format(r(), r(), r())
            color_range.append(color)
        data = [go.Bar(x=types, y=values, marker_color=color_range,
                       orientation="v")]  # x could be any column value since its a count
        layout = go.Layout(
            legend=dict(
                x=0,
                y=1.0,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            barmode="stack",
            bargap=0.15,  # gap between bars of adjacent location coordinates.
            bargroupgap=0.1  # gap between bars of the same location coordinate.
        )

    return {"data": data, "layout": layout}


def default_layout_null():
    return html.Div(style={'display': 'none'})


""" Layout Elements"""
""" Top Element """
alert = dbc.Alert(
    [
        dbc.Row([
            dbc.Col(html.H2("PLTCM Plant Performance", className="alert-heading")),
            dbc.Col(html.H6(id="status_stop", className="alert-heading")),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                html.Div(
                    dcc.DatePickerRange(
                        id='date-range',
                        min_date_allowed=dt(2017, 8, 5),
                        max_date_allowed=dt.now(),
                        initial_visible_month=dt.now(),
                        end_date=dt.now()
                    )
                ), width="auto"
            ),
            dbc.Col(
                html.Div(
                    dbc.Button(
                        id='submit-button',
                        n_clicks=0,
                        children='Submit',
                        color="primary", className="mr-1"
                    )
                ), width="auto")
        ]),
    ]
)

""" Indicators"""
pl_Indicator = [
    dbc.CardHeader("Total Delay Duartion PL in Min"),
    dbc.CardBody(
        [
            html.H4(html.P(id="left_PL_indicator", className="card-text", style={'text-align': 'center'})),
        ]
    ),
]
tcm_Indicator = [
    dbc.CardHeader("Total Delay Duartion TCM in Min"),
    dbc.CardBody(
        [
            html.H4(html.P(id="middle_TCM_indicator", className="card-text", style={'text-align': 'center'})),
        ]
    ),
]

plctm_Indicator = [
    dbc.CardHeader("Total Delay Duartion PLTCM in Min"),
    dbc.CardBody(
        [
            html.H4(html.P(id="right_PLTCM_indicator", className="card-text", style={'text-align': 'center'})),
        ]
    ),
]

indicators = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(pl_Indicator, color="primary", inverse=True)),
                dbc.Col(dbc.Card(tcm_Indicator, color="secondary", inverse=True)),
                dbc.Col(dbc.Card(plctm_Indicator, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
    ]
)

# Tonnage Graph Card
yearly_delay_graph = [
    dbc.CardHeader("Yearly Avg Delay"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="yearly_analysis",
            ),
        ]
    ),
]

monthly_delay_graph = [
    dbc.CardHeader("Monthly Avg Delay"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="monthly_analysis",
            ),
        ]
    ),
]
daily_delay_graph = [
    dbc.CardHeader("hourly Avg Delay"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="hour_analysis",
            ),
        ]
    ),
]

delay_graph_card = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(yearly_delay_graph, color="primary", inverse=True)),
                dbc.Col(dbc.Card(monthly_delay_graph, color="secondary", inverse=True)),
                dbc.Col(dbc.Card(daily_delay_graph, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
    ]
)

""" Model """
alloy_table_model = [
    dbc.CardHeader("Plant Delay Statistics", className="card-title"),
    dbc.CardBody(
        [
            html.Div(
                dcc.Loading(id='table-view', children=html.Div(
                    id="stop_table",
                ), type="cube"),

            )
        ]
    )
]
table_cards = dbc.Row(
    [dbc.Col(dbc.Card(alloy_table_model, color="primary", inverse=True))]
)


def serve_layout():
    return html.Div(
        [
            # ALeart
            alert,
            # Interval
            dcc.Interval(interval=300 * 1000, id="interval_stop"),

            # indicators row div
            indicators,

            # charts row div
            delay_graph_card,
            dcc.Input(id="input-1", value='Input triggers local spinner', style={'display': 'none'}),
            html.Div(id="parttime_df", style={'display': "none"}),
            # dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="default"),
            table_cards,
        ]
    )


@app.callback(
    Output("status_stop", "children"),
    [Input("interval_stop", "n_intervals")],
)
def update_status(_):
    time_now = str(dt.now())
    data_last_updated = dt.strptime(time_now[:19], "%Y-%m-%d %H:%M:%S")
    return "Data last updated at {} UTC".format(data_last_updated)


# update hidden div data block
@app.callback(
    Output('parttime_df', 'children'),
    [Input("interval_stop", "n_intervals"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def store_data(_, n_clicks, start_date, end_date):
    df = get_stop_time()
    if start_date and end_date is not None:
        if n_clicks > 0:
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            df1 = df.loc[(df['DATE'] > start) & (df['DATE'] <= end)]
            if df1.empty:
                raise PreventUpdate
            return df1.to_json(orient="split")
    else:
        return df.to_json(orient="split")


# updates left indicator based on df updates
@app.callback(
    Output("left_PL_indicator", "children"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df_stats = df.groupby('PLANT')['DURATION'].sum()
        return np.ceil(np.abs(df_stats[1]))
    else:
        return 0


# updates middle  indicator based on df updates
@app.callback(
    Output("middle_TCM_indicator", "children"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df_stats = df.groupby('PLANT')['DURATION'].sum()
        return np.ceil(df_stats[2])
    else:
        return 0


# updates Right  indicator based on df updates
@app.callback(
    Output("right_PLTCM_indicator", "children"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df_stats = df.groupby('PLANT')['DURATION'].sum()
        return np.ceil(df_stats[3])
    else:
        return 0


# update table based on drop down value and df updates
@app.callback(
    Output("stop_table", "children"),
    [Input("parttime_df", "children"), Input("input-1", "value"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def leads_table_callback(df, value, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('DATE')['DURATION'].describe().reset_index()

        datatable = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("rows"),
            fixed_rows={'headers': True, 'data': 0},
            # filtering=True,
            sort_action="native",
            style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center',
                        'backgroundColor': 'rgb(50, 50, 50)'},
            style_header={
                'backgroundColor': 'black',
                'fontWeight': 'bold'
            },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': '#3D9970',
            }],
            style_table={
                'maxHeight': '280px',
                # 'overflowY': 'scroll',
                #  'border': 'thin lightgrey solid'
            },
        )
        return datatable
    else:
        return default_layout_null()


# update Bar chart figure df updates
@app.callback(
    Output("yearly_analysis", "figure"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def by_date_source_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('YEAR')['DURATION'].describe().reset_index()
        figure = date_source(df, 'YEAR')
        return figure
    else:
        return default_layout_null()


# update Bar chart figure df updates
@app.callback(
    Output("monthly_analysis", "figure"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def by_date_source_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('MONTH')['DURATION'].describe().reset_index()
        figure = date_source(df, 'MONTH')
        return figure
    else:
        return default_layout_null()


# update Bar chart figure df updates
@app.callback(
    Output("hour_analysis", "figure"),
    [Input("parttime_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def by_date_source_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('HOUR')['DURATION'].describe().reset_index()
        figure = date_source(df, 'HOUR')
        return figure
    else:
        return default_layout_null()
