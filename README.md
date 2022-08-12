# initialisation-service

Application qui permet de générer et de publier tous les modèles nécessaires au fonctionnement du site web [Nemo](https://github.com/erudit-recommandation/Nemo)

# Installation et dépendances
Les dépendances sont dans le fichier `requirement.txt`, ainsi que le module `fr_core_news_sm` de `spacy` et les modules `punkt` et `stopwords`. Il suffit de lancer la commande `make install` pour tout installer.

# Usage
L'application est gérée par les fichiers `env.json` ou `env_dev.json`, ceux caractérise la construction des modèles et leur déploiement dans les services. Le champ `step` gère les opérations que l'application va effectuer les choix sont les suivants et l'ordre n'a pas d'importance: 
- "BUILD_SOM" => construit le modèle SOM
- "SEND_gensim_TO_SERVER" => envoie le modèle `gensim` au serveur
- "BUILD_GENSIM_MODEL" => construit le modèle `gensim`
- "SEND_ARTICLE_TO_DB" => envoie les articles et les informations qui s'y rattachent dans la base de données
- "SEND_ARTICLE_TO_DB_RAW" => envoie simplement les articles dans la base de données
- "ALL" => effectue toutes les opérations
- "SEND_SENTENCES_TO_DB" => envoie les phrase à la base de donnée
- "CREATE_PERSONA_IMAGE" => création des images pour les persona

`max_rows_doc_parses` peut être assigné à `null` afin de prendre toutes les lignes des `doc_parse.csv`

Afin de lancer l'application, il suffit de simplement exécuter la commande `make run` afin de la configuration de développement (`env_dev.json`), pour lancer l'application en mode déploiement il faut lancer la commande `make run-deploy`.

## Exemple d'un fichier `env.json`
```json
{
   "working_data": [
        {
            "directory": "./erudit",
            "doc_parse_cols": [
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
                "annee",
                "lemma",
                "text"
            ]
        }
    ],
    "steps": [
        "SEND_ARTICLE_TO_DB_RAW"
    ], 
    "doc_dict": {
        "number_words": 1000
    },
    "max_rows_doc_parses": 200,
    "tfidf": {
        "max_features": 20000,
        "min_df": 2,
        "max_df": 0.75,
        "vocab": null
    },
    "som": {
        "number_of_som_cells": 300
    },
    "db": {
        "url": "http://localhost:8529",
        "username": "root",
        "password": "rootpassword",
        "databaseName": "erudit",
        "collectionName": "articles",
        "viewName": "article_analysis"
    },
    "text_analysis_service": {
        "url": "http://localhost:8092/model",
        "password": "Pqpj3uUvT37dKToGNUapv"
    }
}
```