# reads raw detector tif files and saved numpy image arrays, including the project orientation convention.
import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform
import time

SCREENWIDTH = 1520
SCREENHEIGHT = 1912
dataset_type = '1000'

# project orientation note:
# the detector is physically 1912 pixels wide and 1520 pixels high.
# early in the project, arrays were loaded transposed and the rest of the code
# was built around that convention. because changing it now would break many
# maps and fits, read_np_image_arrays keeps returning arrays in this historical
# project orientation. newly added datasets should be saved normally; only mark
# them for transposing here if they were saved in the same old reversed way.

if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
      SLASH = '/'
else: # windows
      SLASH = '\\'
            

# returns the raw old .tif images for one setting as a dictionary keyed by filename.
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
      start = time.time()
      # take the path to the directory that will be processed, accounting for windows/unix filesystems
      dirname: str = os.path.dirname(p = __file__)
      path: str = os.path.join(dirname, f"2026-06-08_Detector_noise_calibration{SLASH}", voltage_type)
            
      # load each 2D .tif image and stack them into a 3D array.
      
      image_files = glob.glob(pathname = os.path.join(path, '*.tif'))
      array_of_images = [np.array(Image.open(filename), dtype=np.float64).T for filename in image_files]
      stacked_images = np.stack(array_of_images, axis=2)
      print(stacked_images.shape)
      
      # prev_array = np.array(Image.open(image_files[0]), dtype=np.float64).T[:, :, None]
      # for filename in glob.glob(pathname = os.path.join(path, '*.tif')): # loop through all the .tif image files in the specified folder
      #       image_as_array = np.array(Image.open(filename), dtype=np.float64).T
      #       three_D_image_array: np.ndarray = image_as_array[:, :, None] # make a 2d image into a n * n * 1 three dimensional image for later
            
      #       prev_array = np.concat((prev_array, three_D_image_array), axis = 2)
      # image_array: np.ndarray = prev_array
      end = time.time()
      print(f"Converted images to arrays in {end - start} seconds")
      return stacked_images

def safe_image_path(voltage_type):
      if voltage_type == 'darkfield':
            return 'darkfield'

      return voltage_type[:4] + voltage_type[5:]


def read_np_image_arrays(voltage_type = 'darkfield', filetype = 'npy', dist_type = 'avg'):
      dirname: str = os.path.dirname(p = __file__)
      # filenames omit the slash in settings like "90kV/40W".
      safe_path: str = safe_image_path(voltage_type = voltage_type)
      if dataset_type == '1000':
            full_path: str = f"{dirname}{SLASH}2026-06-15_numpy_image_arrays{SLASH}{voltage_type}{SLASH}{dist_type}_array_{safe_path}.{filetype}"
            if filetype == 'png':
                  return full_path
            elif filetype == 'npy':
                  # the 1000-image arrays were saved in the opposite orientation from
                  # the rest of the project, so they are transposed on load.
                  return (np.load(file = full_path)).T
      elif dataset_type == '20':
            full_path: str = f"{dirname}{SLASH}Numpy image arrays{SLASH}{voltage_type}{SLASH}{dist_type}_array_{safe_path}.{filetype}"
            if filetype == 'png':
                  return full_path
            elif filetype == 'npy':
                  return (np.load(file = full_path))
      
            
