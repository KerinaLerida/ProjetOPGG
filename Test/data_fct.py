import json
from pymongo import MongoClient,errors
import pymongo

def regions_management(Regions):
    if Regions.count_documents({}) == 0:
        with open('regions.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            Regions.bulk_write([pymongo.InsertOne(doc) for doc in data])

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
        Regions=db["Regions"]

        regions_management(Regions)

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
    return Joueurs.find_one({"_id": summoner_id}) is not None

def add_new_doc(collection, data_up, id_search):
    for doc in data_up:
        query = {id_search: doc[id_search]}
        update = {"$set": doc}
        result = collection.update_one(query, update, upsert=True)

        if result.matched_count > 0:
            print(f"Le document pour {id_search} {doc[id_search]} a été mis à jour dans la collection {collection.name}.")
        elif result.upserted_id is not None:
            print(f"Le document pour {id_search} {doc[id_search]} a été ajouté dans la collection {collection.name}.")

def maj_champions(collection,data_up,id_search):
    if collection.count_documents({}) != len(data_up):
        add_new_doc(collection, data_up,id_search)
        print(f"Les champions dans la collection {collection.name} a été mis à jour.")

def maj_data(collection, data_up, id_search): # optimiser
    if collection.name == "Champions" :
        return

    for key, value in data_up.items():
        existing_document = collection.find_one({id_search: value})

        if existing_document:
            for key, value in data_up.items():
                if key not in existing_document or existing_document.get(key) != value:
                    existing_document[key] = value

            collection.update_one({id_search: value}, {"$set": existing_document})
            print(f"Les informations pour {id_search} dans la collection {collection.name} ont été mises à jour.")
            return

    collection.insert_one(data_up)
    print(f"Le document pour {id_search} a été ajouté à la collection {collection.name}.")

def rename_first_key(dictionary):
    if dictionary:
        old_key = next(iter(dictionary))
        dictionary["_id"] = dictionary.pop(old_key)
    return dictionary

def nettoie_donnees(selected_data, collects):
    info_joueur=selected_data.get("data", {})

    # ************** Nettoyage des Données **************
    region_id=selected_data.get("region")
    summoner_id = info_joueur.get("summoner_id")
    rank = info_joueur["ladder_rank"].get("rank")
    total = info_joueur["ladder_rank"].get("total")

    if rank is not None and total is not None:
        pourcentage_rank_total = (rank / total) * 100
    else:
        pourcentage_rank_total = None

    if info_joueur.get("team_info") is not None:
        info_team=info_joueur["team_info"]
        team_id = info_team.get("team_id")
        authority=info_team.get("authority")
        nickname=info_team.get("nickname")
        data_team =info_team.get("team")
        rename_first_key(data_team)
    else:
        team_id = None
        data_team=None
        authority=None
        nickname=None

    data_joueur = {
        "_id": summoner_id,
        "game_name": info_joueur.get("game_name"),
        "tagline": info_joueur.get("tagline"),
        "level": info_joueur.get("level"),
        "ladder_rank": pourcentage_rank_total,
        "profile_image_url": info_joueur.get("profile_image_url"),
        "team_id": team_id,
        "authority":authority,
        "nickname":nickname,
        "region_id":region_id
    }

    data_ranked_activities = {
        "player_id": summoner_id,
        "lp_histories": info_joueur.get("lp_histories", [])
    }

    champ_played_most = info_joueur.get("most_champions", {})
    if champ_played_most is not None:
        data_champ_played_most = {
            "player_id": summoner_id,
            "champ_stats": champ_played_most.get("champion_stats")
        }
    else:
        data_champ_played_most = None

    data_champions = info_joueur.get("champions")
    if data_champions is not None:
        for data_champ in data_champions:
            rename_first_key(data_champ)
        maj_champions(collects[-1], data_champions, "_id")

    data_all = [data_joueur, data_team, data_ranked_activities, data_champ_played_most, data_champions]
    ids = ["_id", "_id", "player_id", "player_id", "_id"]

    if summoner_id_exist(summoner_id,collects):
        print(f"Le summoner_id {summoner_id} existe déjà dans la base de données.")
        for collection, data, id_search in zip(collects,data_all,ids):
            if data is not None:
                maj_data(collection, data, id_search)
        return None

    return data_all

def interactions_mongodb(data_all, collects):
    for collection, data in zip(collects, data_all):
        if data is not None:
            if collection.name == "Champions":
                collection.bulk_write([pymongo.InsertOne(doc) for doc in data])
            else:
                print(f"{collection}")
                collection.insert_one(data)

def main():
    client, collects=connect_to_mongodb()
    with open('output.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        selected_data=data.get("props", {}).get("pageProps", {})

        # Nettoyage des données
        result = nettoie_donnees(selected_data, collects)

        if result is not None:
            interactions_mongodb(result, collects)

    disconnect_from_mongodb(client)

if __name__ == "__main__":
    main()
