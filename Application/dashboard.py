import flask
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, dash, State
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from pymongo import MongoClient

client = MongoClient('mongodb://mongodb-opgg-conteneur:27017/') # Connexion au serveur MongoDB
db = client['TestScraping']                 # Connexion à la base de données

Joueurs = db["Joueurs"]                         # Récupération de la collection Joueurs
Champions = db["Champions"]                     # Récupération de la collection Champions
Ranked = db["Ranked"]                           # Récupération de la collection Ranked
MostChampPlayed = db['MostChampPlayed']         # Récupération de la collection MostChampPlayed
Teams = db["Teams"]                             # Récupération de la collection Teams
Regions=db["Regions"]                           # Récupération de la collection Regions

regions_data = Regions.find({}, {'_id': 1, 'name': 1})                                           # Récupération des id des différentes régions
regions_options = [{'label': region['name'], 'value': region['_id']} for region in regions_data] # Création des options pour le dropdown

def get_all_champions(): # Récupération de tous les champions sous forme de cartes HTML
    champions_data = Champions.find({})         # Récupération de tous les champions
    champions_content = []                      # Liste des cartes HTML

    for champion in champions_data:             # Pour chaque champion
        champion_id = str(champion['_id'])          # Récupération de l'id
        champion_name = champion['name']            # Récupération du nom
        image_url = champion['image_url']           # Récupération de l'url de l'image

        # Création de la carte HTML
        champion_card = html.Div([
            html.Img(src=image_url, style={'width': '80px', 'height': '80px', 'margin-right': '10px'}),
            html.H6(children=champion_name+" |", style={'display': 'inline-block', 'margin-bottom': '10px'}),
        ], key=champion_id, style={'margin-bottom': '20px', 'margin-right': '20px','textAlign': 'left'})

        champions_content.append(champion_card) # Ajout de la carte à la liste

    return champions_content # Retourne la liste des cartes

def get_all_players_info(): # Récupération de tous les joueurs sous forme de cartes HTML
    players_data = Joueurs.find({})                     # Récupération de tous les joueurs
    players_content = []                                # Liste des cartes HTML

    for player in players_data:                         # Pour chaque joueur
        player_id = str(player['_id'])                      # Récupération de l'id
        player_name = player['game_name']                   # Récupération du nom
        player_tag=player['tagline']                        # Récupération du tag
        profile_image_url = player['profile_image_url']     # Récupération de l'url de l'image

        # Création de la carte HTML
        player_card = html.Div([
            html.Img(src=profile_image_url, style={'width': '80px', 'height': '80px', 'margin-right': '10px'}),
            html.H6(children=player_name+"#"+player_tag+" |", style={'display': 'inline-block', 'margin-bottom': '10px'}),
        ], key=player_id, style={'margin-bottom': '20px', 'margin-right': '20px', 'textAlign': 'left'})

        players_content.append(player_card) # Ajout de la carte à la liste

    return players_content # Retourne la liste des cartes

def get_ranked_info(ranked): # Récupération des informations ranked sous forme de cartes HTML

    ranked=ranked[len(ranked)-1]['tier_info']   # Récupération des dernières informations concernant le classement en "Ranked" du joueur
    tier=ranked['tier']                         # Récupération du rang : Iron / Bronze / Silver / Gold / Platinum / Diamond / Master / Grandmaster / Challenger
    division=ranked['division']                 # Récupération de la division : I / II / III / IV
    lp=ranked['lp']                             # Récupération des points de ligue LP
    tier_image_url=ranked['tier_image_url']     # Récupération de l'url de l'image du rang

    # Création de la carte HTML
    return [html.Div([
        html.H4(f"Ranked: {tier} {division}, {lp} LP", style={'color': '#FFD700','margin-right': '10px'}),
        html.Img(src=tier_image_url, style={'width': '50px', 'height': '50px', 'margin-bottom': '10px'}),
    ], style={'display': 'flex', 'align-items': 'flex-start', 'justify-content': 'flex-start', 'margin-bottom': '10px'})]

