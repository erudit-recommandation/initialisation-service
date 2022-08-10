# -*- coding: utf-8 -*-

import pandas as pd
from pathlib import Path
from arango import ArangoClient
import numpy as np


def delete_badly_formated_articles(row):
    return row["idproprio"] == "47054ac" or row["idproprio"] == "010109ar"


def convert_df_to_arango(cols, row, i):
    doc = {}
    if delete_badly_formated_articles(row):
        return None
    for c in cols:
        if row[c] == None:
            pass
        elif c == "sstitrerev":
            sstitrerev = row[c]
            sstitrerev = sstitrerev.split(" •")
            sstitrerev = [rev if rev[0] != " " else rev[1:]
                          for rev in sstitrerev]
            doc[c] = sstitrerev

        else:
            doc[c] = row[c]
    doc['pandas_index'] = i
    return doc


def initialise_arango_db(directory, cols, arangoURL, username, password, databaseName, collectionName, viewName, raw=False):

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
        collection.add_persistent_index(fields=["idproprio"], unique=True)
        collection.add_persistent_index(fields=["title"])
        collection.add_persistent_index(fields=["author"])
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
    notice_freq = 1000
    nDocumentAdded = 0
    i = 0

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
                        collection.insert(doc)
                    except:
                        print(
                            "---an error happen when inserting with error {}---".format(i))
                    finally:
                        nDocumentAdded += 1
                    if nDocumentAdded % notice_freq == 0:
                        print("----{} document added----".format(nDocumentAdded))
                i += 1
    print("---- Done -----")
