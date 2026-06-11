import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform
import matplotlib.pyplot as plt

from fileIO import *

voltages = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages = ['10W', '20W', '30W', '40W']


#def read_np_image_arrays(voltage_type = 'darkfield', filetype = 'npy', dist_type = 'avg'):

x_mid = read_np_image_arrays().shape[0] // 2
y_mid = read_np_image_arrays().shape[1] // 2




def intensity_list_func(x, y):

    #create a array for pixel x,y: first entry for voltages, second entry for wattages
    intensity_array = np.zeros((5, 5))

    #add dark field intensity to first wattage entry (for each voltage)
    intensity_array[0, 0] = read_np_image_arrays()[x, y] 
    intensity_array[1, 0] = read_np_image_arrays()[x, y] 
    intensity_array[2, 0] = read_np_image_arrays()[x, y] 
    intensity_array[3, 0] = read_np_image_arrays()[x, y] 
    intensity_array[4, 0] = read_np_image_arrays()[x, y]

    #insert each intensity entry 
    for voltage in voltages:
        i = voltages.index(voltage)
        for wattage in wattages:
            j = wattages.index(wattage)
            #start wattage entries at entry 1, not 0, since 0 is for dark field
            intensity_array[i, j + 1] = (read_np_image_arrays(voltage_type=f'{voltage}\\{wattage}')[x_mid, y_mid])

    return intensity_array

#print(intensity_list_func(x_mid, y_mid))


#plot intensity entries against wattages, 5 times, one for each voltage. first with middle pixel
plt.imshow(intensity_list_func(x_mid, y_mid))
plt.colorbar()
plt.show()










#intensity_list_30kV = []
#for filename in  glob.glob(os.path.join(path, '30kV')):
#    if 'dark' in filename:
#        array = np.load(filename)
#        intensity_list_30kV.append()

        
    