def get_champ_stats(champ_stats): # Récupération des informations des champions les plus joués par le joueur sous forme de tableau HTML
    n=0                                 # Nombre de champions à afficher (n)
    if len(champ_stats)>0 :             # Si le joueur a joué au moins un champion
        if len(champ_stats)>=3 :            # Si le joueur a joué au moins 3 champions
            n=3                                 # On affiche les 3 champions les plus joués
        else :
            n=len(champ_stats)              # Sinon on affiche tous les champions joués
    else:
        return []                           # Si le joueur n'a joué à aucun champion, on retourne une liste vide

    df=pd.DataFrame(columns=['Champion','Match played','Win','Lose','Winrate (%)']) # Création du DataFrame

    for champ in champ_stats[:n]:                           # Pour chaque champion
        id=champ['id']                                          # Récupération de l'id du champion
        champion=Champions.find_one({'_id':id})['name']         # Récupération du nom du champion
        if champion is None:                                    # Si le champion n'est pas dans la base de données
            break                                                   # On arrête la boucle
        play=champ['play']                                      # Récupération du nombre de matchs joués
        win=champ['win']                                        # Récupération du nombre de matchs gagnés
        lose=champ['lose']                                      # Récupération du nombre de matchs perdus
        winrate=round(win/(win+lose)*100,2)                     # Calcul du winrate en pourcentage

        df=df.append({'Champion':champion,'Match played':play,'Win':win,'Lose':lose,'Winrate (%)':winrate},ignore_index=True) # Ajout des informations dans le DataFrame

    df=df.sort_values(by=['Match played'],ascending=False)  # Tri du DataFrame par nombre de matchs joués

    # Création du tableau HTML
    return [ html.Div(html.H4("The most played Champions by the player:", style={'color': '#fd1eff','margin-right': '10px'})),
        dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)]

def get_player_info(game_name, tagline): # Récupération des informations du joueur sous forme de cartes HTML
    player_info = Joueurs.find_one({'game_name': game_name, 'tagline': tagline})                # Récupération des informations du joueur dans la base de données

    if not player_info:                                                                         # Si le joueur n'est pas dans la base de données
        return [html.Div(html.I("Player not found. Try for example: Caps#45555"))]                  # On retourne un message d'erreur

    summoner_id = player_info.get('_id')                                                        # Récupération de l'id du joueur
    ranked = Ranked.find_one({'player_id': summoner_id})['lp_histories']                        # Récupération des informations ranked du joueur
    champ_stats=MostChampPlayed.find_one({'player_id': summoner_id})['champ_stats']             # Récupération des informations des champions les plus joués par le joueur

    if ranked is not None :                                                                     # Si le joueur a des informations ranked
        ranked_layout = get_ranked_info(ranked)                                                     # On récupère les informations ranked sous forme de carte HTML
    else :
        ranked_layout = [html.Div(html.I("No ranked information available for this player"))]   # Sinon on retourne un message d'erreur

    if champ_stats is not None:                                                                 # Si le joueur a des informations sur les champions les plus joués
        champ_layout= get_champ_stats(champ_stats)                                                  # On récupère les informations sur les champions les plus joués sous forme de tableau HTML
    else:
        champ_layout=[html.Div(html.I("No champion information available for this player"))]    # Sinon on retourne un message d'erreur

    # Création de la carte HTML avec les informations du joueur
    player_layout = [
        html.Div([
            html.H4(f"Player: {player_info['game_name']} #{player_info['tagline']}", style={'color': '#1E90FF','margin-right': '10px'}),
            html.Img(src=player_info['profile_image_url'], style={'width': '50px', 'height': '50px', 'margin-bottom': '10px'}),
        ], style={'display': 'flex', 'align-items': 'flex-start', 'justify-content': 'flex-start', 'margin-bottom': '10px'}),
        dbc.Table.from_dataframe(pd.DataFrame({
            'Level': [player_info['level']],
            'Ladder Rank (%)': [round(player_info['ladder_rank'],2)],
            'Region': [player_info['region_id']],
        }), striped=True, bordered=True, hover=True),
    ]

    team_id = player_info.get('team_id')                            # Récupération de l'id de l'équipe du joueur
    if team_id:                                                     # Si le joueur a une équipe
        team_info = Teams.find_one({'_id': team_id}) or {}              # Récupération des informations de l'équipe
        # Création de la carte HTML avec les informations de l'équipe
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
        player_layout.extend(team_layout)                          # Ajout des informations de l'équipe à la carte HTML du joueur

    return player_layout + ranked_layout + champ_layout            # Retourne la carte HTML du joueur avec les informations ranked et les informations sur les champions les plus joués

