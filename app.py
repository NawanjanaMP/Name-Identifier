import dash
from dash import Dash, html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import base64
import io
from dash import dash_table
from dash import dcc, html, Input, Output, State, callback_context, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import emoji
from fuzzywuzzy import fuzz
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer

nltk.download('punkt')
nltk.download('stopwords')


app = Dash(__name__, external_stylesheets=[dbc.themes.SOLAR, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = dbc.Container([
    dbc.Card([
        dbc.CardBody(
            [
            dbc.Row(
            dbc.Col(
                [
                    html.H2(
                        emoji.emojize(":memo:") + " Name Identifier " + emoji.emojize(":pushpin:"),
                        style={"textAlign": "center"},
                    ),
                    html.Hr(),
                ],
                # width=4,
            ),
            justify="center",
            ),
            ]),
    ]
    ),

    html.Br(),

    dbc.Card([ 
                dbc.CardBody(
            [ 
                    dbc.Container(
            [
                dbc.Row(
                dbc.Col(
                    [
                    html.H3("Upload Dataset  "+emoji.emojize(':package:'), className="app-header"),
                    html.P("Add your dataset here. Then we will guide through \
                                dataset modification tools where you can manipulate your dataset. ",className="body"),  
                    ]
                    #width=6,
                   
                ), justify="left",
         ),
                dbc.Row(
                dcc.Upload(
                    id='upload-data',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                        ]),
                        style= {
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'},
                        multiple = True
                    ),justify="left",
                    
                ),
                html.Br(),
                html.Hr(),
            ]

        ),
            ]
            )
            ]
            ),

    html.Br(),
    dbc.Card(
    [
        dbc.CardHeader("View Uploaded Data"),
        dbc.CardBody(
            [
                dbc.Row(
                    [                   
                    html.Div(id='output-data-upload') 
                    ]
                )
            ]
        )
    ]
    ),
    
    html.Br(),

    dbc.Card(
        [
            dbc.CardHeader("Your Data Set"),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                "Select the short name column",
                                width=3,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="short_name",               
                                    style={"width": "100%"},
                                    options=[],
                                    value=None,
                                    # multi=True,
                                ),
                                # width=9,
                            ),                                
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                "Select the full name column",
                                width=3,
                            ),
                            dbc.Col(
                                dcc.Dropdown(
                                    id="full_name",                                           
                                    style={"width": "100%"},
                                    options=[],
                                    # multi=True,
                                    value=None,
                                ),
                                # width=9,
                            ),
                        ],
                        style={"margin-top": "10px", 'display': 'flex'},
                    ),
                    
                    html.Br(),


                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    "Calculate",
                                    id="calculate-button",
                                    color="success",
                                    style={"margin-left": "10px"},
                                ), 
                            ),

                        ]
                    ),html.Br(),

                ],
            ),
        ],
            style={
                "padding": "10px",
                "margin": "10px",
                "border-color": "#b2beb5",
            },
    ),
    dbc.Card(
        [
            dbc.CardHeader("Result Table"),
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dcc.Loading(
                                id="loading-table",
                                type="default",
                                children=[
                                    dash_table.DataTable(
                                        id='results-table',
                                        columns=[
                                            {'name': 'Short Name', 'id': 'Short Name'},
                                            {'name': 'Full Name', 'id': 'Full Name'},
                                            {'name': 'Fuzzy Score', 'id': 'Fuzzy Score'},
                                            {'name': 'Semantic Score', 'id': 'Semantic Score'}
                                        ],
                                        data=[],
                                        style_data_conditional=[
                                                    {
                                                        'if': {
                                                            'column_id': 'Fuzzy Score',
                                                            'filter_query': '{Fuzzy Score} < 45'
                                                        },
                                                        'backgroundColor': 'red',
                                                        'color': 'white'
                                                    },
                                                    {
                                                        'if': {
                                                            'column_id': 'Semantic Score',
                                                            'filter_query': '{Semantic Score} < 45'
                                                        },
                                                        'backgroundColor': 'red',
                                                        'color': 'white'
                                                    }
                                                ],
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
        ],
        style={
            "padding": "10px",
            "margin": "10px",
            "border-color": "#b2beb5",
        },
    ),
])




def parse_contents(contents,filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    # print(decoded)

    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            # print(df)
        # elif 'xls' in filename:
        #     # Assume that the user uploaded an excel file
        #     df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return [{'label': i, 'value': i} for i in df.columns], [{'label': i, 'value': i} for i in df.columns]
    # return df


@app.callback(
        Output('output-data-upload', 'children'),
        Output("short_name", "options"),
        Output("full_name", "options"),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),       
        )

def update_output(contents, filename):
    if contents is not None:
        content_list = []
        options_list_1 = []
        options_list_2 = []
        for content, name in zip(contents, filename):
            options_1, options_2 = parse_contents(content, name)
            options_list_1 += options_1
            options_list_2 += options_2
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            try:
                if 'csv' in name:
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                # elif 'xls' in name:
                #     # Assume that the user uploaded an excel file
                #     df = pd.read_excel(io.BytesIO(decoded))
                content_list.append(
                    dash_table.DataTable(
                        data=df.to_dict('records'),
                        columns=[{'name': i, 'id': i} for i in df.columns]
                    )
                )
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])
        return content_list, options_list_1, options_list_2
    else:
        return None, [], []
 

def preprocess_text(text):
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [PorterStemmer().stem(token) for token in tokens if token not in stop_words]
    return " ".join(filtered_tokens)


@app.callback(
    Output('results-table', 'data'),
    Input('calculate-button', 'n_clicks'),
    State('short_name', 'value'),
    State('full_name', 'value'),
    State('output-data-upload', 'children')
)

def update_table(n_clicks, short_name, full_name, uploaded_data):
    if n_clicks and short_name and full_name and uploaded_data:
        try:
            data = uploaded_data[0]['props']['data']
            updated_data = data.copy() 
            # Calculate similarity scores and update the data
            for item in updated_data:
                fuzzy_score = fuzz.ratio(item[short_name], item[full_name])
                semantic_score = fuzz.ratio(preprocess_text(item[short_name]), preprocess_text(item[full_name]))
                item['Fuzzy Score'] = fuzzy_score
                item['Semantic Score'] = semantic_score
            return updated_data
        except KeyError:
            return []
    return []


if __name__ == '__main__':
    app.run_server(debug=True)
# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/