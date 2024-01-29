# Utiliser l'image officielle MongoDB
FROM mongo:latest

LABEL authors="keren couton, matthieu constantin"

# Copier le script init-mongo.js dans le conteneur
#COPY ./MongoDB/init-mongo.js /docker-entrypoint-initdb.d/
COPY ./init-mongo.js /docker-entrypoint-initdb.d/

# Exposer le port par défaut de MongoDB
EXPOSE 27017

# Définir un volume pour persister les données MongoDB en dehors du conteneur
VOLUME /data/db

# Commande pour démarrer mongod avec bind_ip_all
CMD ["mongod", "--bind_ip_all"]
