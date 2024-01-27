import multiprocessing

import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, dash, State
import pandas as pd
import plotly.express as px
import time
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from Scrapy.crawler.crawler.spiders.opgg_project import OpggSpider


last_click_time=0

client = MongoClient('mongodb://localhost:27017/')
db = client['TestScraping']

Joueurs = db["Joueurs"]
Champions = db["Champions"]
Ranked = db["Ranked"]
MostChampPlayed = db['MostChampPlayed']
Teams = db["Teams"]
Regions=db["Regions"]

#spider=OpggSpider()
#new_url = "https://www.op.gg/summoners/euw/Caps-45555"
#request = spider.system_request(new_url)

regions_data = Regions.find({}, {'_id': 1, 'name': 1})
regions_options = [{'label': region['name'], 'value': region['_id']} for region in regions_data]

def run_crawler(new_url):
    # Configurer les paramètres du projet Scrapy
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # Ajouter le Spider à la configuration du processus
    process.crawl(OpggSpider, start_urls=[new_url])

    # Démarrer le processus (bloquant jusqu'à ce que le Spider ait terminé)
    process.start()
    process.stop()

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

def get_all_players_info():
    players_data = Joueurs.find({})
    players_content = []

    for player in players_data:
        player_id = str(player['_id'])
        player_name = player['game_name']
        profile_image_url = player['profile_image_url']

        player_card = html.Div([
            html.Img(src=profile_image_url, style={'width': '100px', 'height': '100px', 'margin-right': '10px'}),
            html.H6(children=player_name, style={'display': 'inline-block', 'margin-bottom': '10px'}),
        ], key=player_id, style={'margin-bottom': '20px', 'margin-right': '20px', 'textAlign': 'left'})

        players_content.append(player_card)

    return players_content

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
    df_aggregated = df_players.groupby('region_id', as_index=False).agg({'ladder_rank': 'mean', 'nickname': lambda x: ', '.join(x)})

    # Fusionner df_aggregated avec df_regions pour obtenir les pays associés à chaque région
    df_merged = pd.merge(df_aggregated, df_regions, left_on='region_id', right_on='_id', how='left')

    c=[]
    v=[]
    t=[]
    n=[]
    for _,ligne in df_merged.iterrows():
        if ligne['countries'] is not None:
            for country in ligne['countries']:
                c.append(country)
                v.append(ligne['ladder_rank'])
                t.append(ligne['name'])
                n.append(ligne['nickname'])

    df_map = pd.DataFrame({'country': c, 'value': v, 'region_name': t, 'nicknames': n})
    df_map = df_map.dropna(subset=['value'])

    # Création de la carte choropleth
    fig = px.choropleth(
        df_map,
        locations='country',
        locationmode='country names',
        color='value',
        title="Moyenne des Ladder Rank par serveur qu'en fonction des Joueurs PRO",
        color_continuous_scale="Plasma",
        hover_data={'country': True, 'value': True, 'region_name': True, 'nicknames': True},
        range_color=[df_map['value'].min(), df_map['value'].max()],
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
            landcolor='rgb(56, 111, 72)',
            center=dict(lon=-0, lat=0),
            projection_scale=1,
        ),
        height=500
    )
    fig.update_geos(fitbounds="locations", visible=False)

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

third_page_content = html.Div([
    html.H3(children='Joueur', style={'margin-bottom': '15px', 'textAlign': 'center'}),
    html.Div(get_all_players_info(), style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'flex-start'}),

    html.Footer(children=[
        # Ajoutez le pied de page pour la nouvelle page
        # ...
    ]),
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Button("Dashboard", id='btn-dashboard', href='/dashboard/page1', style={'margin-right': '10px'}),
    dbc.Button("Champions", id='btn-champions', href='/dashboard/page2', style={'margin-right': '10px'}),  # Ajoutez une marge à droite
    dbc.Button("Joueur", id='btn-joueur', href='/dashboard/page3', style={'margin-right': '10px'}),  # Ajoutez une marge à droite
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
    elif pathname == '/dashboard/page3':  # Ajoutez la logique pour afficher la nouvelle page
        return third_page_content
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
        if region is not None and value is not None and '#' in value:
            gamename, tag = value.split('#')
            output_text=f'Region selected: {region} | Gamename: {gamename} | Tag: {tag}'
            new_url = f"https://www.op.gg/summoners/{region}/{gamename.replace(' ', '-')}-{tag}"

            #spider = OpggSpider()
            #request=next(spider.start_requests_for_new_url(new_url))

            process=multiprocessing.Process(target=run_crawler, args=(new_url,))
            process.start()
            process.join()

            player_info_layout = get_player_info(gamename, tag)
            print(output_text, player_info_layout)
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
              [Input('esport-map-button', 'n_clicks')],
              [State('esport-map-button', 'ts')]
              )
def update_esport_map(n_clicks, ts):
    global last_click_time

    # Calcule le temps écoulé depuis le dernier clic
    elapsed_time = time.time() - last_click_time

    # Si le bouton est cliqué après 30 secondes ou plus
    if n_clicks > 0 and elapsed_time >= 30:
        # Mettez à jour le temps du dernier clic
        last_click_time = time.time()
        fig = generate_esport_map()
        return fig, ''

    # Si le bouton est cliqué dans les 30 secondes, affichez le compteur
    elif n_clicks > 0 and elapsed_time < 30:
        return None, f"Attendez {int(30 - elapsed_time)} secondes avant de cliquer à nouveau."

    # Si le bouton n'est pas encore cliqué, affichez la carte initiale
    else:
        return generate_esport_map(), ''

@app.callback(
    Output('player-info-container', 'children'),
    [Input('button', 'n_clicks')],
    [State('input-box', 'value'),
     State('dropdown-region', 'value')]
)
def update_player_info_page(n_clicks, value, region):
    if n_clicks > 0:
        if region is not None and value is not None and '#' in value:
            gamename, tag = value.split('#')
            player_info_layout = get_player_info(gamename, tag)
            return player_info_layout
        else:
            return [html.Div(html.I("Please select a region and enter a valid Game Name + #Tag."))]
    else:
        return []







if __name__ == '__main__':
    app.run_server(debug=True)
