# Importation des modules nécessaires
from pymongo import MongoClient,errors
import pymongo

# **************** Données ****************
# Liste des régions et leurs pays associés
data_regions=[
    {
        "_id": "na",
        "name": "North America",
        "countries": ["Canada", "United States of America"]
    },
    {
        "_id": "euw",
        "name": "Europe West",
        "countries": ["France", "United Kingdom of Great Britain and Northern Ireland", "Ireland", "Spain", "Portugal", "Monaco", "Andorra", "Belgium", "Luxembourg", "Netherlands", "Switzerland", "Italy", "Saint Martin", "Vatican", "Malta", "Austria", "Germany"]
    },
    {
        "_id": "eune",
        "name": "Europe Nordic & East",
        "countries": ["Norway", "Sweden", "Finland", "Estonia", "Latvia", "Lithuania", "Belarus", "Ukraine", "Crimea", "Moldova", "Romania", "Bulgaria", "Greece", "Albania", "Macedonia", "Kosovo", "Montenegro", "Serbia", "Bosnia and Herzegovina", "Croatia", "Hungary", "Slovakia", "Slovenia", "Czech Republic", "Poland"]
    },
    {
        "_id": "oce",
        "name": "Oceania",
        "countries": ["Australia", "New Zealand"]
    },
    {
        "_id": "kr",
        "name": "Korea",
        "countries": ["Korea"]
    },
    {
        "_id": "jp",
        "name": "Japan",
        "countries": ["Japan"]
    },
    {
        "_id": "br",
        "name": "Brazil",
        "countries": ["Brazil"]
    },
    {
        "_id": "las",
        "name": "Latin America South",
        "countries": ["Bolivia", "Paraguay", "Argentina", "Uruguay", "Chile"]
    },
    {
        "_id": "lan",
        "name": "Latin America North",
        "countries": ["Venezuela", "Colombia", "Ecuador", "Peru"]
    },
    {
        "_id": "ru",
        "name": "Russia",
        "countries": ["Russia"]
    },
    {
        "_id": "tr",
        "name": "Türkiye",
        "countries": ["Türkiye"]
    },
    {
        "_id": "sg",
        "name": "Singapore",
        "countries": ["Singapore"]
    },
    {
        "_id": "ph",
        "name": "Philippines",
        "countries": ["Philippines"]
    },
    {
        "_id": "tw",
        "name": "Taiwan",
        "countries": ["Taiwan"]
    },
    {
        "_id": "vn",
        "name": "Vietnam",
        "countries": ["Vietnam"]
    },
    {
        "_id": "th",
        "name": "Thailand",
        "countries": ["Thailand"]
    }
]
# *****************************************

def regions_management(Regions): # Fonction pour gérer les régions dans la base de données MongoDB
    if Regions.count_documents({}) == 0:                                        # Vérifie si la collection Regions est vide, si oui, on l'initialise
        Regions.bulk_write([pymongo.InsertOne(doc) for doc in data_regions])    # Insertion des données de la liste data_regions dans la collection Regions

def connect_to_mongodb(): # Fonction pour se connecter à la base de données MongoDB

    # try/except pour gérer les erreurs de connexion à MongoDB :

    try: # Si la connexion à MongoDB est effectuée sans erreur

        # Connexion à la base de données MongoDB
        client = MongoClient('mongodb://mongodb-opgg-conteneur:27017/')     # Connexion au conteneur MongoDB
        db = client['TestScraping']                                         # Connexion à la base de données TestScraping

        # Initialisation des collections
        Joueurs = db["Joueurs"]                     # Collection Joueurs
        Champions = db["Champions"]                 # Collection Champions
        Ranked = db["Ranked"]                       # Collection Ranked
        MostChampPlayed = db['MostChampPlayed']     # Collection MostChampPlayed
        Teams = db["Teams"]                         # Collection Teams
        Regions=db["Regions"]                       # Collection Regions

        regions_management(Regions) # Gestion des régions dans la base de données MongoDB

        return client, [Joueurs, Teams, Ranked, MostChampPlayed, Champions] # Retourne le client MongoDB et les collections MongoDB
    except errors.ConnectionFailure as e: # Si une erreur est levée, afficher un message d'erreur
        print(f"Erreur de connexion à MongoDB : {e}")       # Affichage du message d'erreur
        raise                                               # Lève l'erreur

def disconnect_from_mongodb(client): # Fonction pour se déconnecter de la base de données MongoDB

    # try/except pour gérer les erreurs de déconnexion de MongoDB :

    try: # Si la déconnexion de MongoDB est effectuée sans erreur

        if client:              # Si la connexion MongoDB est ouverte
            client.close()      # Fermeture de la connexion MongoDB
    except Exception as e: # Si une erreur est levée, afficher un message d'erreur
        print(f"Erreur lors de la fermeture de la connexion MongoDB : {e}")     # Affichage du message d'erreur

