import pandas as pd
import numpy as np
import scipy.sparse

from pathlib import Path
import os
from gnomonics.persona_text import corpus_vectors, vectors_som, plot_persona, plot_persona_grid, plot_single_persona, plot_persona_talks

mapsize = [50, 50]  # [50,50], unless for A2 Poster [70,50]


def create_som_codebook(directory, n_rows):
    path = os.path.join(directory, 'doc_parse.csv')
    df = pd.read_csv(path, encoding='utf-8', sep=';', nrows=n_rows,
                     usecols=['author', 'title', 'titrerev', 'annee', 'idproprio', 'lemma'])
    corpus = df.lemma

    dict_path = os.path.join(directory, 'doc_countvectors/doc_dict_counts.csv')
    X, columns = corpus_vectors(corpus, vectorizer='Tfidf', dict_outpath=dict_path, max_features=20000,
                                # min_df=0.001,max_df=1.00,
                                vocab=None)

    path = os.path.join(directory, 'doc_countvectors', 'doc_countvectors.npz')
    scipy.sparse.save_npz(path, X)

    path = os.path.join(directory, 'doc_countvectors',
                        'doc_countvectors_words.csv')
    pd.DataFrame(columns, columns=['words']).to_csv(path, sep=';')

    path = os.path.join(directory, 'doc_countvectors', 'doc_countvectors.npz')
    X_arr = scipy.sparse.load_npz(path)
    X_arr = X_arr.toarray()

    path = os.path.join(directory, 'doc_countvectors',
                        'doc_countvectors_words.csv')
    words = pd.read_csv(path, sep=';', usecols=['words'])

    som_outpath = os.path.join(directory, 'doc_countvectors', 'som_mask')
    cb, bmu_wordmatrix = vectors_som(
        vectors=X_arr.T, words=words, mapsize=mapsize, verbose='info', som_outpath=som_outpath, ask=False)

    path = os.path.join(directory, 'doc_countvectors', 'som_codebook.npz')
    scipy.sparse.save_npz(path, scipy.sparse.csr_matrix(cb))

    path = os.path.join(directory, 'doc_countvectors', 'words_by_bmu.csv')
    bmu_wordmatrix.to_csv(path, encoding='utf-8', sep=';')
