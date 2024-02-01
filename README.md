# Projet OP.GG

## Description

Notre projet vise à réaliser un scraping web sur le site https://www.op.gg/. Afin de récupérer les données de différents joueurs de League of Legends, professionnels ou non, nous avons ainsi utilisé le framework Scrapy. Les données ont été ensuite stockées dans une base de données MongoDB. Puis, nous avons réalisé une application web permettant de visualiser les données récupérées, pour les analyser par la suite.

## Structure du Projet

Le projet est organisé en trois dossiers principaux, ayant chacun son DockerFile correspondant au service qu'il peut délivrer, déployés dans des conteneurs Docker distincts :

- **MongoDB** : Contient les fichiers nécessaires pour construire l'image Docker de MongoDB, notre base de données.
- **Scrapy** : Contient les fichiers nécessaires pour construire l'image Docker de Scrapy, notre service de scraping.
- **Application** : Contient les fichiers nécessaires pour construire l'image Docker de l'application, notre application web.

## Prérequis

- Docker installé sur votre machine ([Installer Docker](https://docs.docker.com/get-docker/))

## Configuration

Chaque dossier (MongoDB, Scrapy, Application) contient un fichier Dockerfile pour construire l'image respective. Et à la racine du projet, un fichier docker-compose.yml est présent pour déployer les conteneurs Docker pour nos 3 services MongoDB, Scrapy et Application.

## Utilisation

1. Clonez le dépôt sur votre machine locale :

   ```bash
   git https://github.com/KerinaLerida/ProjetOPGG.git
   cd ProjetOPGG
    ```
   
2. Lancez le projet avec la commande suivante :

   ```bash
   docker-compose up --build
   ```
3. Ouvrez votre navigateur et accédez à l'adresse suivante donnant sur l'application : http://localhost:8050

## Auteurs

- **Keren COUTON** - [KerinaLerida](https://github.com/KerinaLerida)
- **Matthieu CONSTANTIN** - [FoxSilverR](https://github.com/FoxSilverR)

## Améliorations possibles

- Scraping dynamique : récupérer les données en temps réel. [Implémentation d'une API]
- Ajouter des fonctionnalités à l'application web.

## Notes supplémentaires

- Le scraping est réalisé sur le site https://www.op.gg/ et les données récupérées sont stockées dans une base de données MongoDB.
- Assurez-vous que les ports nécessaires ne sont pas utilisés par d'autres services sur votre machine.
- Pour arrêter le projet, utilisez la combinaison de touches Ctrl+C dans le terminal où docker-compose est en cours d'exécution.
- Si vous souhaitez ajouter des joueurs à la base de données, vous pouvez modifier la variable **start_urls** de la **classe OpggSpider** dans le dossier Scrapy, puis dans le dossier crawler, puis dans le dossier spiders et puis dans le fichier **opgg_project.py**. Il suffit d'ajouter l'url des joueurs (exemple : https://www.op.gg/summoners/euw/NPC%20Kerina-Coach) (Syntaxe : https://www.op.gg/summoners/id_region/Riot_id-tag) à la suite de la liste, en les mettant entre guillemets.

## Structure du projet approndie

**ProjetOPGG :**
- Dossier : **MongoDB**
  - Fichier : Dockerfile
    - Contient les instructions pour construire l'image Docker de MongoDB.
  - Fichier : init-mongo.js
    - Contient les instructions pour créer la base de données et les collections.
  - Dossier : data
    - Contient les données récupérées par le scraping.
-
- Dossier : **Scrapy**
  - Fichier : Dockerfile
    - Contient les instructions pour construire l'image Docker de Scrapy.
  - Fichier : requirements.txt
    - Contient les dépendances nécessaires pour Scrapy.
  - Fichier : scrapy.cfg
    - Contient les paramètres de Scrapy.
  - Fichier : __init __.py
  -
  - Dossier : **crawler**
    - Fichier : __init __.py
    - Fichier : items.py
    - Fichier : middlewares.py
    - Fichier : pipelines.py
    - Fichier : settings.py
      - Contient les paramètres de Scrapy.
    - Dossier : spiders
      - Fichier : opgg_project.py
        - Contient les instructions pour réaliser le scraping.
      - Fichier : data_fct.py
        - Contient les fonctions pour récupérer les données.
      - Fichier : __init __.py
-
- Dossier : **Application**
  - Fichier : Dockerfile
    - Contient les instructions pour construire l'image Docker de l'application.
  - Fichier : requirements.txt
    - Contient les dépendances nécessaires pour l'application.
  - Fichier : dashboard.py
    - Contient les instructions pour réaliser l'application.
  -
  - Dossier : assets
    - Fichier : faker.gif
    - Fichier : logo.png
- 
- Fichier : **docker-compose.yml**
  - Contient les instructions pour déployer les conteneurs Docker pour nos 3 services MongoDB, Scrapy et Application.
- Fichier : README.md
  - Contient les informations sur le projet.
