# -*- coding: utf-8 -*-
import math
from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import numpy as np
import pandas as pd
from dash.dependencies import Input, Output, State
from plotly import graph_objs as go

from app import app, dbc
from datamanager import get_production


# returns pie chart that shows coils per alloycode
def alloy_source(df):
    types = df["ALLOYCODE"]
    values = df["count"]
    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65), legend=dict(orientation="h"))

    return dict(data=[trace], layout=layout)


# returns pie chart that shows width per coils
def width_source(df):
    types = df["ENTRYWIDTH"]
    values = df["count"]
    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65))

    return dict(data=[trace], layout=layout)


# returns pie chart that shows thickness per coils
def thickness_pie_source(df):
    types = df["EXITTHICK"]
    values = df["count"]
    trace = go.Pie(
        labels=types,
        values=values,
        marker={"colors": ["#264e86", "#0074e4", "#74dbef", "#eff0f4"]},
    )

    layout = dict(margin=dict(l=15, r=10, t=0, b=65))

    return dict(data=[trace], layout=layout)


def thickness_source(df):
    types = df["EXITTHICK"]
    values = df["count"]
    data = [go.Scatter(x=types, y=values, line=dict(dash='solid', width=2))]
    layout = dict(
        xaxis={"title": "Exit Thickness"},
        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
        legend={'x': 0, 'y': 1},
        hovermode='closest'
    )

    return {"data": data, "layout": layout}


# function to perform date range filter
def filter_data(df, start_date, end_date):
    if start_date is not None:
        start_date = pd.to_datetime(start_date)
    if end_date is not None:
        end_date = pd.to_datetime(end_date)

    df['DTENDROLLING'] = pd.to_datetime(df['DTENDROLLING'])

    if start_date is not None:
        mask = (df['DTENDROLLING'] > start_date) & (df['DTENDROLLING'] <= end_date)
        df = df.loc[mask]
    return df


# Bar Chart for Weight Analysis
def date_weight_source(df, time):
    types = df[time]
    values = np.round(df["EXITWEIGHTMEAS"])
    if time == "Day":
        data = [go.Scatter(x=types, y=values, line=dict(dash='solid', width=2))]
        layout = dict(
            xaxis={"title": "Date Time",
                   'rangeselector': {'buttons': list([
                       {'count': 1, 'label': '1M', 'step': 'day', 'stepmode': 'backward'},
                       {'count': 10, 'label': '6M', 'step': 'month', 'stepmode': 'backward'},
                       {'step': 'all'}
                   ])}, 'rangeslider': {'visible': True}, 'type': 'date'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    elif time == 'year':
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
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

    return {"data": data, "layout": layout}


def default_layout_null():
    return html.Div(style={'display': 'none'})


""" Layout Elements"""
""" Top Element """
alert = dbc.Alert(
    [
        dbc.Row([
            dbc.Col(html.H2("Coil Production Analysis", className="alert-heading")),
            dbc.Col(html.H6(id="status_prod", className="alert-heading")),
        ]),
        html.Hr(),
        dbc.Row([
            dbc.Col(
                html.Div(
                    dcc.DatePickerRange(
                        id='date-picker-range',
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
count_Indicator = [
    dbc.CardHeader("Coils Count"),
    dbc.CardBody(
        [
            html.H4(html.P(id="left_leads_indicator", className="card-text", style={'text-align': 'center'})),
        ]
    ),
]
weight_Indicator = [
    dbc.CardHeader("Total Weight in ton"),
    dbc.CardBody(
        [
            html.H4(html.P(id="middle_leads_indicator", className="card-text", style={'text-align': 'center'})),
        ]
    ),
]

tonnage_Indicator = [
    dbc.CardHeader("Tonnage Per coil in kg"),
    dbc.CardBody(
        [
            html.H4(html.P(id="right_leads_indicator", className="card-text", style={'text-align': 'center'})),
        ]
    ),
]

indicators = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(count_Indicator, color="primary", inverse=True)),
                dbc.Col(dbc.Card(weight_Indicator, color="secondary", inverse=True)),
                dbc.Col(dbc.Card(tonnage_Indicator, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
    ]
)

# Tonnage Graph Card
yearly_weight_graph = [
    dbc.CardHeader("Yearly Production Weight Analysis"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="yearly_weight_source",
            ),
        ]
    ),
]

monthly_weight_graph = [
    dbc.CardHeader("Monthly Production Weight Analysis"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="monthly_weight_source",
            ),
        ]
    ),
]
daily_weight_graph = [
    dbc.CardHeader("Daily Production Weight Analysis"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="hour_weight_source",
            ),
        ]
    ),
]

prod_weight_card = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(yearly_weight_graph, color="primary", inverse=True)),
                dbc.Col(dbc.Card(monthly_weight_graph, color="secondary", inverse=True)),
                dbc.Col(dbc.Card(daily_weight_graph, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
    ]
)
""" Model """
alloy_table_model = [
    dbc.CardHeader("Alloy Code Statistics"),
    dbc.CardBody(
        [
            html.Div(
                id="alloy_thickness_table",
                style={
                    "maxHeight": "320px",
                    "overflowY": "scroll",
                    "padding": "8",
                    "marginTop": "5",
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px"
                }
            )
        ]
    )
]

witdth_table_model = [
    dbc.CardHeader("Width Statistics"),
    dbc.CardBody(
        [
            html.Div(
                id="width_thickness_table",
                style={
                    "maxHeight": "320px",
                    "overflowY": "scroll",
                    "padding": "8",
                    "marginTop": "5",
                    "backgroundColor": "white",
                    "border": "1px solid #C8D4E3",
                    "borderRadius": "3px"
                }
            )
        ]
    )
]

thickness_table_model = [
    dbc.CardHeader("Exit Thickness Statistics"),
    dbc.CardBody(
        [
            html.Div(
                id="exit_thickness_weight_table",
                style={
                    "overflowY": "scroll",
                }
            )
        ]
    )
]

""" Count Graph Count"""
alloy_count_graph = [
    dbc.CardHeader("Coils count with Alloy Code"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="alloy_source",
            ),
        ]
    ),
]

