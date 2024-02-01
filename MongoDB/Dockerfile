# Utilisation de l'image officielle de MongoDB la plus récente comme base
FROM mongo:latest

# Auteurs du Dockerfile
LABEL authors="keren couton, matthieu constantin"

# Copie du fichier init-mongo.js, fichier d'initialisation, dans le répertoire d'initialisation de la base de données MongoDB
COPY ./init-mongo.js /docker-entrypoint-initdb.d/

# Exposition du port 27017
EXPOSE 27017

# Configuration d'un volume pour stocker les données de la base de données MongoDB
VOLUME /data/db

# Commande à exécuter lors du démarrage du conteneur
CMD ["mongod", "--bind_ip_all"]
