# -*- coding: utf-8 -*-

from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go

from app import app, indicator
from datamanager import get_stop_time


def date_source(df, time):
    types = df[time]
    values = df["mean"]
    if time == "HOUR":
        data = [go.Scatter(x=types, y=values, line=dict(dash='solid', width=2))]
        layout = dict(
            xaxis={"title": "Hours"},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    elif time == 'YEAR':
        data = [go.Pie(
            labels=types,
            values=values,
            marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
        )]

        layout = dict(margin=dict(l=15, r=10, t=0, b=65), legend=dict(orientation="h"))

    else:
        data = [go.Bar(x=types, y=values,
                       orientation="v")]  # x could be any column value since its a count
        layout = go.Layout(
            barmode="stack",
            margin=dict(l=210, r=25, b=20, t=0, pad=4),
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

    return {"data": data, "layout": layout}


def default_layout_null():
    return html.Div(style={'display': 'none'})


def serve_layout():
    return html.Div(
        [

            html.Div(
                [
                    html.Div(
                        dcc.DatePickerRange(
                            id='date-range',
                            min_date_allowed=dt(2017, 8, 5),
                            max_date_allowed=dt.now(),
                            initial_visible_month=dt.now(),
                            end_date=dt.now()
                        ),
                        className="four columns",
                    ),
                    html.Div(html.Button(id='submit-button', n_clicks=0, children='Submit',
                                         className='button button-primary'), className="two columns"),
                    html.Div(id="status_stop", className="four columns"),
                ],
                className="row",
                style={"marginBottom": "10"},
            ),
            # Interval
            dcc.Interval(interval=60 * 1000, id="interval_stop"),

            # indicators row div
            html.Div(
                [
                    indicator(
                        "#00cc96", "Total Delay Duartion PL in Min", "left_PL_indicator"
                    ),
                    indicator(
                        "#119DFF", "Total Delay Duartion TCM in Min", "middle_TCM_indicator"
                    ),
                    indicator(
                        "#EF553B",
                        "Total Delay Duartion PLTCM in Min",
                        "right_PLTCM_indicator",
                    ),
                ],
                className='row',
            ),

            # charts row div
            html.Div(
                [
                    html.Div(
                        [
                            html.P("Yearly Avg Delay"),
                            dcc.Graph(
                                id="yearly_analysis",
                                style={"height": "90%", "width": "98%"},
                                config=dict(displayModeBar=False),
                            ),
                        ],
                        className="four columns chart_div"
                    ),
                    html.Div(
                        [
                            html.P("Monthly Avg Delay"),
                            dcc.Graph(
                                id="monthly_analysis",
                                style={"height": "90%", "width": "98%"},
                                config=dict(displayModeBar=False),
                            ),
                        ],
                        className="four columns chart_div"
                    ),
                    html.Div(
                        [
                            html.P("hourly Avg Delay"),
                            dcc.Graph(
                                id="hour_analysis",
                                style={"height": "90%", "width": "98%"},
                                config=dict(displayModeBar=False),
                            ),
                        ],
                        className="four columns chart_div"
                    ),

                    # Hidden div inside the app that stores the intermediate value
                    html.Div(id='intermediate-value', style={'display': 'none'}),

                ],
                className="row",
                style={"marginTop": "5"},

            ),
            dcc.Input(id="input-1", value='Input triggers local spinner', style={'display': 'none'}),
            html.Div(id="parttime_df", style={'display': "none"}),
            # dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="default"),

            # table div
            dcc.Loading(id='table-view', children=html.Div(
                id="stop_table",
                className="row",
                style={
                    #  "maxHeight": "320px",
                    #  "overflowY": "scroll",
                    "padding": "8",
                    "marginTop": "5",
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px"

                },
            ), type="default"),

        ]
    )


@app.callback(
    Output("status_stop", "children"),
    [Input("interval_stop", "n_intervals")],
)
def update_status(_):
    data_last_updated = dt.now()

    return "Data last updated at {}".format(data_last_updated)


# update hidden div data block
@app.callback(
    Output('parttime_df', 'children'),
    [Input("interval_stop", "n_intervals"), Input('submit-button', 'n_clicks')],
    [State("date-range", "start_date"),
     State("date-range", "end_date")]
)
def store_data(_, n_clicks, start_date, end_date):
    df = get_stop_time()
    if n_clicks > 0:
        df_1 = df.set_index('DATE')
        df = df_1.loc[start_date:end_date]
        cleaned_df = df.reset_index()
    else:
        cleaned_df = df
    return cleaned_df.to_json(orient="split")


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
            style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center'},
            style_header={
                'backgroundColor': 'white',
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
