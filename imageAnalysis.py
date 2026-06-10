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
def average_full_images(path):
      images = images_to_array(path)
      
      #get the dimensions of the images
      height = int(images.shape[0])
      width = int(images.shape[1])
      
      #create an empty array
      avg_array_xy = np.zeros((width, height))
      
      for y in range(height-1):
            for x in range(width-1):                   
                  avg_array_xy[x, y] = average_single_pixel(images, x, y) 
      
#       return avg_array_xy

#take the stack of 20 images and average their values
def average_single_pixel(images, x, y):
      return np.average(images[y,x])
      
def get_variance_single_pixel(images, x, y, average):
      return np.var(images[y,x], mean=average)

#go from an image array to a png image, use exposure to adjust the brightness
def create_image(image, exposure=1):
      image = image * exposure
      p = Image.fromarray((image).astype(np.uint16))
      p.save('result.png')
      
