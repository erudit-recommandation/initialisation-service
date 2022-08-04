import os
from pathlib import Path
import pandas as pd
import scipy.sparse
import joblib
import numpy as np

from matplotlib import pyplot as plt
from gnomonics.persona_text import persona_talks_grid, query_talks_grid

import warnings
warnings.filterwarnings("ignore")


directory = Path('./erudit')


def create_som_grid(n_row=100):
    path = os.path.join(directory, 'doc_parse.csv')
    corpus = pd.read_csv(path, encoding='utf-8', sep=';', nrows=n_row,
                         usecols=['title', 'titrerev', 'annee', 'idproprio'])
    corpus['author'] = [str(x) + '\n(' + str(int(y)) + ')' for x,
                        y in zip(corpus.titrerev, corpus.annee)]
    corpus['title'] = [str(t) for t in corpus.title]

    path = os.path.join(directory, 'doc_countvectors', 'som_codebook.npz')
    cb_vectors = scipy.sparse.load_npz(path).toarray()

    som_outpath = os.path.join(directory, 'doc_countvectors', 'som_grid')
    df_cb_grid = persona_talks_grid(cb_vectors, corpus, gridsize=[50, 50], masksize=[
                                    50, 50], som_outpath=som_outpath, plot_grid=False)

    path = os.path.join(directory, 'doc_countvectors', 'som_grid_bmus.npy')
    np.save(path, df_cb_grid.bmu)

    path = os.path.join(directory, 'doc_countvectors', 'df_som_grid_bmus.csv')

    df_cb_grid.to_csv(path, index=False)
