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

def get_player_info(game_name, tagline):
    player_info = Joueurs.find_one({'game_name': game_name, 'tagline': tagline})

    if not player_info:
        return [html.Div(html.I("Player not found. Try for example: Caps#45555"))]

    player_layout = [
        html.Div([
            html.H4(f"Player: {player_info['game_name']} #{player_info['tagline']}", style={'color': '#1E90FF','margin-right': '10px'}),
            html.Img(src=player_info['profile_image_url'], style={'width': '50px', 'height': '50px', 'margin-bottom': '10px'}),
        ], style={'display': 'flex', 'align-items': 'flex-start', 'justify-content': 'flex-start', 'margin-bottom': '10px'}),
        dbc.Table.from_dataframe(pd.DataFrame({
            'Level': [player_info['level']],
            'Ladder Rank (%)': [player_info['ladder_rank']],
            'Region': [player_info['region_id']],
        }), striped=True, bordered=True, hover=True),
    ]

    team_id = player_info.get('team_id')
    if team_id:
        team_info = Teams.find_one({'_id': team_id}) or {}
        team_layout = [
            html.Div([
                html.H5(f"Team: {team_info['name']}", style={'color': '#32CD32', 'margin-right': '10px'}),
                html.Img(src=team_info['image_url'], style={'width': '40px', 'height': '40px', 'margin-bottom': '10px'}),
            ], style={'display': 'flex', 'align-items': 'flex-start', 'justify-content': 'flex-start','margin-bottom': '10px'}),
            dbc.Table.from_dataframe(pd.DataFrame({
                'Authority': [player_info['authority']],
                'Nickname': [player_info['nickname']],
            }), striped=True, bordered=True, hover=True),
        ]
        player_layout.extend(team_layout)

    return player_layout

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],suppress_callback_exceptions=True)

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
                        value=regions_options[1]['value'],
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

    html.Div(id='player-info', children=[], style={'margin-bottom': '20px','textAlign': 'left'}),

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
    html.Div(id='content'),
    html.Div(id='output-container'),
    html.Div(id='player-info')
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
    [Output('output-container', 'children'),
     Output('player-info', 'children')],
    [Input('button', 'n_clicks')],
    [State('input-box', 'value'),
     State('dropdown-region', 'value')]
)
def update_output(n_clicks, value, region):
    if n_clicks > 0:
        if region is not None:
            gamename, tag = value.split('#')
            player_info_layout = get_player_info(gamename, tag)
            output_text=f'Région sélectionnée: {region}, Gamename: {gamename}, Tag: {tag}'
            return output_text,player_info_layout
        else:
            return 'Veuillez sélectionner une région.',None
    else: return None, None

if __name__ == '__main__':
    app.run_server(debug=True)
