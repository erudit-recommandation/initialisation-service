import requests
from pathlib import Path


def send_d2v_model(url, password):
    model = open(Path("./model/d2v.model"), 'rb')
    syn1neg = open(Path("./model/d2v.model.syn1neg.npy"), 'rb')
    vectors = open(Path("./model/d2v.model.wv.vectors.npy"), 'rb')
    files = {
        'd2v.model': model,
        'd2v.model.syn1neg.npy': syn1neg,
        'd2v.model.wv.vectors.npy': vectors
    }

    obj = {
        "password": password,
    }

    r = requests.post(url, files=files, data=obj)

    return r.status_code == requests.codes.ok
