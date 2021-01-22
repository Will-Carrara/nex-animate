# _________________________ NASA AMES RESEARCH CENTER _________________________
# title           : nex_utils.py
# description     : A series of functions which
#
#                       |> Variables:
#                           -> NDVI (Normalized Difference Vegetation Index)
#                           -> Fc   (fractional cover)
#                           -> ETo  (reference evapotranspiration)
#                           -> Kcb  (basal crop coefficient)
#                           -> ETc  (basal crop evapotranspiration)
#
# author          : Will Carrara, Alberto Guzman
# date            : 12-16-2020
#
# version         : 1.5
# python_version  : 3.*
# _____________________________________________________________________________




N = M = 600
MAX_SCALE = 6000

def scale_rgb(data_b1, data_b2, data_b3):
   # logrithmic strech to match human visual sensibility
   max_in = MAX_SCALE
   max_out = 255
   ref = max_in*0.20          # 10% reflectance as the middle gray
   offset = max_out*0.5       # corresponding to ref
   scale = max_out*0.20/log(2.0)  # 20% linear increase for 2x in reflectance

   data_rgb = zeros((N, M, 3), 'u1')

   x = clip(data_b1, 1, max_in).astype('f4') # 1 will be zero in logarithm
   x = (log(x) - log(ref))*scale + offset
   x = clip(x, 0, max_out) # 1 will be zero in logarithm
   data_rgb[:, :, 0] = x.reshape(N, M).astype('u1')

   x = clip(data_b2, 1, max_in).astype('f4') # 1 will be zero in logarithm
   x = (log(x) - log(ref))*scale + offset
   x = clip(x, 0, max_out) # 1 will be zero in logarithm
   data_rgb[:, :, 1] = x.reshape(N, M).astype('u1')

   x = clip(data_b3, 1, max_in).astype('f4') # 1 will be zero in logarithm
   x = (log(x) - log(ref))*scale + offset
   x = clip(x, 0, max_out) # 1 will be zero in logarithm
   data_rgb[:, :, 2] = x.reshape(N, M).astype('u1')

   return data_rgb
