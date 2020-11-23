import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from model import inference
import geonexl1g

# set data directory
#L1G_directory = '/nex/datapool/geonex/public/GOES16/GEONEX-L1G/'
#sensor = 'G16'
L1G_directory = '/nex/datapool/geonex/public/GOES17/GEONEX-L1G/'
sensor = 'G17'

# Parameters
tile = 'h09v03'
#tile = 'h16v05'
year = 2020
hour = 18

# Model checkpoint file
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),'model/params.yaml')
model, _ = inference.load_model(config_file)

# Retrieve tiles
files = []
geo = geonexl1g.GeoNEXL1G(L1G_directory, sensor)
for doy in range(190,260):
	files.append(geo.files(tile=tile, year=year, dayofyear=doy))


print(len(files))
files = pd.concat(files)
print(len(files))

for i, row in files.iterrows():
	f = row['file']#.values()
	
	#if row['hour'] != hour:
	#	print("passed")
	#	pass
	
	# Read file
	dataobj = geonexl1g.L1GFile(f, resolution_km=1.)
	data = dataobj.load()

	# Translate domains
	h8_prediction = inference.domain_to_domain(model, data, sensor, 'H8')

	# Get RGB
	R = data[:,:,1:2]
	G = h8_prediction[:,:,1:2]
	B = data[:,:,0:1]

	# Scaling AHI closer to True Green
	F = 0.05
	G = G * F + (1-F) * R

	# Assemble Virtual RGB Image and Scale
	virtual_rgb = np.concatenate([R, G, B], axis=2)
	virtual_rgb[virtual_rgb < 0.] = 0
	virtual_rgb /= 1.6

	# Make and save image to disk
	plt.figure(figsize=(10,10))
	plt.imshow(virtual_rgb**0.5)
	plt.axis('off')
	plt.tight_layout()
	#plt.savefig('example.png')
	#plt.savefig(f+f'{i}.png')
	plt.savefig('test'+str(i)+'.png')

'''
ffmpeg -r 15 -f image2 -s 1920x1080 -i animation/rgb-%03d.png -crf 25  -pix_fmt yuv420p hurricane.mp4
'''

