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
# def average_full_images():
#       images = images_to_array()
      
      
      
#       #get the dimensions of the images
#       width = int(images.shape[1])
#       height = int(images.shape[0])
#       print(width, height)
      
#       avg_array_xy = np.zeros(width, height)
#       for y in range(height):
#             for x in range(width):  
#                   avg_array_xy[x, y] = average_single_pixel(images, x, y) 
      
#       # for i in range(20):
#       #       for j in range(20):
#       #             print(len(avg_array_xy[x]), len(avg_array_xy))
#       return avg_array_xy

#take the stack of 20 images and average their values
def average_single_pixel(images, x, y):
      return np.average(images[x,y])
      
      # array_to_average = []
      # for image in images.values():
      #       array_to_average.append(image[x][y])
      # return np.average(array_to_average)
      
def get_variance_single_pixel(images, x, y, average):
      return np.var(images, x, y, mean=average)



# px = average_full_images()
# p = Image.fromarray((px).astype(np.uint8))

# p.save('result.png')