# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
from arango import ArangoClient
import numpy as np
import os
import json


def delete_badly_formated_articles(row):
    return row["idproprio"] == "47054ac" or row["idproprio"] == "010109ar"


def convert_df_to_arango(cols, row, i):
    doc = {}
    if delete_badly_formated_articles(row):
        return None
    for c in cols:
        if row[c] == None:
            pass
        elif c=="date":
            doc["annee"] = row[c]
        elif c == "sstitrerev":
            sstitrerev = row[c]
            sstitrerev = sstitrerev.split(" •")
            sstitrerev = [rev if rev[0] != " " else rev[1:]
                          for rev in sstitrerev]
            doc[c] = sstitrerev
        elif c=="idproprio":
            doc[c] = str(row[c])

        else:
            doc[c] = row[c]
    doc['pandas_index'] = i
    return doc


def insert_articles(directory, cols, arangoURL, username, password, databaseName, collectionName, viewName, raw=False):

    client = ArangoClient(hosts=arangoURL)
    sys_db = client.db("_system", username=username, password=password)
    db = None
    if not sys_db.has_database(databaseName):
        sys_db.create_database(databaseName)
        db = client.db(databaseName, username=username, password=password)
    else:
        print("the database already exist")
        db = client.db(databaseName, username=username, password=password)

    collection = None
    if db.has_collection(collectionName):
        collection = db.collection(collectionName)
    else:
        collection = db.create_collection(collectionName)
        collection.add_persistent_index(fields=["idproprio"], unique=True)
        collection.add_persistent_index(fields=["bmu"])
        collection.add_persistent_index(fields=["pandas_index"], unique=True)

    chunksize = 1000

    df = None
    if raw:
        path = Path('{}/doc_parse.csv'.format(directory))
        df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize, usecols=cols,
                         sep=';', lineterminator='\n', index_col=False)
    else:
        cols.extend(["bmu", "som_persona"])

        path = Path('{}/doc_parse_extended.csv'.format(directory))
        df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize, usecols=cols,
                         sep=',', lineterminator='\n', index_col=False)
    insert_into_db(df, chunksize, collection)


def insert_into_db(df, chunksize, collection, updateBMU=False):

    notice_freq = 1000
    nDocumentAdded = 0
    i = 0

    with df as reader:
        for chunk in reader:
            chunk.reset_index(inplace=True)
            chunk.replace({np.nan: None}, inplace=True)
            cols = list(chunk.columns)
            for (_, row) in chunk.iterrows():
                doc = convert_df_to_arango(cols, row, i)
                if doc is None:
                    print("A badly formated article")
                else:
                    try:
                        if updateBMU:
                            query, update= {'idproprio': doc["idproprio"]}, {'bmu': int(doc["key_bmu"])}
                            collection.update_match(query, update)
                        else:
                            collection.insert(doc)
                    except Exception as e:
                        print(
                            "---an error happen when inserting with error {} with document {}---".format(e, i))
                    finally:
                        nDocumentAdded += 1
                    if nDocumentAdded % notice_freq == 0:
                        print("----{} document added----".format(nDocumentAdded))
                i += 1
    print("---- Done -----")


def insert_sentences(directory, arangoURL, username, password, databaseName, collectionName, viewName):
    client = ArangoClient(hosts=arangoURL)
    sys_db = client.db("_system", username=username, password=password)
    db = None
    if not sys_db.has_database(databaseName):
        sys_db.create_database(databaseName)
        db = client.db(databaseName, username=username, password=password)
    else:
        print("the database already exist")
        db = client.db(databaseName, username=username, password=password)

    collection = None
    if db.has_collection(collectionName):
        collection = db.collection(collectionName)
    else:
        collection = db.create_collection(collectionName)
        collection.add_fulltext_index(fields=["text"])
        collection.add_persistent_index(fields=["idproprio"])
        collection.add_persistent_index(fields=["index_nm"])
        collection.add_persistent_index(fields=["pandas_index"], unique=True)
        db.create_view(name=viewName, view_type='arangosearch',
                       properties={
                           'links': {
                               collectionName: {
                                   'fields': {
                                       'text': {
                                           'analyzers': [
                                               'text_fr'
                                           ]
                                       }
                                   }
                               }
                           }
                       })

    chunksize = 1000
    cols = ["idproprio", "text", "index_nm"]
    path = Path('{}/doc_sent_parse.csv'.format(directory))
    df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize,
                     sep=';', lineterminator='\n', index_col=False, usecols=cols)
    insert_into_db(df, chunksize, collection)


def insert_images(directory, arangoURL, username, password, databaseName, collectionName, img_repertory, idproprioImages=False):
    client = ArangoClient(hosts=arangoURL)
    sys_db = client.db("_system", username=username, password=password)
    db = None
    if sys_db.has_database(databaseName):
        db = client.db(databaseName, username=username, password=password)
    else:
        raise Exception("database don't exist")

    collection = None
    if db.has_collection(collectionName):
        collection = db.collection(collectionName)
    else:
        raise Exception("collection don't exist")
    image_list = os.listdir(img_repertory)

    notice_freq = 1000
    nDocumentAdded = 0
    failledImages = []
    for img in image_list:
        svg = None
        if ".svg" in img:
            try:
                with open(os.path.join(img_repertory, img), "r") as f:
                    svg = f.read()
                img_name_split = img.split(".")
                pandas_index = int(img_name_split[0])
                if idproprioImages:
                    pandas_index-=1
                    
                collection.update_match(
                    {'pandas_index': pandas_index}, {'persona_svg': svg})
                if nDocumentAdded % notice_freq == 0:
                    print("----{} document added----".format(nDocumentAdded))
                nDocumentAdded += 1
            except Exception as e:
                failledImages.append(img)
                print("fail to add {} with error: {}".format(img, e))
    if len(failledImages) != 0:
        json_object = json.dumps({"payload": failledImages})
        with open("{}/failled_images.json".format(directory), "w") as f:
            f.write(json_object)


def insert_bmu(directory, arangoURL, username, password, databaseName, collectionName):
    client = ArangoClient(hosts=arangoURL)
    sys_db = client.db("_system", username=username, password=password)
    db = None
    if sys_db.has_database(databaseName):
        db = client.db(databaseName, username=username, password=password)
    else:
        raise Exception("database don't exist")

    collection = None
    if db.has_collection(collectionName):
        collection = db.collection(collectionName)
    else:
        raise Exception("collection don't exist")
    chunksize = 1000

    path = Path('{}/key_host_bmus.csv'.format(directory))
    df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize,
                     sep=';', lineterminator='\n', index_col=False)
    insert_into_db(df, chunksize, collection, updateBMU=True)
