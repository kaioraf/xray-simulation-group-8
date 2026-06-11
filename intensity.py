import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform
import matplotlib.pyplot as plt
from lmfit import models

from fileIO import *

#voltages en wattages lists with names in numpy image arrays to extract data
voltages = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages = ['10W', '20W', '30W', '40W']


#arrays with actual values of wattages and voltages to plot later on
kV_list = [30, 45, 60, 75, 90]
kV = np.array(kV_list)
W_list = [0, 10, 20, 30, 40]
W = np.array(W_list)


#find x- and y-coordinate of middle pixel for later use
x_mid = read_np_image_arrays().shape[0] // 2
y_mid = read_np_image_arrays().shape[1] // 2


# outputs a 2D (mean) intensity array for pixel x,y
# first dimension for voltages, second for wattages
def intensity_array_func(x, y):

    #create an array for pixel x,y
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


# outputs a 2D st_dev-of-intensity array for pixel x,y
# first dimension for voltages, second for wattages
def sigma_intensity_array_func(x, y):

    #create an array for pixel x,y
    sigma_intensity_array = np.zeros((5, 5))

    #add dark field sigmas to first wattage entry (for each voltage)
    sigma_intensity_array[0, 0] = np.sqrt(read_np_image_arrays(dist_type='var')[x, y])
    sigma_intensity_array[1, 0] = np.sqrt(read_np_image_arrays(dist_type='var')[x, y])
    sigma_intensity_array[2, 0] = np.sqrt(read_np_image_arrays(dist_type='var')[x, y])
    sigma_intensity_array[3, 0] = np.sqrt(read_np_image_arrays(dist_type='var')[x, y])
    sigma_intensity_array[4, 0] = np.sqrt(read_np_image_arrays(dist_type='var')[x, y])
    

    #insert each st_dev-of-intensity entry 
    for voltage in voltages:
        i = voltages.index(voltage)
        for wattage in wattages:
            j = wattages.index(wattage)
            #start wattage entries at entry 1, not 0, since 0 is for dark field
            sigma_intensity_array[i, j + 1] = np.sqrt((read_np_image_arrays(voltage_type=f'{voltage}\\{wattage}', dist_type='var')[x_mid, y_mid]))

    return sigma_intensity_array

#print(intensity_list_func(x_mid, y_mid))

#color map voor intensity, wattages op x-as, voltages op y-as
#plt.imshow(intensity_list_func(x_mid, y_mid))
#plt.colorbar()
#plt.show()


#for pixel [x,y], plot intensity entries against wattages, 5 times, one for each voltage
#includes st_dev
def plot_I_W(x, y):

    #get intensity array and st_dev-of-intensity array of chosen pixel
    intensity_array = intensity_array_func(x, y)
    sigma_intensity_array = sigma_intensity_array_func(x, y)

    plt.figure()

    for i in range(5):
        plt.errorbar(W, intensity_array[i, :], yerr=sigma_intensity_array[i, :], fmt='-o', markersize=2, capsize=8, label=voltages[i])
        
    plt.xlabel(f'Power P in Watt (W)')
    plt.ylabel(f'Average Intensity I (detector units)')
    plt.legend()
    plt.show()


#plot_I_W(x_mid, y_mid)


#create linear fit model
def linear_fit(P, a, b):
    return a * P + b
    
model_I_W = models.Model(linear_fit)

# makes linear fit for pixel x,y
def fit_I_W_lmfit(x, y):

    intensity_array = intensity_array_func(x, y)
    sigma_intensity_array = sigma_intensity_array_func(x, y)
    fit_results = fit_I_W_lmfit(x, y)

    plt.figure()

    W_fit = np.linspace(0, 40, 100)

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

    for i in range(5):

        color = colors[i]

        # fitted parameters
        a = fit_results[i].params['a'].value
        b = fit_results[i].params['b'].value

        # fitted line
        I_fit = linear_fit(W_fit, a, b)

        plt.plot(
            W_fit,
            I_fit,
            '-',
            color=color,
            label=f'{voltages[i]} fit'
        )

        # measured data with errorbars
        plt.errorbar(
            W,
            intensity_array[i, :],
            yerr=sigma_intensity_array[i, :],
            fmt='o',
            color=color,
            ecolor=color,
            markersize=3,
            capsize=6,
            label=voltages[i]
        )

    plt.xlabel('Power P in Watt (W)')
    plt.ylabel('Average Intensity I (detector units)')
    plt.legend()
    plt.show()


# print fit reports for pixel x,y
def print_fit_reports(x, y):

    fit_results = fit_I_W_lmfit(x, y)

    for i in range(5):
        print()
        print(f"Fit report for {voltages[i]}")
        print(fit_results[i].fit_report())


# run for middle pixel
fit_I_W_lmfit(x_mid, y_mid)
print_fit_reports(x_mid, y_mid)







        
    


