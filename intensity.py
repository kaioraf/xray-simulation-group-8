import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

from fileIO import *

#def read_np_image_arrays(voltage_type = 'darkfield', filetype = 'npy', dist_type = 'avg'):
intensity_array = 0
x_len = read_np_image_arrays().shape[0]
y_len = read_np_image_arrays().shape[1]

print(read_np_image_arrays()[x_len // 2, y_len // 2])







#intensity_list_30kV = []
#for filename in  glob.glob(os.path.join(path, '30kV')):
#    if 'dark' in filename:
#        array = np.load(filename)
#        intensity_list_30kV.append()

        
    


