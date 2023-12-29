import json
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['TestScraping']

Joueurs=db["Joueurs"]
Champions=db["Champions"]
Ranked=db["Ranked"]
MostChampPlayed=db['MostChampPlayed']
Teams=db["Teams"]

with open('./Test/output.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)
    #print(data.keys())

info_joueur=data.get("props", {}).get("pageProps", {}).get("data",{})

# ************** Nettoyage des Données **************
summoner_id=info_joueur.get("summoner_id")
rank = info_joueur["ladder_rank"].get("rank")
total = info_joueur["ladder_rank"].get("total")

if rank is not None and total is not None:
    pourcentage_rank_total = (rank / total) * 100
else: pourcentage_rank_total=None

if info_joueur.get("team_info") is not None:
    team_id=info_joueur["team_info"].get("team_id")
    data_team=info_joueur.get("team_info")
else: team_id=None

data_joueur = {
    "summoner_id": summoner_id,
    "game_name": info_joueur.get("game_name"),
    "tagline": info_joueur.get("tagline"),
    "level": info_joueur.get("level"),
    "ladder_rank": pourcentage_rank_total,
    "profile_image_url": info_joueur.get("profile_image_url"),
    "team_id":team_id
}

data_ranked_activities={
    "summoner_id": summoner_id,
    "lp_histories":info_joueur.get("lp_histories",[])
}

champ_played_most=info_joueur.get("most_champions",{})
if champ_played_most is not None:
    data_champ_played_most={
        "summoner_id": summoner_id,
        "champ_stats": champ_played_most.get("champion_stats")
    }
else: data_champ_played_most=None

data_champions=info_joueur.get("champions")
# ****************************************************

# TESTS :

print(info_joueur.get("game_name"),info_joueur.get("tagline"),info_joueur.get("level"))
#profile_image_url
#level
#updated_at # JOUEURS
#print(info_joueur.get("summoner_id"))

lp=info_joueur.get("lp_histories",[])
#print(lp[0])
#print(lp) # LP HISTORY

lp_stats=info_joueur.get("league_stats",[])
print(lp_stats[0].get("queue_info")) # SOLORANKED nom
#print(lp_stats)

champ_played_most=info_joueur.get("most_champions",{})
print(champ_played_most.keys())
print(champ_played_most.get("season_id"))
#print(champ_played_most.get("champion_stats")[0]) # les champions les plus joués par le joueur
print(info_joueur.get("ladder_rank")) #JOUEURS

#print(info_joueur.get("champions")[0]) # LISTE DES CHAMPIONS

#games=data.get("props", {}).get("pageProps", {}).get("games",{}).get("data",[])
#print(games[0].get("participants",[])[1])


