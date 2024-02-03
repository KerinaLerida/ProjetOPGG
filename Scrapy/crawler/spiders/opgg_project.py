# Importation des modules nécessaires
import scrapy
import json
import requests

# Importation de la fonction main issue du fichier data_fct.py
from .data_fct import main

class OpggSpider(scrapy.Spider): # Création de la classe OpggSpider qui hérite de la classe scrapy.Spider

    name = "opgg"                   # Nom du spider
    allowed_domains = ['op.gg']     # Domaines autorisés pour le spider

    # Liste des urls de départ à scraper
    start_urls = [
        "https://www.op.gg/summoners/euw/NPC Kerina-Coach",
        "https://www.op.gg/summoners/euw/NPC Honthagr-01530",
        "https://www.op.gg/summoners/euw/NPC FoxSilver-NPC",
        "https://www.op.gg/summoners/euw/NPC Reintack-EUW",
        "https://www.op.gg/summoners/euw/NPC bebe-NPC",
        "https://www.op.gg/summoners/euw/NPC Azaba-EUW",
        "https://www.op.gg/summoners/euw/NPC Kog Mawtivé-EUW",
        "https://www.op.gg/summoners/euw/NPC Yato-EUW",
        "https://www.op.gg/summoners/euw/Caps-45555",
        "https://www.op.gg/summoners/euw/GoldenRetriever-NPC",
        "https://www.op.gg/summoners/euw/Miky-Loser",
        "https://www.op.gg/summoners/euw/Razørk Activoo-razzz",
        "https://www.op.gg/summoners/euw/Season 3 Chall-EUW",
        "https://www.op.gg/summoners/euw/Targamas-5555",
        "https://www.op.gg/summoners/euw/Mazs-EUW",
        "https://www.op.gg/summoners/kr/Hide on bush-KR1",
        "https://www.op.gg/summoners/kr/우치하 홍창현-KR1",
        "https://www.op.gg/summoners/kr/Deft-8366",
        "https://www.op.gg/summoners/kr/BeryL-000",
        "https://www.op.gg/summoners/kr/아구몬-0509",
        "https://www.op.gg/summoners/kr/Keria-레나타",
        "https://www.op.gg/summoners/kr/T1 제우스-0102",
        "https://www.op.gg/summoners/kr/T1 Gumayusi-KR1",
        "https://www.op.gg/summoners/kr/Oner-KR222",
        "https://www.op.gg/summoners/kr/Lehends-KR1",
        "https://www.op.gg/summoners/kr/JUGKlNG-KR1",
        "https://www.op.gg/summoners/kr/허거덩-0303",
        "https://www.op.gg/summoners/kr/kiin-KR1",
        "https://www.op.gg/summoners/kr/Peyz-KR11",
        "https://www.op.gg/summoners/na/blaberfish2-NA1",
        "https://www.op.gg/summoners/na/Sneaky-NA69",
        "https://www.op.gg/summoners/na/goldenglue-NA1",
        "https://www.op.gg/summoners/na/Licorice-NA1",
        "https://www.op.gg/summoners/na/TL HONDA IMPACT-XDDD",
        "https://www.op.gg/summoners/oce/Dragku-Doner",
        "https://www.op.gg/summoners/oce/Only1-OCE",
        "https://www.op.gg/summoners/oce/Vxpir-Vxpir",
        "https://www.op.gg/summoners/oce/Djalal-OCE",
        "https://www.op.gg/summoners/oce/Carbon-2014",
        "https://www.op.gg/summoners/jp/yyyyyyyyyy-1234",
        "https://www.op.gg/summoners/jp/ytzz-2426",
        "https://www.op.gg/summoners/jp/Rainbrain-JP1",
        "https://www.op.gg/summoners/jp/nororin-2061",
        "https://www.op.gg/summoners/jp/Roki-JP1",
        "https://www.op.gg/summoners/br/Kami-BR1",
        "https://www.op.gg/summoners/br/XDXdxdxdxdxd-BR2",
        "https://www.op.gg/summoners/br/nano-BR1",
        "https://www.op.gg/summoners/br/ProDelta-BR1",
        "https://www.op.gg/summoners/br/nappera-BR1",
        "https://www.op.gg/summoners/br/micaO-1996",
        "https://www.op.gg/summoners/br/Klaus-BR1",
        "https://www.op.gg/summoners/br/Professor-heart",
        "https://www.op.gg/summoners/br/Grevthar-BR1",
        "https://www.op.gg/summoners/br/Ayel-0001",
        "https://www.op.gg/summoners/br/Aegis-BR1",
        "https://www.op.gg/summoners/br/AMANDINHA TI AMO-BR1"
    ]
    
    def system_request(self, url): # Fonction effectuant une requête avec un User-Agent (en-tête spécifique)

        # Pour éviter le blocage du site, création d'un User-Agent spécifique
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        # try/except pour gérer les erreurs de requête :

        try: # Si la requête est effectuée sans erreur, retourner la réponse de la requête
            response = requests.get(url, headers=headers)                       # Requête avec l'User-Agent spécifique
            response.raise_for_status()                                         # Vérification du code de statut de la réponse

            return scrapy.Request(url, headers=headers, callback=self.parse)    # Retourne la réponse de la requête pour le traitement par Scrapy (parse)
        except requests.RequestException as e: # Si une erreur est levée, afficher un message d'erreur
            self.log(f"An error occurred during system_request: {e}")           # Affichage du message d'erreur
            return None                                                         # Retourne None

    def start_requests(self): # Fonction qui lance les requêtes initiales
        for url in self.start_urls:             # Pour chaque url de départ
            request = self.system_request(url)  # Effectuer une requête avec un User-Agent spécifique
            if request:                             # Si la requête est effectuée sans erreur
                yield request                       # Retourner la requête pour le traitement par Scrapy (parse)

    def parse(self, response): # Fonction qui parse les données pour les envoyer à la fonction main du fichier data_fct.py

        data_content = response.css('#__NEXT_DATA__::text').get()   # Récupération du contenu de la balise #__NEXT_DATA__ (contient les données au format JSON)
        self.log(f"parsing {response.url})")                        # Affichage de l'url parsée

        if data_content:   # Si le contenu de la balise #__NEXT_DATA__ n'est pas vide

            # try/except pour gérer les erreurs de parsing JSON :
            try: # Si le contenu de la balise #__NEXT_DATA__ est parsé sans erreur
                json_data = json.loads(data_content)        # Conversion du contenu de la balise #__NEXT_DATA__ au format JSON
                main(json_data)                             # Passer json_data à la fonction main dans data_fct.py pour le traitement des données et l'insertion de celles-ci dans notre base de données MongoDB
            except json.JSONDecodeError as e: # Si une erreur est levée, afficher un message d'erreur
                self.log(f"Failed to decode JSON: {e}")     # Affichage du message d'erreur




