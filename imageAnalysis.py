#
# Collection of functions to analyse the image arrays, taking their average and their standard deviation, either of an 
# entire layer of images or a single layer of pixels
#

import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

from fileIO import images_to_dict

VOLTAGES = {30, 45, 60, 75, 90} 
WATTAGES = {10, 20, 30, 40}
COUNTS = 20


#take all the files within some folder e.g. 75kV/10W/, and then averages all their values into a single new image
def average_full_images():
      images = images_to_dict()
      
      #get the dimensions of the images
      first_image = next(iter(images))
      width = len(images[first_image])
      height = len(images[first_image][0])
      print(width, height)
      
      #todo: rewrite with list comprehension?
      avg_array_xy = []
      for y in range(height):
            # print(y)
            avg_array_x = []
            for x in range(width):   
                  avg_array_x.append(average_single_pixel(images, x, y))
            avg_array_xy.append(avg_array_x)
      
      # for i in range(20):
      #       for j in range(20):
      #             print(len(avg_array_xy[x]), len(avg_array_xy))
      return avg_array_xy

#take the stack of 20 images and average their values
def average_single_pixel(images, x, y):
      array_to_average = []
      for image in images.values():
            array_to_average.append(image[x][y])
      return np.average(array_to_average)
      
# def get_variance_single_pixel(images, x, y, average):
#       diff = []
#       for image in images.values():
#             diff.append((image[x][y] - average)**2)
#             dataset_deviation.append((i - avg)**2)
#             var = sum(dataset_deviation)/len(dataset)
#             return variance
      

px = average_full_images()
p = Image.fromarray((px).astype(np.uint8))

p.save('result.png')