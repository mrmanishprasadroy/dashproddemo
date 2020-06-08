import json
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from telegram_definition_L1 import *
from app import app, dbc
from datetime import datetime as dt
from datamanager import get_segment_data
import dash_table


def get_dataframe():
    """Retrieve the dataframe from Redis
    This dataframe is periodically updated through the redis task
    """
    jsonified_df = get_segment_data()
    return json.loads(jsonified_df)


def generate_front_page():
    filename = "volume Segment"
    logo_url = "https://www.sms-group.com/typo3conf/ext/bm_client/Resources/Public/Assets/img/Logo_SMSGroup.svg"

    return html.Div(
        id="report-header",
        children=[
            html.Img(id="las-logo", src=logo_url),
            html.Div(
                id="report-header-text",
                children=[
                    html.H1("Segment Measuring Point Report"),
                    html.Div(
                        id="las-file-info",
                        children=[
                            html.Span(id="source-filename", children=filename),
                        ],
                    ),
                ],
            ),
        ],
    )


def generate_axis_title(desc, unit):
    title_words = desc.split(" ")

    current_line = ""
    lines = []
    for word in title_words:
        if len(current_line) + len(word) > 15:
            lines.append(current_line[:-1])
            current_line = ""
        current_line += "{} ".format(word)
    lines.append(current_line)

    title = "<br>".join(lines)
    title += "<br>({})".format(unit)

    return title


def generate_table():
    dataset = get_dataframe()
    data = json.loads(dataset)
    MP_00 = pd.read_json(data['df_00'], orient='split')


    datatable = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in MP_00.columns],
        data=MP_00.to_dict("rows"),
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


def serve_layout():
    return html.Div(
        [
            html.Div(id="controls", children=[html.Button("Print", id="las-print")]),
            html.Div(id="frontpage", className="page", children=generate_front_page()),
            html.Div(
                className="section",
                children=[
                    html.Div(className="section-title", children="LAS well"),
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
                    html.Div(className="section-title", children="LAS curves"),
                    html.Div(
                        className="page",
                    ),
                ],
            ),
        ]
    )


@app.callback(Output("las-table-print", "children"), [Input("table", "data")])
def update_table_print(data):
    colwidths = {
        "mnemonic": "100px",
        "descr": "300px",
        "unit": "25px",
        "value": "300px",
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