entry_width_count_graph = [
    dbc.CardHeader("Coils count with Entry width"),
    dbc.CardBody(
        [
            dcc.Graph(
                id="width_source",
            ),
        ]
    ),
]

exit_thickness_count_graph = [
    dbc.CardHeader("Coils count with Exit Thickness"),
    dbc.CardBody(
        [
            html.Div(
                dcc.RangeSlider(
                    id='thicknessslider',
                    marks={i: 'Thick.  {} mm'.format(i) for i in range(0, 4)},
                    min=-0,
                    max=3,
                    step=0.1,
                    value=[0, 3]
                ),
            ),
            dcc.Graph(
                id="thickness_leads",
            ),
        ]
    ),
]

count_graph_card = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(alloy_count_graph, color="primary", inverse=True)),
                dbc.Col(dbc.Card(entry_width_count_graph, color="secondary", inverse=True)),
                dbc.Col(dbc.Card(exit_thickness_count_graph, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
    ]
)

tables_card = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(dbc.Card(alloy_table_model, color="primary", inverse=True)),
                dbc.Col(dbc.Card(witdth_table_model, color="secondary", inverse=True)),
                dbc.Col(dbc.Card(thickness_table_model, color="info", inverse=True)),
            ],
            className="mb-4",
        ),
    ]
)
modal = html.Div(
    [
        dbc.Button("Open modal", id="open"),
        dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody("This is the content of the modal"),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal",
        ),
    ]
)


def serve_layout():
    return html.Div(
        [
            # Interval
            dcc.Interval(interval=60 * 1000, id="interval_prod"),
            # Alert
            alert,
            # Indicators
            indicators,

            # Production Graph
            prod_weight_card,

            # Count Graph,
            count_graph_card,

            # Model
            tables_card,

            html.Div(id="time_df", style={'display': "none"}),
        ]
    )


@app.callback(
    Output("status_prod", "children"),
    [Input("interval_prod", "n_intervals")],
)
def update_status(_):
    time_now = str(dt.now())
    data_last_updated = dt.strptime(time_now[:19], "%Y-%m-%d %H:%M:%S")
    return "Data last updated at {}".format(data_last_updated)


@app.callback(Output('time_df', 'children'),
              [Input("interval_prod", "n_intervals"), Input('submit-button', 'n_clicks')],
              [State("date-picker-range", "start_date"),
               State("date-picker-range", "end_date")])
