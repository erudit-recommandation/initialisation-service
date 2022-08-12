import joblib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

from pathlib import Path
import os
import pandas as pd


import logging
logging.getLogger('matplotlib').setLevel(logging.ERROR)


def generate_image(i, som_mask, cm, generate_image_directory):
    plt.figure(figsize=(10, 10))
    plt.imshow(som_mask.codebook.matrix.T[i].reshape(50, 50), cmap=cm)
    plt.axis('off')
    path = os.path.join(generate_image_directory, str(i)+".svg")
    plt.savefig(str(path), bbox_inches='tight', pad_inches=0)
    plt.close()


def create_som_images(directory, n_rows):

    path = os.path.join(directory, 'doc_countvectors', 'som_mask')
    som_mask = joblib.load(path)

    generate_image_directory = os.path.join(directory, "SOM_imgs")

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

    for i in range(0, n_rows):
        generate_image(i, som_mask, cm, generate_image_directory)
        imagecreated += 1
        if imagecreated % notice_freq == 0:
            print("----{} document added----".format(imagecreated))

        print("---- Done -----")
