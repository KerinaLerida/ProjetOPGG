# Utiliser l'image Python 3.9 comme base
FROM python:3.9

# Auteurs du Dockerfile
LABEL authors="keren couton, matthieu constantin"

# Définition du répertoire de travail
WORKDIR /ApplicationDocker

# Copie du fichier requirements.txt dans le répertoire de travail
COPY ./requirements.txt .

# Installation des dépendances Python définies danns le fichier requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port 8050
EXPOSE 8050

# Copie de tous les fichiers du répertoire courant dans le répertoire de travail du conteneur
COPY . .

# Commande à exécuter au lancement du conteneur
CMD ["python", "dashboard.py"]
