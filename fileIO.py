import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

#returns a dictionary filled with the 20 different image arrays, with their key being [filename]/scan_xx.tif
def image_to_dict(voltage_type = 'darkfield'):
      #take the path to the directory that will be processed, accounting for windows/unix filesystems
      dirname = os.path.dirname(__file__)
      if (platform.system() == 'Linux' or platform.system() == 'Darwin'): #darwin = macos
            path = os.path.join(dirname, '2026-06-08_Detector_noise_calibration/', voltage_type)
      else: #windows
            path = os.path.join(dirname, '2026-06-08_Detector_noise_calibration\\', voltage_type) 
            
      image_dict = {}

      for filename in glob.glob(os.path.join(path, '*.tif')): #loop through all the .tif image files in the specified folder
            image = Image.open(filename)
            image_as_array = np.array(image)
            image_dict.update({filename: image_as_array})

      # print(image_dict.keys()) #test print
      
      return image_dict

image_to_dict()            