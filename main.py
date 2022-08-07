from create_doc_dict_count import create_doc_dict_count
from create_tfidf import create_tfidf
from create_som_grid import create_som_grid
from create_som_codebook import create_som_codebook
from create_som_model import create_som_model

from insert_into_arangodb import initialise_arango_db
from create_som_images import create_som_images

from send_d2v_model import send_d2v_model


import json
from pathlib import Path
import os
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('-d', required=False,
                    action="store_true", help="developpement mode")
parser.add_argument('-dd', required=False,
                    action="store_true", help="docker developpement mode")
parser.add_argument('-p', required=False,
                    action="store_true", help="production mode")
args = parser.parse_args()

env_variable = None
if args.d:
    print("developpement mode")
    with open(Path("./env_dev.json"), 'r') as f:
        env_variable = json.load(f)
elif args.dd:
    print("developpement mode with docker")
    with open(Path("./env_dev_docker.json"), 'r') as f:
        env_variable = json.load(f)
elif args.p:
    print("production mode")
    with open(Path("./env.json"), 'r') as f:
        env_variable = json.load(f)
else:
    print("developpement mode")
    with open(Path("./env_dev.json"), 'r') as f:
        env_variable = json.load(f)

for directory in env_variable["working_directory"]:

    doc_countvectors_path = os.path.join(directory, "doc_countvectors")
    try:
        os.mkdir(doc_countvectors_path)
    except:
        print("doc_countvectors exist")

    img_path = os.path.join(directory, "SOM_imgs")
    try:
        os.mkdir(img_path)
    except:
        print("img_path exist")
    if "BUILD_SOM" in env_variable["steps"] or "ALL" in env_variable["steps"]:
        create_doc_dict_count(
            directory=directory,
            number_words=env_variable["doc_dict"]["number_words"],
            n_rows=env_variable["max_rows_doc_parses"]
        )

        create_tfidf(
            directory=directory,
            max_features=env_variable["tfidf"]["max_features"],
            min_df=env_variable["tfidf"]["min_df"],
            max_df=env_variable["tfidf"]["max_df"],
            vocab=env_variable["tfidf"]["vocab"],
            n_rows=env_variable["max_rows_doc_parses"],
        )

        create_som_codebook(
            directory=directory,
            n_rows=env_variable["max_rows_doc_parses"],
        )

        create_som_grid(
            directory=directory,
            n_rows=env_variable["max_rows_doc_parses"],
        )

        create_som_model(
            directory=directory,
            n_rows=env_variable["max_rows_doc_parses"],
            number_of_som_cells=env_variable["som"]["number_of_som_cells"]
        )

        create_som_images(
            directory=directory,
            n_rows=env_variable["max_rows_doc_parses"],
        )

    if "SEND_ARTICLE_TO_DB" in env_variable["steps"] or "ALL" in env_variable["steps"]:
        initialise_arango_db(
            directory=directory,
            arangoURL=env_variable["db"]["url"],
            username=env_variable["db"]["username"],
            password=env_variable["db"]["password"],
            databaseName=env_variable["db"]["databaseName"],
            collectionName=env_variable["db"]["collectionName"],
            viewName=env_variable["db"]["viewName"],
        )
    elif "SEND_ARTICLE_TO_DB_RAW" in env_variable["steps"]:
        initialise_arango_db(
            directory=directory,
            arangoURL=env_variable["db"]["url"],
            username=env_variable["db"]["username"],
            password=env_variable["db"]["password"],
            databaseName=env_variable["db"]["databaseName"],
            collectionName=env_variable["db"]["collectionName"],
            viewName=env_variable["db"]["viewName"],
            raw=True,
        )

    if "SEND_GEMSIM_TO_SERVER" in env_variable["steps"] or "ALL" in env_variable["steps"]:
        sended = send_d2v_model(
            url=env_variable["text_analysis_service"]["url"],
            password=env_variable["text_analysis_service"]["password"]
        )
        if not sended:
            raise Exception("was not able to send the model to the server")
    print("----------------------- DONE ----------------------- ")
