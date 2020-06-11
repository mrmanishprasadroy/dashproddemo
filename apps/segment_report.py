import json

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots

from app import app, dbc
from datamanager import get_segment_data


def get_dataframe():
    """Retrieve the dataframe from Redis
    This dataframe is periodically updated through the redis task
    """
    jsonified_df = get_segment_data()
    return json.loads(jsonified_df)


def generate_front_page():
    filename = "Volume Segment"

    return html.Div(
        id="las-header",
        children=[
            html.Div(
                id="las-header-text",
                children=[
                    html.H1("Segment Measuring Point Report")
                ],
            ),
        ],
    )


def generate_table():
    dataset = get_dataframe()
    data = json.loads(dataset)
    MP = pd.read_json(data['df_00'], orient='split')
    col = ["time",
           "SegId",
           "SetupId",
           "CoilId",
           "LenSegStart",
           "TmSinceThread",
           "TmSeg",
           "VolSeg",
           "NumValSeg" ]
    MP_00 = MP[col]
    datatable = dash_table.DataTable(
        id="table",
        columns=[{"name": i, "id": i} for i in MP_00.columns],
        data=MP_00.head(100).to_dict("rows"),
        fixed_rows={'headers': True, 'data': 0},
        # filtering=True,
        sort_action="native",
        style_cell={
            "padding": "5px",
            "midWidth": "0px",
            "textAlign": "center",
            "border": "white",
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_data={'border': '1px solid blue'},
        style_header={'border': '1px solid pink'},
    )
    return datatable


print_button = html.Div(
    [
        html.Div(id="controls", children=[dbc.Button("Print Report", id="las-print", size="lg", className="mr-1")]),
    ]
)


def serve_layout():
    return html.Div(
        [
            print_button,
            html.Div(id="frontpage", className="page", children=generate_front_page()),
            html.Div(
                className="section",
                children=[
                    html.Div(className="section-title", children="Measuring Point 01"),
                    html.Div(
                        className="page",
                        children=[
                            html.Div(id="las-table", children=generate_table()),
                            html.Div(id="las-table-print"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="section",
                children=[
                    html.Div(className="section-title", children="Segment Curves"),
                    html.Div(
                        className="page",
                        children=[html.Div(id="las-curves", children=generate_curves())],
                    ),
                ],
            ),
        ]
    )


@app.callback(Output("las-table-print", "children"), [Input("table", "data")])
def update_table_print(data):
    colwidths = {
        "time": "75px",
        "SegId": "25px",
        "SetupId": "25px",
        "CoilId": "25px",
        "LenSegStart": "25px",
        "TmSinceThread": "25px",
        "TmSeg": "25px",
        "VolSeg": "25px",
        "NumValSeg": "25px",
        "TmSeg": "25px",
        "VolSeg": "25px",
    }
    tables_list = []
    num_tables = int(len(data) / 34) + 1  # 34 rows max per page
    for i in range(num_tables):
        table_rows = []
        for j in range(34):
            if i * 34 + j >= len(data):
                break
            table_rows.append(
                html.Tr([html.Td(data[i * 34 + j][key]) for key in data[0].keys()])
            )
        table_rows.insert(
            0,
            html.Tr(
                [
                    html.Th(key.title(), style={"width": colwidths[key]})
                    for key in data[0].keys()
                ]
            ),
        )
        tables_list.append(
            html.Div(className="tablepage", children=html.Table(table_rows))
        )
    return tables_list


def generate_curves(
        height=900,
        width=1400,
):
    fig = make_subplots(rows=4, cols=3, shared_yaxes=True, shared_xaxes=True)
    dataset = get_dataframe()
    data = json.loads(dataset)
    MP_00 = pd.read_json(data['df_00'], orient='split')
    MP_01 = pd.read_json(data['df_01'], orient='split')
    MP_02 = pd.read_json(data['df_02'], orient='split')
    MP_03 = pd.read_json(data['df_03'], orient='split')
    MP_04 = pd.read_json(data['df_04'], orient='split')
    MP_05 = pd.read_json(data['df_05'], orient='split')
    MP_06 = pd.read_json(data['df_06'], orient='split')
    MP_07 = pd.read_json(data['df_07'], orient='split')
    MP_08 = pd.read_json(data['df_08'], orient='split')
    MP_09 = pd.read_json(data['df_09'], orient='split')
    MP_10 = pd.read_json(data['df_10'], orient='split')
    # MP_01.to_csv('data', sep='\t', encoding='utf-8')
    # index = pd.to_datetime(MP_02['time'], format="%Y-%m-%d %H:%M:%S.%f")
    item = "VolSeg"
    # Create and style traces
    fig.add_trace(go.Scatter(
        x=MP_00['time'],
        y=MP_00[item],
        name=' At MP 00',
        text=MP_00[item]
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=MP_01['time'],
        y=MP_01[item],
        name=' At MP 01',
        text=MP_01[item]
    ), row=1, col=2)
    fig.add_trace(go.Scatter(
        x=MP_02['time'],
        y=MP_02[item],
        name='At MP 02',
        text=MP_02[item]
    ), row=1, col=3)
    fig.add_trace(go.Scatter(
        x=MP_03['time'],
        y=MP_03[item],
        name=' At MP 03',
        text=MP_03[item]
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=MP_04['time'],
        y=MP_04[item],
        name=' At MP 04',
        text=MP_04[item]
    ), row=2, col=2)
    fig.add_trace(go.Scatter(
        x=MP_05['time'],
        y=MP_05[item],
        name=' At MP 05',
        text=MP_05[item]
    ), row=2, col=3)
    fig.add_trace(go.Scatter(
        x=MP_06['time'],
        y=MP_06[item],
        name=' At MP 06',
        text=MP_06[item],
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=MP_07['time'],
        y=MP_07[item],
        name=' At MP 07',
        text=MP_07[item]
    ), row=3, col=2)
    fig.add_trace(go.Scatter(
        x=MP_08['time'],
        y=MP_08[item],
        name=' At MP 08',
        text=MP_08[item]
    ), row=3, col=3)
    fig.add_trace(go.Scatter(
        x=MP_09['time'],
        y=MP_09[item],
        name=' At MP 09',
        text=MP_09[item]
    ), row=4, col=1)
    fig.add_trace(go.Scatter(
        x=MP_10['time'],
        y=MP_10[item],
        name=' At MP 10',
        text=MP_10[item]
    ), row=4, col=2)

    # #############################################################################
    # IMPORTANT | Set the global font properties of the figure
    fig.update_layout(
        font=dict(
            family="Time New Roman",
            size=18,
            color="red"),
        width=width,
        height=height
    )

    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                {
                    'showarrow': False,
                    'text': 'Volume Segment',
                    'x': 0.5,
                    'xanchor': 'center',
                    'xref': 'paper',
                    'y': 0,
                    'yanchor': 'top',
                    'yref': 'paper',
                    'yshift': -30,

                    "font": dict(
                        # family="Courier New, monospace",
                        size=18,
                        # color="#ffffff"
                    ),

                })
        ]
    )
    return dcc.Graph(figure=fig)
