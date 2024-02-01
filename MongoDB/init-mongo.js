// Connexion à la base de données 'TestScraping'
var db = db.getSiblingDB('TestScraping');

// Initialisation des collections
db.createCollection('Joueurs');            // Collection pour les joueurs
db.createCollection('Champions');          // Collection pour les champions
db.createCollection('Ranked');             // Collection pour les ranked, parties classées pour chaque joueur
db.createCollection('MostChampPlayed');    // Collection pour les champions les plus joués pour chaque joueur
db.createCollection('Teams');              // Collection pour les équipes
db.createCollection('Regions');            // Collection pour les régions
