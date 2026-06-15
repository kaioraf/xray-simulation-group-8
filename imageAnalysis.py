#
# Collection of functions to analyse the image arrays, taking their average and their standard deviation, either of an 
# entire layer of images or a single layer of pixels
#

import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

from fileIO import images_to_array

VOLTAGES = {30, 45, 60, 75, 90} 
WATTAGES = {10, 20, 30, 40}
COUNTS = 20


#take all the files within some folder e.g. 75kV/10W/, and then averages all their values into a single new image
def average_full_images(images, voltage_type='darfield', save_file = False):
      
      #get the dimensions of the images
      height = int(images.shape[0])
      width = int(images.shape[1])
      
      #create an empty array
      avg_array_xy = np.zeros((width, height))
      
      for y in range(height-1):
            for x in range(width-1):                   
                  avg_array_xy[x, y] = average_single_pixel(images, x, y)

      if save_file:
            dirname = os.path.dirname(__file__)
            #remove the slash from the filename
            safe_path = voltage_type[:4] + voltage_type[5:]
            #save values to npy file. to read out the image: avg_image = np.load("avg_array_75kV_10W.npy")
            np.save(f"{dirname}/Numpy image arrays/{voltage_type}/avg_array_{safe_path}.npy", avg_array_xy)

      return avg_array_xy

#def average_average_full_images():

      dirname = os.path.dirname(__file__)
      if (platform.system() == 'Linux' or platform.system() == 'Darwin'): #darwin = macos
            path = os.path.join(dirname, 'Numpy image arrays/')
      else: #windows
            path = os.path.join(dirname, 'Numpy image arrays\\')

       #get the dimensions of the images
      height = int(images.shape[0])
      width = int(images.shape[1])
      
      #create an empty array
      avg_array_xy = np.zeros((width, height))

      for filename in glob.glob(os.path.join(path, '*.npy')): 
            if 'avg' in filename:
                  mean = (np.mean(np.load(filename)))
                  
                  
            


#take all the files within some folder e.g. 75kV/10W/, and for each pixel calculate the variance of the 20 images
#so it outputs a 2D array with each pixel entry being it's variance
def variance_full_images(images, voltage_type='darkfield', save_file = False):

      #get dimension of the images
      height = int(images.shape[0])
      width = int(images.shape[1])

      #create an empty array
      var_array_xy = np.zeros(width, height)

      for y in range(height-1):
            for x in range(width-1):
                  var_array_xy[x, y] = get_variance_single_pixel(images, x, y)
      
      if save_file:
            dirname = os.path.dirname(__file__)
            #remove the slash from the filename
            safe_path = voltage_type[:4] + voltage_type[5:]
            #save values to npy file. to read out the image: avg_image = np.load("avg_array_75kV_10W.npy")
            np.save(f"{dirname}/Numpy image arrays/{voltage_type}/var_array_{safe_path}.npy", var_array_xy)

      return var_array_xy


#take the stack of 20 images and average their values
def average_single_pixel(images, x, y):
      return np.average(images[y,x])
      
def get_variance_single_pixel(images, x, y, average):
      return np.var(images[y,x], mean=average)

#go from an image array to a png image, use exposure to adjust the brightness
def create_image(image, exposure=1, filename='result.png'):
      image = image * exposure
      p = Image.fromarray((image).astype(np.uint16))
      p.save(filename)
      
def create_all_images(): #very long function, do not run if the files are already created!
      for voltage in VOLTAGES:
            for wattage in WATTAGES:
                  path = voltage + "kV" + "/" + wattage + "W" #linux/macos only, but this will only run once anyway
                  images = images_to_array(path)
                  avg = average_full_images(images, path, save_file=True)
                  var = variance_full_images(images, path, save_file=True)
                  # create_image(avg, filename=)
                  
  

# image = images_to_array()
# avg = average_single_pixel(image, 0, 0)
# print(get_variance_single_pixel(image, 0, 0, avg))
# get_variance_single_pixel(average_single_pixel(images_to_array(), 0, 0), 0,0)

# average_single_pixel(images_to_array(), 0, 0)     

