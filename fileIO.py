import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

SCREENWIDTH = 1520
SCREENHEIGHT = 1912

# returns a dictionary filled with the 20 different image arrays, with their key being [filename]/scan_xx.tif
def images_to_dict(voltage_type = 'darkfield'):
      COUNTS = 20
      # take the path to the directory that will be processed, accounting for windows/unix filesystems
      dirname: str = os.path.dirname(p = __file__)
      if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
            path: str = os.path.join(dirname, '2026-06-08_Detector_noise_calibration/', voltage_type)
      else: # windows
            path = os.path.join(dirname, '2026-06-08_Detector_noise_calibration\\', voltage_type) 
            
      image_dict: dict = {}

      for filename in glob.glob(pathname = os.path.join(path, '*.tif')): # loop through all the .tif image files in the specified folder
            image: Image = Image.open(fp = filename)
            image_as_array: np.ndarray = np.array(object = image)
            image_dict.update({filename: image_as_array})

      # print(image_dict.keys()) # test print
      
      return image_dict

def images_to_array(voltage_type = 'darkfield'):
      COUNTS = 20
      # take the path to the directory that will be processed, accounting for windows/unix filesystems
      dirname: str = os.path.dirname(p = __file__)
      if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
            path: str = os.path.join(dirname, '2026-06-08_Detector_noise_calibration/', voltage_type)
      else: # windows
            path: str = os.path.join(dirname, '2026-06-08_Detector_noise_calibration\\', voltage_type) 
            
      # now we will create the 3d np.array, first creating a 2d image array
      first_loop = True
      for filename in glob.glob(pathname = os.path.join(path, '*.tif')): # loop through all the .tif image files in the specified folder
            image_as_array: np.ndarray = np.array(object = Image.open(fp = filename))
            image_as_array = np.transpose(image_as_array)
            three_D_image_array: np.ndarray = image_as_array[:, :, None] # make a 2d image into a n * n * 1 three dimensional image for later

            if first_loop: # on the first loop, we can't combine the current with the previous, so we just set prev_array to the current one
                  prev_array: np.ndarray = three_D_image_array
                  first_loop = False
            else: # here, we add the new 3d array to the existing 3d array
                  prev_array = np.concat((prev_array, three_D_image_array), axis = 2)
      image_array: np.ndarray = prev_array
      print(image_array.shape)
      return image_array

def read_np_image_arrays(voltage_type = 'darkfield', filetype = 'npy', dist_type = 'avg'):
      dirname: str = os.path.dirname(p = __file__)
      safe_path: str = voltage_type[:4] + voltage_type[5:]
      if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
            full_path: str = f"{dirname}/Numpy image arrays/{voltage_type}/{dist_type}_array_{safe_path}.{filetype}"
      else: # windows
            full_path = f"{dirname}\\Numpy image arrays\\{voltage_type}\\{dist_type}_array_{safe_path}.{filetype}"
            
      if filetype == 'png':
            return full_path
      elif filetype == 'npy':
            return np.load(file = full_path)
       
# print(images_to_array())
# print(images_to_array(voltage_type = '45kV/10W')) # macos
# images: dict = images_to_dict(voltage_type = '45kV/10W') # macos
# print(images[r'C:\Users\beekm\programming_projects\Project-group-8\2026-06-08_Detector_noise_calibration\45kV\10W\scan_00.tif'])
