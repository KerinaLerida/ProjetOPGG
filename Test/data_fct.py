import json
from pymongo import MongoClient,errors
import pymongo
import logging

"""# Connexion à la base de données MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['TestScraping']

# Initialisation des collections
Joueurs = db["Joueurs"]
Champions = db["Champions"]
Ranked = db["Ranked"]
MostChampPlayed = db['MostChampPlayed']
Teams = db["Teams"]"""

def connect_to_mongodb():
    try:
        # Connexion à la base de données MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['TestScraping']

        # Initialisation des collections
        Joueurs = db["Joueurs"]
        Champions = db["Champions"]
        Ranked = db["Ranked"]
        MostChampPlayed = db['MostChampPlayed']
        Teams = db["Teams"]

        return client, [Joueurs, Teams, Ranked, MostChampPlayed, Champions]
    except errors.ConnectionFailure as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        raise

def disconnect_from_mongodb(client):
    try:
        # Fermeture de la connexion MongoDB
        if client:
            client.close()
    except Exception as e:
        print(f"Erreur lors de la fermeture de la connexion MongoDB : {e}")

def summoner_id_exist(summoner_id,collects):
    Joueurs=collects[0]
    return Joueurs.find_one({"summoner_id": summoner_id}) is not None

def add_new_doc(collection,data_up,id_search):
    existant_ids = [document[id_search] for document in collection.find()]
    new_docs = [item for item in data_up if item[id_search] not in existant_ids]

    if new_docs:
        collection.insert_many(new_docs)
def maj_champions(collection,data_up,id_search):
    if collection.count_documents({}) != len(data_up):
        add_new_doc(collection, data_up,id_search)
        print(f"Les champions dans la collection {collection.name} a été mis à jour.")
def maj_data(collection, data_up, id_search): # optimiser
    if collection.name == "Champions" :
        maj_champions(collection, data_up,id_search)
        return

    #print(f"{id_search}, {collection.name}")

    for key, value in data_up.items():
        existing_document = collection.find_one({id_search: value})

        if existing_document:
            for key, value in data_up.items():
                if existing_document.get(key) != value:
                    existing_document[key] = value

            collection.update_one({id_search: value}, {"$set": existing_document})
            print(
                f"Les informations pour {id_search} {value} dans la collection {collection.name} ont été mises à jour.")
            return

    collection.insert_one(data_up)
    print(f"Le document pour {id_search} {data_up[id_search]} a été ajouté à la collection {collection.name}.")

def nettoie_donnees(info_joueur, collects):
    # ************** Nettoyage des Données **************
    summoner_id = info_joueur.get("summoner_id")
    rank = info_joueur["ladder_rank"].get("rank")
    total = info_joueur["ladder_rank"].get("total")

    if rank is not None and total is not None:
        pourcentage_rank_total = (rank / total) * 100
    else:
        pourcentage_rank_total = None

    if info_joueur.get("team_info") is not None:
        team_id = info_joueur["team_info"].get("team_id")
        authority=info_joueur["team_info"].get("authority")
        data_team = info_joueur["team_info"].get("team")
    else:
        team_id = None
        data_team=None

    data_joueur = {
        "summoner_id": summoner_id,
        "game_name": info_joueur.get("game_name"),
        "tagline": info_joueur.get("tagline"),
        "level": info_joueur.get("level"),
        "ladder_rank": pourcentage_rank_total,
        "profile_image_url": info_joueur.get("profile_image_url"),
        "team_id": team_id,
        "authority":authority
    }

    data_ranked_activities = {
        "summoner_id": summoner_id,
        "lp_histories": info_joueur.get("lp_histories", [])
    }

    champ_played_most = info_joueur.get("most_champions", {})
    if champ_played_most is not None:
        data_champ_played_most = {
            "summoner_id": summoner_id,
            "champ_stats": champ_played_most.get("champion_stats")
        }
    else:
        data_champ_played_most = None

    data_champions = info_joueur.get("champions")

    #collects=[Joueurs, Teams, Ranked, MostChampPlayed, Champions]
    data_all = [data_joueur, data_team, data_ranked_activities, data_champ_played_most, data_champions]
    ids=["summoner_id", "team_id", "summoner_id", "summoner_id","id"]

    if summoner_id_exist(summoner_id,collects):
        print(f"Le summoner_id {summoner_id} existe déjà dans la base de données.")
        for collection, data, id_search in zip(collects,data_all,ids):
            maj_data(collection, data, id_search)
        return None

    #return data_joueur,data_team, data_ranked_activities, data_champ_played_most, data_champions
    return data_all

"""def interactions_mongodb(data_joueur, data_team, data_ranked_activities, data_champ_played_most, data_champions): # à comprendre
    Joueurs.insert_one(data_joueur)
    Ranked.insert_one(data_ranked_activities)

    if data_champ_played_most is not None:
        MostChampPlayed.insert_one(data_champ_played_most)

    Champions.insert_many(data_champions)

    if data_joueur.get("team_id") is not None:
        Teams.insert_one(data_team)"""
def interactions_mongodb(data_all, collects):
    for collection, data in zip(collects, data_all):
        if data is not None:
            if collection.name == "Champions":
                collection.bulk_write([pymongo.InsertOne(doc) for doc in data])
            else:
                collection.insert_one(data)

def main():
    #collects = db.list_collection_names()
    client, collects=connect_to_mongodb()
    with open('output.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        info_joueur = data.get("props", {}).get("pageProps", {}).get("data", {})

        # Nettoyage des données
        result = nettoie_donnees(info_joueur,collects)

        if result is not None:
            #data_joueur,data_team, data_ranked_activities, data_champ_played_most, data_champions=result

            # Intéractions avec la BDD MongoDB
            #interactions_mongodb(data_joueur, data_team, data_ranked_activities, data_champ_played_most, data_champions)
            interactions_mongodb(result, collects)

    disconnect_from_mongodb(client)

if __name__ == "__main__":
    main()
