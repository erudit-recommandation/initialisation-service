# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
from arango import ArangoClient
import numpy as np
import os
import json


def delete_badly_formated_articles(row):
    return row["idproprio"] == "47054ac" or row["idproprio"] == "010109ar"


def convert_df_to_arango(cols, row, i, idproprioIsPandas=False):
    doc = {}
    if delete_badly_formated_articles(row):
        return None
    for c in cols:
        if row[c] == None:
            pass
        elif c == "date":
            try:
                doc["annee"] = int(row[c])
            except:
                pass

        elif c == "sstitrerev":
            sstitrerev = row[c]
            sstitrerev = sstitrerev.split(" •")
            sstitrerev = [rev if rev[0] != " " else rev[1:]
                          for rev in sstitrerev]
            doc[c] = sstitrerev
        elif idproprioIsPandas and c == "idproprio":
            doc[c] = str(i)
        elif c == "idproprio":
            doc[c] = str(row[c])

        else:
            doc[c] = row[c]
    doc['pandas_index'] = i
    return doc


def insert_articles(directory, cols, arangoURL, username, password, databaseName, collectionName, viewName, idproprioIsPandas,chunksize):

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

    path = os.path.join(directory, "doc_parse.csv")
    df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize, usecols=cols,
                     sep=';', lineterminator='\n', index_col=False)

    insert_into_db(df, chunksize, collection)


def insert_into_db(df, chunksize, collection,updateBMU=False, idproprioIsPandas=False,):

    notice_freq = 1000
    nDocumentAdded = 0
    i = 0
    print("idproprio is pandas_index ", idproprioIsPandas)

    with df as reader:
        for chunk in reader:
            chunk.reset_index(inplace=True)
            chunk.replace({np.nan: None}, inplace=True)
            cols = list(chunk.columns)
            for (_, row) in chunk.iterrows():
                doc = convert_df_to_arango(
                    cols, row, i, idproprioIsPandas=idproprioIsPandas)
                if doc is None:
                    print("A badly formated article")
                else:
                    try:
                        if updateBMU:
                            query, update = {'idproprio': str(doc["idproprio"])}, {
                                'bmu': int(doc["key_bmu"])}
                            collection.update_match(query, update)
                        else:
                            collection.insert(doc)
                    except Exception as e:
                        print(
                            "---an error happen when inserting with error {} with document {}---".format(e, doc))
                    finally:
                        nDocumentAdded += 1
                    if nDocumentAdded % notice_freq == 0:
                        print("----{} document added----".format(nDocumentAdded))
                i += 1
    print("---- Done -----")


def insert_sentences(directory, arangoURL, username, password, databaseName, collectionName, viewName, mode):
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

    path = Path('{}/doc_sent_parse.csv'.format(directory))
    if mode["mode"]=="ONE_BY_ONE":
        chunksize = mode["chunksize"]
        cols = ["idproprio", "text", "index_nm", "pandas_index"]
        df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize,
                        sep=';', lineterminator='\n', index_col=False, usecols=cols)
        insert_into_db(df, chunksize, collection)
        
    elif mode["mode"] =="BULK":
        chunksize = mode["chunksize"]
        cols = ["idproprio", "text", "index_nm"]
        df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize,
                        sep=';', lineterminator='\n', index_col=False, usecols=cols)
        with df as reader:
            for chunk in reader:
                chunk.reset_index(inplace=True)
                chunk.replace({np.nan: None}, inplace=True)
                chunk["idproprio"] = chunk["idproprio"].astype("string")

                tempDocs = chunk.to_dict('records')
                docs = []
                for t in tempDocs:
                    t["pandas_index"] = t.pop("index")
                    docs.append(t)
                collection.import_bulk(docs, halt_on_error=False,details=False)
                
                    
        
    elif mode["mode"] =="ARANGO_IMPORT":
    
        if "localhost" in arangoURL:
            arangoURL = arangoURL.replace("http", "http+tcp")
        elif "arangodb.cloud" in arangoURL:
            arangoURL = arangoURL.replace("https", "ssl")

        command = '{arangoImportCommand} --server.endpoint {db_url} \
        --server.username root --server.password="{password}" --server.database="{database}"\
        --file "{csv}" --type csv --collection "{collection}" --datatype idproprio=string \
        --datatype index_nm=number --datatype text=string --separator=";" --auto-rate-limit'.format(
            arangoImportCommand=mode["arango_import_command"],
            password=password,
            database=databaseName,
            collection=collectionName,
            db_url=arangoURL,
            csv=path)
        stream = os.popen(command)
        output = stream.read()
        print(output)


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
                    pandas_index -= 1

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


def insert_bmu(directory, arangoURL, username, password, databaseName, chunksize,collectionName):
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

    path = Path('{}/key_host_bmus.csv'.format(directory))
    df = pd.read_csv(path, encoding='utf-8', chunksize=chunksize,
                     sep=';', lineterminator='\n', index_col=False)
    insert_into_db(df, chunksize, collection, updateBMU=True)
