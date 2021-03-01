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
# author          : Will Carrara
# date            : 02-08-2021
#
# version         : 1.5
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
from model import inference
from utils import geonexl1g, nex_utils

# current directory
w = os.path.join(os.path.dirname(__file__))

# path for .toml configuration
path = w+'config/config.toml'

def animate(path):
    """Loads satellite collection for animation process.

    Args:
        path (str): A path to a dictionary of remote sensing data (.toml file)

    Returns:
        image (object): An series of .png images at discrete intervals

    Examples:
        >>> animate('config/config.toml')
    """

    # read satellite data file
    sat = toml.load(path)
    
    for key in sat.keys():
        L1G_directory = sat[key].get('collection')   # satellite collection to retrieve
        sensor = sat[key].get('sensor')              # corresponding sensor
        tile = sat[key].get('tile')                  # tile of interest
        year = sat[key].get('year')                  # year of interest
        doys = sat[key].get('doys')                  # day range to retrieve (exclusive)
        hours = sat[key].get('hours')                # hour of interest
        frames = sat[key].get('frames')              # duration
        remove = sat[key].get('remove')              # remove resultant png images
        file_name = sat[key].get('name')             # output file name

        # convert string to booelan
        str_bool = lambda x: True if x.lower()=='true' else False
        remove = str_bool(remove)

        # model checkpoint file
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'model/params.yaml')
        model, _ = inference.load_model(config_file)

        # retrieve tiles
        files = []
        geo = geonexl1g.GeoNEXL1G(L1G_directory, sensor)
        for doy in range(doys[0],doys[1]): files.append(geo.files(tile=tile, year=year, dayofyear=doy))
        files = pd.concat(files)

        # check if empty collection
        if files.shape[0] == 0:
            print("The requested satellite overpass data is not available.")
            continue

        files = files.sort_values(['dayofyear','hour','minute'])
        files = files[(files['hour'] >= hours[0]) & (files['hour'] <= hours[1])]

        count = 0
        for i, row in files.iterrows():
            f = row['file']
            f_split = f.split('_')

            # extract date
            y = f_split[2][0:4]
            m = f_split[2][4:6]
            d = f_split[2][6:8]
            t = f_split[3]

            # iterate counter
            count = count + 1
            print(str(count)+": processing: "+t)

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
            F = 0.05
            G = G * F + (1-F) * R

            #virtual_rgb = nex_utils.scale_rgb(R,G,B)

            # assemble virtual rgb image and scale
            virtual_rgb = np.concatenate([R, G, B], axis=2)
            virtual_rgb[virtual_rgb < 0.] = 0
            virtual_rgb /= 1.6

            # make and save image to disk
            fig = plt.figure(figsize=(10,10))
            ax = fig.add_subplot(111)
            plt.imshow(virtual_rgb**0.5)
            ax.text(0.95, 0.01, y+"-"+m+"-"+d+" "+t,
            verticalalignment='bottom', horizontalalignment='right',
            transform=ax.transAxes,
            color='white', fontsize=20)

            plt.axis('off')
            plt.tight_layout()

            # parse file name
            name = f_split[0].split('/')
            name = name[5]+'_'+name[7]+'_'+name[8]+'_'+name[9]+t

            plt.savefig(w+'images/{}'.format(name))
            plt.close()
        
        # apply color enhancement 
        nex_utils.color_fix()

        # convert .png images to .gif file
        nex_utils.make_gif(file_name)
        
        # remove .png files if desired
        if remove: nex_utils.empty_dir()
        
        quit()

animate(path)
