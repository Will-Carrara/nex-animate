# _________________________ NASA AMES RESEARCH CENTER _________________________
# title           : nex_utils.py
# description     : A series of utility functions to be used in the animation
#                   and color correction process.
#
#                       |> Functions:
#                           -> scale_rgb (green band scaling)
#                           -> make_gif   (png images to gif)
#
# author          : Will Carrara
# date            : 03-01-2021
#
# version         : 1.1.2
# python_version  : 3.*
# _____________________________________________________________________________

# system handling
import os
import glob

# image handling
import imageio
from PIL import ImageEnhance, Image

# data processing
import numpy as np

N = M = 600
MAX_SCALE = 6000

# image directory location
png_dir = 'images/'

def scale_rgb(data_b1, data_b2, data_b3):
    """Logarithmic stretch to match human visual sensibility."""

    max_in = MAX_SCALE
    max_out = 255
    ref = max_in*0.20          # 10% reflectance as the middle gray
    offset = max_out*0.5       # corresponding to ref
    scale = max_out*0.20/np.log(2.0)  # 20% linear increase for 2x in reflectance

    data_rgb = np.zeros((N, M, 3), 'u1')

    x = np.clip(data_b1, 1, max_in).astype('f4') # 1 will be zero in logarithm
    x = (np.log(x) - np.log(ref))*scale + offset
    x = np.clip(x, 0, max_out) # 1 will be zero in logarithm
    data_rgb[:, :, 0] = x.reshape(N, M).astype('u1')

    x = np.clip(data_b2, 1, max_in).astype('f4') # 1 will be zero in logarithm
    x = (np.log(x) - np.log(ref))*scale + offset
    x = np.clip(x, 0, max_out) # 1 will be zero in logarithm
    data_rgb[:, :, 1] = x.reshape(N, M).astype('u1')

    x = np.clip(data_b3, 1, max_in).astype('f4') # 1 will be zero in logarithm
    x = (np.log(x) - np.log(ref))*scale + offset
    x = np.clip(x, 0, max_out) # 1 will be zero in logarithm
    data_rgb[:, :, 2] = x.reshape(N, M).astype('u1')

    return data_rgb



def color_fix():
    """Apply color enhancement."""
    
    # loop through images 
    for file_name in sorted(os.listdir(png_dir)):
       if file_name.endswith('.png'):
          file_path = os.path.join(png_dir, file_name) 
          # read image
          image = Image.open(file_path)
          
          # increase contrast
          enhancer = ImageEnhance.Contrast(image)
          image = enhancer.enhance(1.75)
          
          # overwrite image
          image = image.save(png_dir+'/'+file_name) 


def make_gif(name):
    """ Generate .gif file."""
    
    # empty image list
    images = []

    for file_name in sorted(os.listdir(png_dir)):
       if file_name.endswith('.png'):
           file_path = os.path.join(png_dir, file_name)
           images.append(imageio.imread(file_path))

    # save as .gif
    imageio.mimsave('output/'+name+'.gif', images, duration=.1)


def empty_dir():
    """Remove old images."""

    # resulted images
    files = glob.glob('images/*.png')
    for f in files: os.remove(f)
