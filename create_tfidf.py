from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd
import joblib

from pathlib import Path
import os

directory = Path('./erudit')
max_features = 20000
min_df = 2
max_df = 0.75
vocab = None


def create_tfidf(n_row=100):

    path = os.path.join(directory, 'doc_parse.csv')
    df = pd.read_csv(path, encoding='utf-8', sep=';', nrows=n_row,
                     usecols=['author', 'title', 'titrerev', 'annee', 'idproprio', 'lemma'])
    corpus = df.lemma

    vectorizer = TfidfVectorizer(
        max_features=max_features, min_df=min_df, max_df=max_df, vocabulary=vocab, sublinear_tf=True)

    X = vectorizer.fit_transform(corpus)
    path = path = os.path.join(directory, 'tfidf_model')
    joblib.dump(vectorizer, path, compress=True)
