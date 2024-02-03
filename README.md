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

## Choix techniques

1. Web Scraping : Scrapy

Nous avons choisis puisque Scrapy est un framework Python open-source conçu pour extraire des données de sites web, qui offre une structure organisée pour la création de spiders et fournit des fonctionnalités puissantes pour le scraping. Utiliser Scrapy nous a paru logique puisque l'on devait extraire des données à partir de plusieurs pages web issues d'un même site web et que Scraping gère le scraping de manière efficace.

3. Base de données : MongoDB

Nous avons choisis MongoDB car c'est une base de données NoSQL orientée document, ce qui signifie qu'elle stocke les données sous forme de documents JSON. Et dans notre cas de scraping, le site web avait un sélecteur CSS, qui pointait sur un format JSON, ainsi l'utilisation de MongoDB fut évident par rapport à un base de données SQL. Puisqu'utiliser MongoDB revenait à simplifier le stockage et la manipulation des données extraites, car elles sont déjà dans un format similaire (JSON).

De plus, la flexibilité de MongoDB est particulièrement utile lorsqu'on travaille avec des données semi-structurées, comme c'est souvent le cas dans le scraping web et dans notre cas par exemple.

4. Application : Dash & Serveur Flask

Au niveau de la création de notre application WEB, nous avons choisis Dash, qui est un framework Python conçu pour la création d'applications web interactives basées sur Plotly et qui permet de construire des tableaux de bord interactifs avec des composants réactifs en Python.

Et nous avons aussi Dash avec un serveur Flask enfin de nous offrir une manière efficace de construire un tableau de bord interactif pour visualiser les données extraites. Dans notre cas, Flask sert de backend web pour Dash, et l'intégration entre les deux est relativement simple.

5. Conclusion

Nos choix ont été fait ainsi d'optimiser le processus d'extraction des données avec Scrapy, stocker ces données de manière flexible avec MongoDB, et fournir une interface utilisateur interactive pour explorer ces données à l'aide de Dash avec un backend Flask. Et nous avons choisis chacune de ces technologies en fonction de ses avantages spécifiques par rapport aux besoins du projet.

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

4. Arrêtez le projet avec la commande suivante :

   ```bash
   docker-compose down
   ```
5. Relancez le projet avec la commande suivante : 

   ```bash
   docker-compose up
   ```
   
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
