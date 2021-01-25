# NASA EARTH EXCHANGE ANIMATE
>
>
> ## Abstract
> This document provides a brief description of the animation tool set developed by the NASA Earth Exchange program. These tools can be used to animate remote sensing data with a .HDF file extension. To approximate true color, this process uses a deep learning VAE-GAN Architecture for unsupervised image-to-image translation with shared spectral reconstruction loss which was trained on GOES-16/17 and Himawari-8 L1B data processed by GeoNEX. More information on this model can be found [here](https://github.com/tjvandal/unsupervised-spectral-synthesis).
>
>
> ## Tutorial
> A detailed walk-through on the operation of these tools has been assembled in the following series of documentation contained in the links below:
> 1. [Using NEX-Animate](docs/tutorial.md)
>
> ## Example Output
> <img src="docs/nex.gif"/>
>
>
> ## Data Availability
> Data is available through the GeoNEX data portal for all states in the contiguous U.S. Data is available from January 1st, 2019 through present (up through the most recently available GOES-16/17 and Himawari-8 L1B SR data for each location).
>
>
> ## Restrictions
> GeoNEX data is freely available, but users that redistribute GeoNEX data are requested to acknowledge and credit NASA NEX as the source of the data. The GeoNEX datasets are distributed for research, evaluation, and demonstration purposes only.