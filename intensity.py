import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

from fileIO import images_to_array

dirname = os.path.dirname(__file__)
if (platform.system() == 'Linux' or platform.system() == 'Darwin'): #darwin = macos
    path = os.path.join(dirname, 'Numpy image arrays/')
else: #windows
    path = os.path.join(dirname, 'Numpy image arrays\\') 

intensity_array = np.zeros((5,5))

#for filename in glob.glob(os.path.join(path, '*.npy')): 
   # if 'avg' in filename:



intensity_array_30kV = np.array()
intensity_array_30kV.append(2)
print(intensity_array_30kV)
        
    


