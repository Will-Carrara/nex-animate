# _________________________ NASA AMES RESEARCH CENTER _________________________
# title           : animate.py
# description     : Animation tool set developed by the NASA Earth Exchange
#                   program. These tools can be used to animate remote sensing
#                   data with a .HDF file extension. This process uses a deep
#                   learning VAE-GAN Architecture for unsupervised image-to-image
#                   translation with shared spectral reconstruction loss which
#                   was trained on GOES-16/17 and Himawari-8 L1B data processed
#                   by GeoNEX.
#
#                       |> Parameters:
#                           -> config.toml
#
# author          : Will Carrara, Alberto Guzman
# date            : 01-22-2021
#
# version         : 1.3
# python_version  : 3.*
# _____________________________________________________________________________

# system handling
import os
import glob

# config file handling
import toml

# image processing
from PIL import Image
import matplotlib.pyplot as plt

# data processing
import pandas as pd
import numpy as np

# utility files
from utils.model import inference
from utils import geonexl1g

# current directory
w = os.path.join(os.path.dirname(__file__), '..')

# path for .toml configuration
path = w+'/config/config.toml'

def animate(path):
    """Loads satellite collection for animation process.

    Args:
        path (str): A path to a dictionary of remote sensing data (.toml file)

    Returns:
        image (object): An series of .png images at discrete intervals

    Examples:
        >>> animate('../config/config.toml')
    """

    # read satellite data file
    sat = toml.load(path)

    L1G_directory = sat['ANIMATE'].get('collection')   # satellite collection to retrieve
    sensor = sat['ANIMATE'].get('sensor')              # corresponding sensor
    tile = sat['ANIMATE'].get('tile')                  # tile of interest
    year = sat['ANIMATE'].get('year')                  # year of interest
    doys = sat['ANIMATE'].get('doys')                  # day range to retrieve (exclusive)
    hour = sat['ANIMATE'].get('hour')                  # hour of interest

    # model checkpoint file
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'model/params.yaml')
    model, _ = inference.load_model(config_file)

    # retrieve tiles
    files = []
    geo = geonexl1g.GeoNEXL1G(L1G_directory, sensor)
    for doy in range(doys[0],doys[1]): files.append(geo.files(tile=tile, year=year, dayofyear=doy))
    files = pd.concat(files)
    files = files.sort_values(['dayofyear','hour','minute'])
    files = files[(files['hour'] >= 14) & (files['hour'] <= 24)]

    count = 0
    for i, row in files.iterrows():
        f = row['file']

        # iterate counter
        count = count + 1
        print(str(count)+": proccesing: "+ f[-32:-4])

        # read file
        dataobj = geonexl1g.L1GFile(f, resolution_km=1.)
        data = dataobj.load()

        # translate domains
        h8_prediction = inference.domain_to_domain(model, data, sensor, 'H8')

        # get rgb
        R = data[:,:,1:2]
        G = h8_prediction[:,:,1:2]
        B = data[:,:,0:1]

        # scaling AHI closer to true green
        F = 0.04
        G = G * F + (1-F) * R

        # assemble virtual rgb image and scale
        virtual_rgb = np.concatenate([R, G, B], axis=2)
        virtual_rgb[virtual_rgb < 0.] = 0
        virtual_rgb /= 1.6

        # make and save image to disk
        plt.figure(figsize=(10,10))
        plt.imshow(virtual_rgb**0.5)
        plt.axis('off')
        plt.tight_layout()
        #plt.savefig(f[-43:-4]+'.png')
        plt.savefig(f[-32:-4]+'.png')
        plt.close()