def summoner_id_exist(summoner_id,collects): # Fonction pour vérifier si un summoner_id existe déjà dans la collection Joueurs dans la base de données MongoDB
    Joueurs=collects[0]                                         # Collection Joueurs
    return Joueurs.find_one({"_id": summoner_id}) is not None   # Retourne True si le summoner_id existe déjà dans la collection Joueurs, False sinon

def maj_champions(collection, data_up, id_search): # Fonction pour mettre à jour la collection Champions dans la base de données MongoDB

    current_champion_ids = set(collection.distinct(id_search))                              # Récupère les ids des champions déjà présents dans la collection
    new_champions = [doc for doc in data_up if doc[id_search] not in current_champion_ids]  # Récupère les nouveaux champions qui ne sont pas encore dans la collection

    if new_champions:                                                                                                                   # Si il y a des nouveaux champions à mettre à jour dans la collection
        bulk_operations = [pymongo.UpdateOne({"_id": doc[id_search]}, {"$set": doc}, upsert=True) for doc in new_champions]         # Création des opérations de mise à jour
        collection.bulk_write(bulk_operations)                                                                                                  # Mise à jour de la collection

        print(f"Les champions dans la collection {collection.name} ont été mis à jour.")                                                        # Affichage d'un message de confirmation
    else:                                                                                                                               # Si il n'y a pas de nouveaux champions à mettre à jour dans la collection
        print(f"Aucun nouveau champion à mettre à jour dans la collection {collection.name}.")                                                  # Affichage d'un message de confirmation

def maj_data(collection, data_up, id_search): # Fonction pour mettre à jour les données de la collection donnée dans la base de données MongoDB

    existing_document = collection.find_one({id_search: data_up[id_search]}) # Récupère le document existant dans la collection (si il existe) lié à l'id de recherche

    if existing_document:                                                                       # Si le document existe déjà dans la collection

        for key, value in data_up.items():                                                              # Pour chaque clé et valeur du document à mettre à jour
            if key not in existing_document or existing_document[key] != value:                             # Si la clé n'existe pas dans le document ou si la valeur est différente de celle du document
                existing_document[key] = value                                                                      # Mettre à jour la valeur de la clé dans le document

        collection.update_one({id_search: data_up[id_search]}, {"$set": existing_document})                         # Mise à jour du document dans la collection
        print(f"Les informations pour {id_search} dans la collection {collection.name} ont été mises à jour.")      # Affichage d'un message de confirmation
    else:                                                                                       # Si le document n'existe pas dans la collection
        collection.insert_one(data_up)                                                                  # Insertion du document dans la collection
        print(f"Le document pour {id_search} a été ajouté à la collection {collection.name}.")          # Affichage d'un message de confirmation

def rename_first_key_list(dictionary_list): # Fonction pour renommer la première clé d'une liste de dictionnaires
    for dictionary in dictionary_list:                      # Pour chaque dictionnaire de la liste
        if dictionary:                                              # Si le dictionnaire n'est pas vide
            old_key = next(iter(dictionary))                                # Récupère la première clé du dictionnaire
            dictionary["_id"] = dictionary.pop(old_key)                     # Renomme la première clé du dictionnaire en "_id"
    return dictionary_list                                  # Retourne la liste de dictionnaires

