import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, callback, Output, Input, dash, State
import pandas as pd
import plotly.express as px
import os
import time
from pymongo import MongoClient

last_click_time=0

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

def generate_esport_map():
    # Création du DataFrame pour les joueurs avec region_id et ladder_rank
    query_players = {"team_id": {"$ne": None}}  # Sélectionne les joueurs ayant un team_id non nul
    projection_players = {"region_id": 1, "ladder_rank": 1, "nickname": 1, "_id": 0}  # Projection des colonnes
    df_players = pd.DataFrame(list(db['Joueurs'].find(query_players, projection_players)))

    distinct_regions = Joueurs.distinct("region_id", {"team_id": {"$ne": None}})
    df_regions = pd.DataFrame(list(Regions.find({"_id": {"$in": distinct_regions}}, {"_id": 1, "countries": 1, "name": 1})))

    # Agrégation par région des valeurs de ladder_rank
    df_aggregated = df_players.groupby('region_id', as_index=False).agg({'ladder_rank': 'mean'})

    # Fusionner df_aggregated avec df_regions pour obtenir les pays associés à chaque région
    df_merged = pd.merge(df_aggregated, df_regions, left_on='region_id', right_on='_id', how='left')

    # Création de la carte choropleth
    fig = px.choropleth(
        df_merged,
        geojson=df_merged['countries'],
        locations=df_merged['region_id'],
        featureidkey="properties.NAME",  # Assurez-vous que la clé correspond à la propriété du pays dans le GeoJSON
        color='ladder_rank',
        color_continuous_scale="Plasma",
        range_color=[df_merged['ladder_rank'].min(), df_merged['ladder_rank'].max()],
        labels={'ladder_rank': 'Moyenne Ladder Rank'},
        template='plotly_dark',
    )

    # Apparence de la carte
    fig.update_geos(
        projection_type="natural earth",
        showcoastlines=True, coastlinecolor="Black",
        showland=True, landcolor="lightgray",
        showocean=True, oceancolor="lightblue",
        showframe=False,
        showcountries=True,
        countrycolor="Black",
    )

    # Ajustement
    fig.update_layout(
        geo=dict(
            showland=True,
            showcoastlines=True,
            landcolor='rgb(217, 217, 217)',
            center=dict(lon=-0, lat=0),
            projection_scale=1,
        ),
        height=500
    )

    return fig


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

    html.Div(html.I(id='output-message', children=[], style={'margin-bottom': '10px','textAlign': 'left'})),

    dcc.Graph(id='ladder-rank-histogram'),

    dcc.Graph(id='esport-map'),
    dbc.Button('Update',id='esport-map-button',n_clicks=0),
    html.Div(id='update-info'),

    html.Footer(children=[
        html.Div([
            html.Img(src=app.get_asset_url('faker.gif'), style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px', 'margin-top': '20px'}),
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
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px', 'margin-top': '20px'}),
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
            output_text=f'Region selected: {region} | Gamename: {gamename} | Tag: {tag}'
            return output_text,player_info_layout
        else:
            return 'Please select a region.',None
    else: return None, None



@app.callback(
    [Output('ladder-rank-histogram', 'figure'),
     Output('output-message', 'children')],
    [Input('dropdown-region', 'value')]
)
def update_histogram(selected_region):
    if selected_region is not None:
        players_in_region = Joueurs.find({'region_id': selected_region})
        df = pd.DataFrame(players_in_region)

        if not df.empty:  # Vérifier si le DataFrame n'est pas vide
            region = Regions.find_one({'_id': selected_region});
            fig = px.histogram(df, x='ladder_rank', nbins=20, title=f'Ladder Rank Distribution of {region["name"]}',
                               labels={'ladder_rank': 'Ladder Rank'},
                               color_discrete_sequence=['#1EDEFF'], range_x=[0,100])

            fig.update_layout(
                title=dict(text=f'Ladder Rank Distribution of {region["name"]}', font=dict(size=16), x=0.5),
                xaxis=dict(title='Ladder Rank', showgrid=False),
                yaxis=dict(title='Frequency', showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'), bargap=0.1, bargroupgap=0.1, showlegend=False
            )

            fig.update_traces(marker=dict(color='#1EDEFF'))

            fig.update_xaxes(tickfont=dict(color='white'))
            fig.update_yaxes(tickfont=dict(color='white'))

            fig.update_layout(
                annotations=[dict(
                    text='This histogram displays the distribution of ladder ranks. The lower the ladder rank, the better the players it represents.',
                    showarrow=False, xref='paper', yref='paper', x=0, y=1, align='left',
                    font=dict(size=10, color='white')
                )]
            )

            return fig, ''  # Aucun message texte à afficher
        else:
            return None, "No players found for this region in the website's database at the moment."
    else:
        return None, 'Select a region.'

@app.callback(
    Output('ladder-rank-histogram', 'style'),
    [Input('ladder-rank-histogram', 'figure')]
)
def hide_graph(figure):
    # Masquer le graphique si la figure est None
    if figure is None:
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback([Output('esport-map', 'figure'),
               Output('update-info', 'children')],
              [Input('update-button', 'n_clicks')],
              [State('update-button', 'ts')]
              )
def update_esport_map(n_clicks, ts):
    global last_click_time

    # Calcule le temps écoulé depuis le dernier clic
    elapsed_time = time.time() - last_click_time

    # Si le bouton est cliqué après 30 secondes ou plus
    if n_clicks > 0 and elapsed_time >= 30:
        # Mettez à jour le temps du dernier clic
        last_click_time = time.time()

        # Insérez ici l'appel à la fonction generate_esport_map()
        # Assurez-vous que db est accessible depuis cette fonction

        # Exemple (à adapter selon votre structure)
        fig = generate_esport_map()
        return fig, ''

    # Si le bouton est cliqué dans les 30 secondes, affichez le compteur
    elif n_clicks > 0 and elapsed_time < 30:
        return None, f"Attendez {int(30 - elapsed_time)} secondes avant de cliquer à nouveau."

    # Si le bouton n'est pas encore cliqué, affichez la carte initiale
    else:
        return generate_esport_map(), ''

if __name__ == '__main__':
    app.run_server(debug=True)
