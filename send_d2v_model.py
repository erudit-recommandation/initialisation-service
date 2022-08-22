import requests
from pathlib import Path


def send_d2v_model(url, directory, password, largeModel, database_name):
    model = open(Path("{}/model/d2v.model".format(directory)), 'rb')
    files = None
    if largeModel:
        syn1neg = open(Path("{}/model/d2v.model.syn1neg.npy".format(directory)), 'rb')
        vectors = open(Path("{}/model/d2v.model.wv.vectors.npy".format(directory)), 'rb')

        files = {
            'd2v.model': model,
            'd2v.model.syn1neg.npy': syn1neg,
            'd2v.model.wv.vectors.npy': vectors
        }
    else:
        files = {
            'd2v.model': model,
        }

    obj = {
        "password": password,
    }
    url = "{}/{}".format(url,database_name)
    r = requests.post(url, files=files, data=obj)

    return r.status_code == requests.codes.ok