def nettoie_donnees(selected_data, collects): # Fonction pour nettoyer les données récupérées sur le site op.gg
    info_joueur=selected_data.get("data", {})               # Récupération des données du joueur

    region_id=selected_data.get("region")                   # Récupération de la région du joueur
    summoner_id = info_joueur.get("summoner_id")            # Récupération du summoner_id du joueur

    if(info_joueur.get("ladder_rank") is not None):         # Si le joueur est classé
        rank = info_joueur["ladder_rank"].get("rank")           # Récupération du rang du joueur
        total = info_joueur["ladder_rank"].get("total")         # Récupération du nombre total de joueurs classés
        pourcentage_rank_total = (rank / total) * 100           # Calcul du pourcentage du rang du joueur par rapport au nombre total de joueurs classés
    else:
        pourcentage_rank_total = "Unranked"                 # Si le joueur n'est pas classé, on met "Unranked" dans la variable pourcentage_rank_total

    if info_joueur.get("team_info") is not None:            # Si le joueur a une équipe, c'est un joueur pro
        info_team=info_joueur["team_info"]                       # Récupération des informations de l'équipe
        team_id = info_team.get("team_id")                       # Récupération de l'id de l'équipe
        authority=info_team.get("authority")                     # Récupération du statut du joueur
        nickname=info_team.get("nickname")                       # Récupération du vrai nom du joueur
        data_team =info_team.get("team")                         # Récupération du nom de l'équipe
        rename_first_key_list([data_team])                       # Renommage de la première clé du dictionnaire data_team en "_id" (pour avoir une clé primaire unique)
    else:                                                   # Si le joueur n'a pas d'équipe, toutes les variables sont mises à None
        team_id = None
        data_team=None
        authority=None
        nickname=None

    data_joueur = {                                                 # Création du dictionnaire des données du joueur
        "_id": summoner_id,                                             # Clé primaire du joueur
        "game_name": info_joueur.get("game_name"),                      # Nom du joueur
        "tagline": info_joueur.get("tagline"),                          # Tagline du joueur
        "level": info_joueur.get("level"),                              # Niveau du joueur
        "ladder_rank": pourcentage_rank_total,                          # Rang du joueur
        "profile_image_url": info_joueur.get("profile_image_url"),      # Url de l'image de profil du joueur
        "team_id": team_id,                                             # Id de l'équipe du joueur
        "authority":authority,                                          # Statut du joueur
        "nickname":nickname,                                            # Vrai nom du joueur
        "region_id":region_id                                           # Id de la région du joueur
    }

    data_ranked_activities = {                                  # Création du dictionnaire des données des activités classées du joueur
        "player_id": summoner_id,                                   # Clé primaire du joueur
        "lp_histories": info_joueur.get("lp_histories", [])         # Historique des points de ligue du joueur
    }

    champ_played_most = info_joueur.get("most_champions", {})  # Récupération des données du champion le plus joué par le joueur
    if champ_played_most is not None:                               # Si le joueur a un champion le plus joué
        data_champ_played_most = {                                      # Création du dictionnaire des données du champion le plus joué par le joueur
            "player_id": summoner_id,                                       # Clé primaire du joueur
            "champ_stats": champ_played_most.get("champion_stats")          # Statistiques du champion le plus joué par le joueur
        }
    else: # Si le joueur n'a pas de champion le plus joué
        data_champ_played_most = None

    data_champions = info_joueur.get("champions")                   # Récupération des données des champions du jeu
    if data_champions is not None:                                      # Si data_champions n'est pas vide
        data_champions = rename_first_key_list(data_champions)          # Renommage de la première clé du dictionnaire data_champions en "_id" (pour avoir une clé primaire unique)
        maj_champions(collects[-1], data_champions, "_id")      # Mise à jour de la collection Champions dans la base de données MongoDB

    data_all = [data_joueur, data_team, data_ranked_activities, data_champ_played_most, None]   # Création de la liste des données
    ids = ["_id", "_id", "player_id", "player_id", "_id"]                                       # Création de la liste des colonnes des données pour la mise à jour des données dans la base de données MongoDB

    if summoner_id_exist(summoner_id,collects):                                 # Si le summoner_id existe déjà dans la collection Joueurs
        name=info_joueur.get("game_name")                                           # Récupération du nom du joueur
        print(f"Le summoner_id {name} existe déjà dans la base de données.")
        for collection, data, id_search in zip(collects,data_all,ids):              # Pour chaque collection, données et colonne des données
            if data is not None:                                                        # Si les données ne sont pas vides
                maj_data(collection, data, id_search)                                       # Mise à jour des données dans la collection
        return None                                                                 # Retourne None

    return data_all                                                            # Retourne la liste des données

def interactions_mongodb(data_all, collects): # Fonction pour interagir avec la base de données MongoDB
    for collection, data in zip(collects, data_all):            # Pour chaque collection et données
        if data is not None and collection.name!="Champions":           # Si les données ne sont pas vides et que la collection n'est pas la collection Champions
            print(f"{collection}")                                          # Affichage de la collection
            collection.insert_one(data)                                     # Insertion des données dans la collection

def main(json_data): # Fonction principale qui gère les données et les envoie à la base de données MongoDB

    client, collects=connect_to_mongodb()                           # Connexion à la base de données MongoDB

    selected_data=json_data.get("props", {}).get("pageProps", {})   # Récupération des données de la page
    result = nettoie_donnees(selected_data, collects)               # Nettoyage des données

    if result is not None:                                          # Si les données sont nettoyées correctement et que le summoner_id n'existe pas déjà dans la base de données
        interactions_mongodb(result, collects)                              # Envoi des données à la base de données MongoDB

    disconnect_from_mongodb(client)                                 # Déconnexion de la base de données MongoDB


