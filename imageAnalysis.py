import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

from fileIO import image_to_dict

VOLTAGES = {30, 45, 60, 75, 90} 
WATTAGES = {10, 20, 30, 40}
COUNTS = 20


#take all the files within some folder e.g. 75kV/10W/, and then averages all their values into a single new image
def average_images():
      images = image_to_dict()
      
      #get the dimensions of the images
      first_image = next(iter(images))
      width = len(images[first_image])
      height = len(images[first_image][0])
      
      #todo: rewrite with list comprehension?
      avg_array_xy = []
      for y in range(height):
            print(y)
            avg_array_x = []
            for x in range(width):   
                  avg_array_x.append(average_single_pixel(images, x, y))
            avg_array_xy.append(avg_array_x)
            
      return avg_array_xy

#take the stack of 20 images and average their values
def average_single_pixel(images, x, y):
      array_to_be_averaged = []
      for image in images.values():
            array_to_be_averaged.append(image[x][y])
      return np.average(array_to_be_averaged)
      
average_images()