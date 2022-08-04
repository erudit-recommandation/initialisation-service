import joblib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

from pathlib import Path
import os
import pandas as pd


import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)


def generate_image(row, som_grid, cm, generate_image_directory):
    plt.figure(figsize=(10, 10))
    plt.imshow(som_grid.codebook.matrix[row['bmu']].reshape(50, 50), cmap=cm)
    plt.axis('off')
    path = os.path.join(generate_image_directory, str(row['idproprio'])+".svg")
    plt.savefig(str(path), bbox_inches='tight', pad_inches=0)
    plt.close()


def create_som_images(directory, n_rows):

    path = os.path.join(directory, 'doc_countvectors', 'sel_arr.npy')
    sel_arr = np.load(path)
    bmus = [int(bmu) for bmu in sel_arr[:, -1]]

    path = os.path.join(directory, 'doc_countvectors', 'som_grid')
    som_grid = joblib.load(path)

    path_df_som_grid = os.path.join(
        directory, 'doc_countvectors', 'df_som_grid_bmus.csv')

    cols = ['title', 'idproprio', 'bmu']

    path_doc_parse = os.path.join(directory, 'doc_parse.csv')
    cols_doc_parse = ['author', 'title', 'titrerev', 'idproprio', 'ppage', 'sstitrerev',
                      'idissnnum', 'nonumero', 'theme', 'periode', 'annee', 'lemma', 'text']

    generate_image_directory = os.path.join(directory, "SOM_imgs")
    insert_into_arangoDB = True

    colors = [(48/255, 61/255, 135/255), (217/255, 117/255, 169/255), (249/255, 249/255, 240/255), (241/255, 220/255, 169/255), (233/255, 189/255, 86/255), (225 /
                                                                                                                                                             255, 161/255, 71/255), (212/255, 143/255, 65/255), (186/255, 110/255, 54/255), (144/255, 78/255, 34/255), (125/255, 67/255, 28/255), (85/255, 45/255, 19/255)]
    cmap_name = 'xenotheka'
    cmap_name_r = 'xenotheka_r'
    cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=1000)
    cm_r = LinearSegmentedColormap.from_list(
        cmap_name_r, np.flip(colors, axis=0), N=1000)

    chunksize = 500
    notice_freq = 100

    imagecreated = 0
    df = pd.read_csv(path_df_som_grid, encoding='utf-8',
                     chunksize=chunksize, sep=',', usecols=cols)

    df_bonified_doc_parse = pd.read_csv(
        path_doc_parse, encoding='utf-8', nrows=n_rows, sep=';', lineterminator='\n', usecols=cols_doc_parse)

    df_bonified_doc_parse = df_bonified_doc_parse.assign(bmu=bmus,
                                                         som_persona=[som_grid.codebook.matrix[bmu].reshape(
                                                             50, 50) for bmu in bmus],
                                                         )
    save_path = os.path.join(directory, "doc_parse_extended.csv")
    df_bonified_doc_parse.to_csv(save_path, index=False)

    with df as reader:
        for chunk in reader:
            for (i, row) in chunk.iterrows():
                generate_image(row, som_grid, cm, generate_image_directory)
                imagecreated += 1
                if imagecreated % notice_freq == 0:
                    print("----{} document added----".format(imagecreated))

        print("---- Done -----")
