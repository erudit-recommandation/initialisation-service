# initialisation-service

Application qui permet de générer et de publier tous les modèles nécessaires au fonctionnement du site web [Nemo](https://github.com/erudit-recommandation/Nemo)

# Installation et dépendances
Les dépendances sont dans le fichier `requirement.txt`, ainsi que le module `fr_core_news_sm` de `spacy` et les modules `punkt` et `stopwords`. Il suffit de lancer la commande `make install` pour tout installer. Il faut également installer [arangoDb](https://www.arangodb.com/download-major/), si on désire se servir du mode "ARANGO_IMPORT" ([voir section usage](#usage))

# Usage
L'application est gérée par les fichiers `env.json` ou `env_dev.json`, ceux caractérise la construction des modèles et leur déploiement dans les services. Le champ `step` gère les opérations que l'application va effectuer les choix sont les suivants et l'ordre n'a pas d'importance: 

- "SEND_GENSIM_TO_SERVER" => envoie le modèle `gensim` au serveur
- "SEND_ARTICLE_TO_DB" => envoie les articles et les informations qui s'y rattachent dans la base de données
- "SEND_ALL" => effectue toutes les opérations
- "SEND_SENTENCES_TO_DB" => envoie les phrases à la base de données
- "EXTEND_ARTICLE_DB_WITH_PERSONA" => ajoute les images des persona dans la base de données
- "EXTEND_DB_WITH_BMU"=> ajoute les bmu dans la base de données

`import_sentences_mode` offre plusieurs options afin d'insérer les phrases dans la base de données:

- "ONE_BY_ONE" => insère les phrases une par une par, très lent (les articles et bmu sont insérés un par un, par contre leurs jeux de données sont beaucoup plus petits, une amélioration possible serait d'implémenté les modes d'importation également pour ces collections)
- "BULK" => insère les phrases en lot, c'est-à-dire l'insertion d'un coup de segments (chunksize) du fichier `csv` dans la base de données
- "ARANGO_IMPORT" => insère tout le `cvs` d'un coup et laisse la base de données faire la gestion de l'importation. Ce mode est le plus rapide, par contre ce mode a tendance a mal fonctionné.

Afin de lancer l'application, il suffit de simplement exécuter la commande `make run` afin de la configuration de développement (`env_dev.json`), pour lancer l'application en mode déploiement il faut lancer la commande `make run-deploy`.

## Exemple d'un fichier `env.json`
```json
{
    "corpus": [
        {
            "active": false, // est-ce que le corpus va être inséré
            "name": "érudit", // nom du corpus, seulement comme référence, il a aucune incidence
            "database_name": "erudit", // nom de la base de donnée, important pour le référencement par nemo
            "working_data": {
                "directory": "./data/erudit", // Emplacement des fichiers `doc_parse.csv`,`doce_sent_parse.csv`, `key_host_bmus.csv` ainsi que les images des persona dans le dossier `SOM_imgs` et les fichier de gensim dans le dossier `model`
                "doc_parse_cols": [ // colone de doc_parse
                    "author",
                    "title",
                    "titrerev",
                    "idproprio",
                    "ppage",
                    "sstitrerev",
                    "idissnnum",
                    "nonumero",
                    "theme",
                    "periode",
                    "annee"
                ]
            },
            "steps": [ // étape du déploiement à exécuter, l'ordre n'a pas d'importance, voir la section Usage pour plus d'information
                "EXTEND_ARTICLE_DB_WITH_PERSONA" 
            ],
            "large_gensim": true // est-ce que le modèle gensim est sur plusieur fichier (`.syn1neg.npy et wv.vectors.npy`)
        },
        {
            "active": true,
            "name": "Théorie de l'architecture française",
            "database_name": "libraryFr",
            "working_data": {
                "directory": "./data/Bibliotheque FR",
                "doc_parse_cols": [
                    "author",
                    "title",
                    "idproprio",
                    "date"
                ]
            },
            "steps": [
                "SEND_SENTENCES_TO_DB"
            ],
            "large_gensim": false
        }
    ],
    "db": {
        "url": "http://localhost:8529", // addresse de la base de données
        "username": "root", // nom de la base de données toujours root, pas besoin de le changer
        "password": "rootpassword", // mot de passe de la base de données
        "collectionName": "articles", // nom de la collection des articles, l'application brise si changé
        "sentencesCollectionName": "sentences", // nom de la collection des phrases, l'application brise si changé
        "viewName": "article_analysis"// nom de la vue des phrases, l'application brise si changé
    },
    "text_analysis_service": {
        "url": "http://localhost:8092/model", // addresse du service d'analyse de texte avec gemsim doit inclure la route `/model`
        "password": "Pqpj3uUvT37dKToGNUapv" // mot de passe du service
    },
    "import_sentences_mode": { // mode d'insertion des phrases voir usage
        "mode": "BULK", // nom du mode
        "chunksize": 2000, // taille des segments de la base de données seulement utilisé avec les mode `ONE_BY_ONE` et `BULK`, est ignorer avec `ARANGO_IMPORT`
        "arango_import_command": "arangoimport" // commande d'arango import est ignoré par tous les modes sauf ARANGO_IMPORT
    },
    "chunksize": 2000 // taille des segments de la base de données, plus ils sont gros plus l'insertion est rapide, mais nécéssite plus de ressources
}
```