def update_output(_, n_clicks, start_date, end_date):
    df = get_production()
    df['DTENDROLLING'] = pd.to_datetime(df['DTENDROLLING'])
    df['Date'] = df.DTENDROLLING.dt.date
    if n_clicks > 0:
        df = filter_data(df, start_date, end_date)
    else:
        pass
    return df.to_json(orient='split')


# module One
@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# updates left indicator based on df updates
@app.callback(
    Output("left_leads_indicator", "children"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def left_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    coil_count = len(df)
    if coil_count > 0:
        return coil_count
    else:
        return 0


# updates middle indicator based on df updates
@app.callback(
    Output("middle_leads_indicator", "children"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def middle_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    return math.floor((df['EXITWEIGHTMEAS'].aggregate(sum)) / 1000)


# updates right indicator based on df updates
@app.callback(
    Output("right_leads_indicator", "children"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def right_leads_indicator_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    coil_count = len(df)
    if coil_count > 0:
        tot_weight = df['EXITWEIGHTMEAS'].aggregate(sum)
        return math.floor(tot_weight / coil_count)
    else:
        return 0


# update pie chart figure df updates
@app.callback(
    Output("alloy_source", "figure"),
    [Input('submit-button', 'n_clicks'), Input("time_df", "children")],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def alloy_source_callback(n_clicks, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        allycode_stats = df.groupby('ALLOYCODE')['EXITTHICK'].describe().reset_index()
        return alloy_source(allycode_stats)
    else:
        return default_layout_null()


# update bar chart figure df updates
@app.callback(
    Output("yearly_weight_source", "figure"),
    [Input('submit-button', 'n_clicks'), Input("time_df", "children")],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def weight_source_callback(n_clicks, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df):
        df['year'] = df.Date.dt.year
        exitweightperday = df.groupby('year')['EXITWEIGHTMEAS'].sum().reset_index()
        exitweightperday['EXITWEIGHTMEAS'] = np.round(exitweightperday.EXITWEIGHTMEAS / 1000)
        return date_weight_source(exitweightperday, 'year')
    else:
        return default_layout_null()


# update bar chart figure df updates
@app.callback(
    Output("monthly_weight_source", "figure"),
    [Input('submit-button', 'n_clicks'), Input("time_df", "children")],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def weight_source_callback(n_clicks, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df):
        df['month'] = df.Date.map(lambda x: x.strftime('%Y-%m'))
        exitweightperday = df.groupby('month')['EXITWEIGHTMEAS'].sum().reset_index()
        exitweightperday['EXITWEIGHTMEAS'] = np.round(exitweightperday.EXITWEIGHTMEAS / 1000)
        return date_weight_source(exitweightperday, 'month')
    else:
        return default_layout_null()


# update bar chart figure df updates
@app.callback(
    Output("hour_weight_source", "figure"),
    [Input('submit-button', 'n_clicks'), Input("time_df", "children")],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def weight_source_callback(n_clicks, df, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df):
        df['Day'] = df.Date.dt.date
        exitweightperday = df.groupby('Day')['EXITWEIGHTMEAS'].sum().reset_index()
        exitweightperday['EXITWEIGHTMEAS'] = np.round(exitweightperday.EXITWEIGHTMEAS / 1000)
        return date_weight_source(exitweightperday, 'Day')
    else:
        return default_layout_null()


# update pie chart figure df updates
@app.callback(
    Output("width_source", "figure"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def width_source_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        width_stats = df.groupby('ENTRYWIDTH')['EXITTHICK'].describe().reset_index()
        return width_source(width_stats)
    else:
        return default_layout_null()


# update pie chart figure df updates
@app.callback(
    Output("thickness_leads", "figure"),
    [Input("thicknessslider", "value"),
     Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")]
)
def thickness_source_callback(value, df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        thickness_stats = df.groupby('EXITTHICK')['EXITWEIGHTMEAS'].describe().reset_index()
        thickness_stats = thickness_stats[thickness_stats['EXITTHICK'] <= value[1]]
        return thickness_source(thickness_stats)
    else:
        return default_layout_null()


# update table based on drop down value and df updates
@app.callback(
    Output("alloy_thickness_table", "children"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")],
)
def aleads_table_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('ALLOYCODE')['EXITTHICK'].describe()
        df = df.reset_index().rename(
            columns={'ALLOYCODE': 'Alloy Code', 'count': 'Coils Count', 'min': 'Min. Thickness',
                     'mean': 'Avg. Thickness',
                     'max': 'Max. Thickness'})
        df['Avg. Thickness'] = df['Avg. Thickness'].round(2)
        df.drop(['std', '25%', '50%', '75%'], axis=1, inplace=True)
        datatable = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("rows"),
            # fixed_rows={'headers': True, 'data': 0},
            # filtering=True,
            sort_action="native",
            style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center',
                        'backgroundColor': 'rgb(50, 50, 50)', },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': '#3D9970',
            }],
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['COILIDOUT', 'COILIDIN', 'ALLOYCODE']
            ],
            style_header={
                'backgroundColor': 'black',
                'fontWeight': 'bold'
            },
            style_table={
                'maxHeight': '280px',
                'overflowY': 'scroll',
                # 'border': 'thin lightgrey solid'
            },
        )
        return datatable
    else:
        return default_layout_null()


# update table based on drop down value and df updates
@app.callback(
    Output("width_thickness_table", "children"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")],
)
def bleads_table_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('ENTRYWIDTH')['EXITTHICK'].describe()
        df = df.reset_index().rename(
            columns={'ENTRYWIDTH': 'Entry Width', 'count': 'Coils Count', 'min': 'Min. Thickness',
                     'mean': 'Avg. Thickness',
                     'max': 'Max. Thickness'})
        df['Avg. Thickness'] = df['Avg. Thickness'].round(2)
        df.drop(['std', '25%', '50%', '75%'], axis=1, inplace=True)
        datatable = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("rows"),
            # fixed_rows={'headers': True, 'data': 0},
            # filtering=True,
            sort_action="native",
            style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center',
                        'backgroundColor': 'rgb(50, 50, 50)', },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': '#3D9970',
            }],
            style_cell_conditional
            =[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['COILIDOUT', 'COILIDIN', 'ALLOYCODE']
            ],
            style_header={
                'backgroundColor': 'black',
                'fontWeight': 'bold'
            },
            style_table={
                'maxHeight': '280px',
                'overflowY': 'scroll',
                # 'border': 'thin lightgrey solid'
            },
        )
        return datatable
    else:
        return default_layout_null()


# update table based on drop down value and df updates
@app.callback(
    Output("exit_thickness_weight_table", "children"),
    [Input("time_df", "children"), Input('submit-button', 'n_clicks')],
    [State("date-picker-range", "start_date"),
     State("date-picker-range", "end_date")],
)
def cleads_table_callback(df, n_clicks, start_date, end_date):
    df = pd.read_json(df, orient="split")
    if len(df) > 0:
        df = df.groupby('EXITTHICK')['EXITWEIGHTMEAS'].describe()
        df = df.reset_index().rename(
            columns={'EXITTHICK': 'Ext thickness', 'count': 'Coils Count', 'min': 'Min. Weight', 'mean': 'Avg. Weight',
                     'max': 'Max. Weight'})
        df['Avg. Weight'] = df['Avg. Weight'].round(2)
        df['Ext thickness'] = df['Ext thickness'].round(2)
        df.drop(['std', '25%', '50%', '75%'], axis=1, inplace=True)
        datatable = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("rows"),
            # fixed_rows={'headers': True, 'data': 0},
            # filtering=True,
            sort_action="native",
            style_cell={'width': '150px', 'padding': '5px', 'textAlign': 'center',
                        'backgroundColor': 'rgb(50, 50, 50)', },
            style_data_conditional=[{
                'if': {'row_index': 'odd'},
                'backgroundColor': '#3D9970',
            }],
            style_cell_conditional=[
                {
                    'if': {'column_id': c},
                    'textAlign': 'left'
                } for c in ['COILIDOUT', 'COILIDIN', 'ALLOYCODE']
            ],
            style_header={
                'backgroundColor': 'rgb(30, 30, 30)',
                'fontWeight': 'bold'
            },
            style_table={
                'maxHeight': '280px',
                'overflowY': 'scroll',
                # 'border': 'thin lightgrey solid'
            },
        )

        return datatable
    else:
        return default_layout_null()
