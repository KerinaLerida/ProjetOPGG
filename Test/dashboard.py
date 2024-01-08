import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, callback, Output, Input, dash, State
import pandas as pd
import plotly.express as px
import os
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['TestScraping']

Joueurs = db["Joueurs"]
Champions = db["Champions"]
Ranked = db["Ranked"]
MostChampPlayed = db['MostChampPlayed']
Teams = db["Teams"]
Regions=db["Regions"]

regions_data = Regions.find({}, {'_id': 1, 'name': 1})
regions_options = [{'label': region['name'], 'value': region['_id']} for region in regions_data]

def get_all_champions():
    champions_data = Champions.find({})
    champions_content = []

    for champion in champions_data:
        champion_id = str(champion['_id'])
        champion_name = champion['name']
        image_url = champion['image_url']

        champion_card = html.Div([
            html.Img(src=image_url, style={'width': '50px', 'height': '50px', 'margin-right': '10px'}),
            html.H6(children=champion_name+" |", style={'display': 'inline-block', 'margin-bottom': '10px'}),
        ], key=champion_id, style={'margin-bottom': '20px', 'margin-right': '20px','textAlign': 'left'})

        champions_content.append(champion_card)

    return champions_content

gamename='Caps'
tag='45555'


# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],suppress_callback_exceptions=True)

"""# Mise en page du dashboard
app.layout = html.Div(children=[
    html.H3(children='Project : OP.GG', style={'margin-bottom': '15px','textAlign': 'center'}),
    html.H6(children='Dashboard related to League of Legends players, leveraging web scraping from the OP.GG website. | By Keren COUTON & Matthieu CONSTANTIN', style={'margin-bottom': '40px','textAlign': 'center'}),

    html.Img(src='assets/logo.png',style={'width': '80px', 'height': '100px', 'margin': 'auto', 'display': 'block', 'margin-bottom': '20px'}),

    dbc.Row(
        [
            dbc.Col([
                dbc.FormGroup([
                    #dbc.Label('Region'),
                    dcc.Dropdown(
                        id='dropdown-region',
                        options=regions_options,
                        placeholder='Select Region..',
                    ),
                ]),
            ], width=3),
            dbc.Col([
                dbc.FormGroup([
                    dcc.Input(id='input-box', type='text', value='Game Name + #Tag'),
                ]),
            ], width=2, style={'marginTop': '5px'}),
            dbc.Col([
                dbc.FormGroup([
                    dbc.Button('.GG', id='button', n_clicks=0)
                ]),
            ], width=1),
        ],
        justify='center'
    ),

    html.Div(id='output-container', children=[], style={'margin-bottom': '20px','textAlign': 'center'}),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': None, 'y': None, 'type': 'line', 'name': 'Valeur'},
            ],
            'layout': {
                'title': 'Graphique de Valeur au fil du temps'
            }
        },
    style={'margin-bottom': "20px"},
    ),

    html.Footer(children=[
        html.Div([
            html.Img(src='assets/faker.gif', style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
        html.P("© 2024 - All rights reserved. By Keren COUTON & Matthieu CONSTANTIN"),
    ])

])"""

first_page_content = html.Div(children=[
    html.H3(children='Project : OP.GG', style={'margin-bottom': '15px','textAlign': 'center'}),
    html.H6(children='Dashboard related to League of Legends players, leveraging web scraping from the OP.GG website. | By Keren COUTON & Matthieu CONSTANTIN', style={'margin-bottom': '40px','textAlign': 'center'}),

    html.Img(src=app.get_asset_url('logo.png'),style={'width': '80px', 'height': '100px', 'margin': 'auto', 'display': 'block', 'margin-bottom': '20px'}),

    dbc.Row(
        [
            dbc.Col([
                dbc.FormGroup([
                    #dbc.Label('Region'),
                    dcc.Dropdown(
                        id='dropdown-region',
                        options=regions_options,
                        placeholder='Select Region..',
                    ),
                ]),
            ], width=3),
            dbc.Col([
                dbc.FormGroup([
                    dcc.Input(id='input-box', type='text', value='Game Name + #Tag'),
                ]),
            ], width=2, style={'marginTop': '5px'}),
            dbc.Col([
                dbc.FormGroup([
                    dbc.Button('.GG', id='button', n_clicks=0)
                ]),
            ], width=1),
        ],
        justify='center'
    ),

    html.Div(id='output-container', children=[], style={'margin-bottom': '20px','textAlign': 'center'}),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': None, 'y': None, 'type': 'line', 'name': 'Valeur'},
            ],
            'layout': {
                'title': 'Graphique de Valeur au fil du temps'
            }
        },
    style={'margin-bottom': "20px"},
    ),

    html.Footer(children=[
        html.Div([
            html.Img(src=app.get_asset_url('faker.gif'), style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px'}),
        dcc.Link('Champions - A comprehensive roster of all champions', href='/dashboard/page2', style={'margin-bottom': '20px'}),
        html.P("© 2024 - All rights reserved. By Keren COUTON & Matthieu CONSTANTIN"),
    ])

])

second_page_content = html.Div([
    html.H3(children='Champions', style={'margin-bottom': '15px','textAlign': 'center'}),
    html.H6(children='A comprehensive roster of all champions | By Keren COUTON & Matthieu CONSTANTIN',style={'margin-bottom': '40px', 'textAlign': 'center'}),

    html.Div(get_all_champions(), style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'flex-start'}), #*get_all_champions(),

    html.Footer(children=[
        html.Div([
            html.Img(src=app.get_asset_url('faker.gif'), style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px'}),
        dcc.Link('Back - Return to dashboard', href='/dashboard/page1', style={'margin-bottom': '20px'}),
        html.P("© 2024 - All rights reserved. By Keren COUTON & Matthieu CONSTANTIN"),
    ]),

])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Button("Dashboard", id='btn-dashboard', href='/dashboard/page1', style={'margin-right': '10px'}),
    dbc.Button("Champions", id='btn-champions', href='/dashboard/page2'),
    html.Div(id='content')
])

# Callback pour changer la page en fonction du lien cliqué
@app.callback(Output('content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/dashboard/page2':
        return second_page_content
    else:
        return first_page_content

# Callback pour mettre à jour l'affichage en fonction du bouton et du champ de texte
@app.callback(
    Output('output-container', 'children'),
    [Input('button', 'n_clicks')],
    [State('input-box', 'value'),
     State('dropdown-region', 'value')]
)
def update_output(n_clicks, value, region):
    if n_clicks > 0:
        if region is not None:
            return f'Région sélectionnée: {region}, Texte saisi: {value}'
        else:
            return 'Veuillez sélectionner une région.'

if __name__ == '__main__':
    app.run_server(debug=True)
