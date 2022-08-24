from create_doc_dict_count import create_doc_dict_count
from create_tfidf import create_tfidf
from create_som_grid import create_som_grid
from create_som_codebook import create_som_codebook
from create_som_model import create_som_model

from insert_into_arangodb import insert_articles, insert_sentences, insert_images, insert_bmu
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

for corpus in env_variable["corpus"]:
    if corpus["active"]:
        directory = corpus["working_data"]["directory"]

        img_path = os.path.join(directory, "SOM_imgs")

        model_path = os.path.join(directory, "model")

        if "SEND_ARTICLE_TO_DB" in corpus["steps"] or "SEND_ALL" in corpus["steps"]:
            try:
                idproprioIsPandas = True
                if corpus["name"] == "érudit":
                    idproprioIsPandasu = False
                insert_articles(
                    directory=directory,
                    cols=corpus["working_data"]["doc_parse_cols"],
                    arangoURL=env_variable["db"]["url"],
                    username=env_variable["db"]["username"],
                    password=env_variable["db"]["password"],
                    databaseName=corpus["database_name"],
                    collectionName=env_variable["db"]["collectionName"],
                    viewName=env_variable["db"]["viewName"],
                    idproprioIsPandas=idproprioIsPandas
                )
            except Exception as e:
                print("SEND_ARTICLE_TO_DB failed: ", e)

        if "SEND_SENTENCES_TO_DB" in corpus["steps"] or "SEND_ALL" in corpus["steps"]:
            try:
                insert_sentences(
                    directory=directory,
                    arangoURL=env_variable["db"]["url"],
                    username=env_variable["db"]["username"],
                    password=env_variable["db"]["password"],
                    databaseName=corpus["database_name"],
                    collectionName=env_variable["db"]["sentencesCollectionName"],
                    viewName=env_variable["db"]["viewName"],
                    arangoImportCommand=env_variable["arango_import_command"]
                )
            except Exception as e:
                print("SEND_SENTENCES_TO_DB failed: ", e)

        if "EXTEND_ARTICLE_DB_WITH_PERSONA" in corpus["steps"] or "SEND_ALL" in corpus["steps"]:
            try:
                idproprioImages = True
                if corpus["name"] == "érudit":
                    idproprioImages = False
                insert_images(
                    directory=directory,
                    arangoURL=env_variable["db"]["url"],
                    username=env_variable["db"]["username"],
                    password=env_variable["db"]["password"],
                    databaseName=corpus["database_name"],
                    collectionName=env_variable["db"]["collectionName"],
                    img_repertory=img_path,
                    idproprioImages=idproprioImages,
                )
            except Exception as e:
                print("EXTEND_ARTICLE_DB_WITH_PERSONA failed: ", e)

        if "EXTEND_DB_WITH_BMU" in corpus["steps"] or "SEND_ALL" in corpus["steps"]:
            try:
                insert_bmu(
                    directory=directory,
                    arangoURL=env_variable["db"]["url"],
                    username=env_variable["db"]["username"],
                    password=env_variable["db"]["password"],
                    databaseName=corpus["database_name"],
                    collectionName=env_variable["db"]["collectionName"],
                )
            except Exception as e:
                print("EXTEND_DB_WITH_BMU failed: ", e)

        if "SEND_GENSIM_TO_SERVER" in corpus["steps"] or "SEND_ALL" in corpus["steps"]:
            sended = send_d2v_model(
                url=env_variable["text_analysis_service"]["url"],
                password=env_variable["text_analysis_service"]["password"],
                largeModel=corpus["large_gensim"],
                database_name=corpus["database_name"],
                directory = corpus["working_data"]["directory"]
            )
            if not sended:
                print("was not able to send the model to the server")
        print("----------------------- DONE {} -----------------------".format(corpus["name"]))
print("--- LEAVING ---")