def generate_histogram(selected_region): # Génération de l'histogramme des ladder ranks en fonction de la région sélectionnée dans le dropdown
    if selected_region is not None:                                         # Vérifier si une région a été sélectionnée
        players_in_region = Joueurs.find({'region_id': selected_region})        # Récupération des joueurs de la région sélectionnée
        df = pd.DataFrame(players_in_region)                                    # Création du DataFrame

        if not df.empty:                                                        # Vérifier si le DataFrame n'est pas vide
            region = Regions.find_one({'_id': selected_region});                # Récupération des informations de la région sélectionnée

            # Création de l'histogramme
            fig = px.histogram(df, x='ladder_rank', nbins=20, title=f'Ladder Rank Distribution of {region["name"]}',
                               labels={'ladder_rank': 'Ladder Rank'},
                               color_discrete_sequence=['#1EDEFF'], range_x=[0,100])

            # Apparence de l'histogramme
            fig.update_layout(
                title=dict(text=f'Ladder Rank Distribution of {region["name"]}', font=dict(size=16), x=0.5),
                xaxis=dict(title='Ladder Rank', showgrid=False),
                yaxis=dict(title='Frequency', showgrid=False),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'), bargap=0.1, bargroupgap=0.1, showlegend=False
            )

            # Apparence des barres de l'histogramme
            fig.update_traces(marker=dict(color='#1EDEFF'))

            # Apparence des axes de l'histogramme (couleur blanche et autorange)
            fig.update_xaxes(tickfont=dict(color='white'),autorange=True),
            fig.update_yaxes(tickfont=dict(color='white'),autorange=True),

            # Ajout d'une annotation pour expliquer l'histogramme
            fig.update_layout(
                annotations=[dict(
                    text='This histogram displays the distribution of ladder ranks. The lower the ladder rank, the better the players it represents.',
                    showarrow=False, xref='paper', yref='paper', x=0, y=1, align='left',
                    font=dict(size=10, color='white')
                )]
            )

            return fig, ''                                  # Retourne l'histogramme et une chaîne de caractères vide car il n'y a pas d'erreur
        else:
            return make_subplots(rows=1, cols=1), "No players found for this region in the website's database at the moment."       # Retourne un histogramme vide et un message d'erreur
    else:
        return make_subplots(rows=1, cols=1), 'Select a region.'                                                                    # Retourne un histogramme vide et un message d'erreur

def generate_esport_map(): # Génération de la carte choropleth des ladder ranks moyens en fonction des joueurs PRO par région
    query_players = {"team_id": {"$ne": None}}                                                  # Filtre pour récupérer les joueurs PRO
    projection_players = {"region_id": 1, "ladder_rank": 1, "nickname": 1, "_id": 0}            # Projection pour récupérer les informations nécessaires
    df_players = pd.DataFrame(list(db['Joueurs'].find(query_players, projection_players)))      # Création du DataFrame des joueurs PRO

    distinct_regions = Joueurs.distinct("region_id", {"team_id": {"$ne": None}})                                                # Récupération des régions des joueurs PRO
    df_regions = pd.DataFrame(list(Regions.find({"_id": {"$in": distinct_regions}}, {"_id": 1, "countries": 1, "name": 1})))    # Création du DataFrame des régions

    # Agrégation par région des valeurs de ladder_rank des joueurs PRO
    df_aggregated = df_players.groupby('region_id', as_index=False).agg({'ladder_rank': 'mean', 'nickname': lambda x: ', '.join(x)})

    # Fusionner df_aggregated avec df_regions pour obtenir les pays associés à chaque région (pour la carte choropleth)
    df_merged = pd.merge(df_aggregated, df_regions, left_on='region_id', right_on='_id', how='left')

    # Création des listes pour la carte choropleth
    c=[]
    v=[]
    t=[]
    n=[]
    for _,ligne in df_merged.iterrows():        # Pour chaque ligne du DataFrame
        if ligne['countries'] is not None:          # Si la ligne contient des pays
            for country in ligne['countries']:          # Pour chaque pays
                c.append(country)                           # Ajout du pays
                v.append(ligne['ladder_rank'])              # Ajout de la valeur de ladder_rank
                t.append(ligne['name'])                     # Ajout du nom de la région
                n.append(ligne['nickname'])                 # Ajout des nicknames des joueurs PRO

    df_map = pd.DataFrame({'country': c, 'value': v, 'region_name': t, 'nicknames': n})     # Création du DataFrame pour la carte choropleth
    df_map = df_map.dropna(subset=['value'])                                                # Suppression des lignes avec des valeurs nulles

    if df_map.empty:                            # Si le DataFrame est vide
        return make_subplots(rows=1, cols=1)        # Retourne une carte choropleth vide

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

    # Apparence de la carte choropleth
    fig.update_geos(
        projection_type="natural earth",
        showcoastlines=True, coastlinecolor="Black",
        showland=True, landcolor="lightgray",
        showocean=True, oceancolor="lightblue",
        showframe=False,
        showcountries=True,
        countrycolor="Black",
    )

    # Ajustement de la taille de la carte choropleth et centrage
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

    return fig # Retourne la carte choropleth


