import numpy as np
from imageAnalysis import *
# outline:
#       take average images for some voltage, then add gaussian standard deviations to it, 
#       this is for every pixel individually. then we also somehow, at some stage need to add blur gaussian 
#       let's do the gaussian blur later, start with going from an average image to some generated sample image

def parameters_to_image(avg_image, var_image):
      sigma_image = np.sqrt(var_image)
      # sigma_image =var_image
      generated_image = np.random.normal(avg_image, sigma_image)
      create_image(generated_image, exposure=3, filename='randomimage30kv40w.png')
      create_image(avg_image, exposure=3, filename='comparisonimage.png')
      

avg_image = read_np_image_arrays("30kV/10W", dist_type='avg')
var_image = read_np_image_arrays("30kV/10W", dist_type='var')
parameters_to_image(avg_image, var_image)