# **********************************************************************************************************************
server = flask.Flask(__name__) # Création du serveur Flask
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],suppress_callback_exceptions=True, server=server) # Création de l'application Dash

# **********************************************************************************************************************

# Création des pages du dashboard

# Page 1
first_page_content = html.Div(children=[
    html.H3(children='Project : OP.GG', style={'margin-bottom': '15px','textAlign': 'center'}),
    html.H6(children='Dashboard related to League of Legends players, leveraging web scraping from the OP.GG website. | By Keren COUTON & Matthieu CONSTANTIN', style={'margin-bottom': '40px','textAlign': 'center'}),

    html.Img(src=app.get_asset_url('logo.png'),style={'width': '80px', 'height': '100px', 'margin': 'auto', 'display': 'block', 'margin-bottom': '20px'}),

    dbc.Row(
        [
            dbc.Col([
                dbc.FormGroup([
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
    html.P("This histogram provides a visualization of the distribution of League of Legends players' ladder rank, based on the data available in the database associated with this web application. Each vertical bar indicates the number of players within a specific range of ladder rank. (It is crucial to note that the horizontal axis of this histogram is expressed in percentages. Therefore, a player positioned at x=10 is among the top 10% of League of Legends players in their region.)", style={'margin-bottom': '20px', 'textAlign': 'center'}),
    html.Br(),

    dcc.Graph(id='esport-map'),
    html.Br(),
    html.P("This choropleth map allows for the analysis of the average ladder rank of PRO players based on their region. On a global competition scale, Korean and Chinese teams prove to be the best, while European teams strive to compete with them. Thus, it is evident that PRO players from Korea and Europe are highly ranked in their ladder, with an average of 0.03%. However, one must consider the higher difficulty of the Korean ladder and the number of players present – 1,687,705 in the European ladder compared to 1,789,433 in the Korean ladder. Korean players are known to exhibit higher skill levels at the top of the ladder.", style={'margin-bottom': '20px', 'textAlign': 'center'}),
    html.Br(),
    html.P("According to the results in global competitions, it seems coherent to see North Americans ranked 3rd on the map with an average ladder rank of 0.22%, followed by South Americans with an average ladder rank of 0.60%, Oceania with an average ladder rank of 0.72%, and Japanese players with an average ladder rank of 1.20%. For comparison, in Europe, a ladder rank of 1.20% corresponds to a Diamond 2 rank.", style={'margin-bottom': '20px', 'textAlign': 'center'}),
    html.Br(),
    html.P("The results align with the World Championship, where regions such as Europe, South Korea, China, and North America qualify for the Swiss round, while other regions must go through what is known as the play-in to secure qualification.", style={'margin-bottom': '20px', 'textAlign': 'center'}),
    html.Br(),
    html.Div(id='hidden-trigger', style={'display': 'none'}),

    html.Footer(children=[
        html.Div([
            html.Img(src=app.get_asset_url('faker.gif'), style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px', 'margin-top': '20px'}),
        dcc.Link('Champions - A comprehensive roster of all champions', href='/dashboard/page2', style={'margin-bottom': '20px'}),
        html.Br(),
        dcc.Link('Players - Roster of all players in the Database', href='/dashboard/page3', style={'margin-bottom': '20px'}),
        html.P("© 2024 - All rights reserved. By Keren COUTON & Matthieu CONSTANTIN"),
    ])

])

# Page 2
second_page_content = html.Div([
    html.H3(children='Champions', style={'margin-bottom': '15px','textAlign': 'center'}),
    html.H6(children='A comprehensive roster of all champions | By Keren COUTON & Matthieu CONSTANTIN',style={'margin-bottom': '40px', 'textAlign': 'center'}),

    html.Div(get_all_champions(), style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'flex-start'}),

    html.Footer(children=[
        html.Div([
            html.Img(src=app.get_asset_url('faker.gif'), style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px', 'margin-top': '20px'}),
        dcc.Link('Back - Return to dashboard', href='/dashboard/page1', style={'margin-bottom': '20px'}),
        html.Br(),
        dcc.Link('Players - Roster of all players in the Database', href='/dashboard/page3', style={'margin-bottom': '20px'}),
        html.P("© 2024 - All rights reserved. By Keren COUTON & Matthieu CONSTANTIN"),
    ]),

])

# Page 3
troisieme_page_content = html.Div([
    html.H3(children='Players', style={'margin-bottom': '15px','textAlign': 'center'}),
    html.H6(children='Roster of all players in the Database| By Keren COUTON & Matthieu CONSTANTIN',style={'margin-bottom': '40px', 'textAlign': 'center'}),

    html.Div(get_all_players_info(), style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'flex-start'}),

    html.Footer(children=[
        html.Div([
            html.Img(src=app.get_asset_url('faker.gif'), style={'width': '120px', 'height': '68px'}),
            html.P('"My personality is that I usually just say what needs to be said."'),
        ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center','margin-bottom': '10px', 'margin-top': '20px'}),
        dcc.Link('Back - Return to dashboard', href='/dashboard/page1', style={'margin-bottom': '20px'}),
        html.Br(),
        dcc.Link('Champions - A comprehensive roster of all champions', href='/dashboard/page2', style={'margin-bottom': '20px'}),
        html.P("© 2024 - All rights reserved. By Keren COUTON & Matthieu CONSTANTIN"),
    ]),
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Button("Dashboard", id='btn-dashboard', href='/dashboard/page1', style={'margin-right': '10px'}),
    dbc.Button("Champions", id='btn-champions', href='/dashboard/page2', style={'margin-right': '10px'}),
    dbc.Button("Joueurs", id='btn-joueurs', href='/dashboard/page3', style={'margin-right': '10px'}),
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
    elif pathname=='/dashboard/page3':
        return troisieme_page_content
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
        if region is not None and value is not None:
            if '#' in value:
                gamename, tag = value.split('#')
            else:
                gamename, tag = value, None
            output_text=f'Region selected: {region} | Gamename: {gamename} | Tag: {tag}'
            #new_url = f"https://www.op.gg/summoners/{region}/{gamename.replace(' ', '-')}-{tag}"

            player_info_layout = get_player_info(gamename, tag)
            return output_text,player_info_layout
        else:
            return 'Please select a region.',None
    else: return None, None

# Callback pour mettre à jour l'histogramme en fonction de la région sélectionnée
@app.callback(
    [Output('ladder-rank-histogram', 'figure'),
     Output('output-message', 'children')],
    [Input('dropdown-region', 'value')]
)
def update_histogram(selected_region):
    return generate_histogram(selected_region)

# Callback pour cacher l'histogramme si la figure est vide
@app.callback(
    Output('ladder-rank-histogram', 'style'),
    [Input('ladder-rank-histogram', 'figure')]
)
def hide_histo(figure):
    # Masquer le graphique si la figure est vide
    if figure is None or not figure.get('data'):
        return {'display': 'none'}
    else:
        return {'display': 'block'}

# Callback pour créer et mettre à jour la carte choropleth
@app.callback(Output('esport-map', 'figure'), [Input('hidden-trigger', 'children')])
def update_esport_map(trigger):
    return generate_esport_map()

# Callback pour cacher la carte choropleth si la figure est vide
@app.callback(
    Output('esport-map', 'style'),
    [Input('esport-map', 'figure')]
)
def hide_esport_map(figure):
    # Masquer la carte esport si la figure est vide
    if figure is None or not figure.get('data'):
        return {'display': 'none'}
    else:
        return {'display': 'block'}

# **********************************************************************************************************************
if __name__ == '__main__':                                  # Lancement de l'application
    app.run_server(host='0.0.0.0', port=8050, debug=True)       # Lancement du serveur Flask

# **********************************************************************************************************************
