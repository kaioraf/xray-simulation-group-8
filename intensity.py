
import matplotlib.pyplot as plt
from fileIO import *
import random

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
    for i in range(len(intensity_array[0])):
        intensity_array[i, 0] = read_np_image_arrays()[x, y] 

    #insert each intensity entry 
    for voltage in voltages:
        i = voltages.index(voltage)
        for wattage in wattages:
            j = wattages.index(wattage)
            #start wattage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
                intensity_array[i, j + 1] = (read_np_image_arrays(voltage_type=f'{voltage}/{wattage}')[x_mid, y_mid])
            else: # windows
                intensity_array[i, j + 1] = (read_np_image_arrays(voltage_type=f'{voltage}\\{wattage}')[x_mid, y_mid])

    return intensity_array


# outputs a 2D st_dev-of-intensity array for pixel x,y
# first dimension for voltages, second for wattages
def sigma_intensity_array_func(x, y):

    #create an array for pixel x,y
    sigma_intensity_array = np.zeros((5, 5))

    #add dark field sigmas to first wattage entry (for each voltage)
    for i in range(len(sigma_intensity_array[0])):
        sigma_intensity_array[i, 0] = np.sqrt(read_np_image_arrays(dist_type='var')[x, y])
    

    #insert each st_dev-of-intensity entry 
    for voltage in voltages:
        i = voltages.index(voltage)
        for wattage in wattages:
            j = wattages.index(wattage)
            #start wattage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
                sigma_intensity_array[i, j + 1] = np.sqrt((read_np_image_arrays(voltage_type=f'{voltage}/{wattage}', dist_type='var')[x_mid, y_mid]))
            else: # windows
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
    plt.title(f"{x}, {y}")
    for i in range(5):
        plt.errorbar(W, intensity_array[i, :], yerr=sigma_intensity_array[i, :], fmt='-o', markersize=2, capsize=8, label=voltages[i])
        
    plt.xlabel(f'Power P in Watt (W)')
    plt.ylabel(f'Average Intensity I (detector units)')
    plt.legend()
    plt.show()


# similar to last function plot_I_W(x, y)
# but doesnt create one figure for coordinate x, y
# creates n figures for n random coordinates
def n_plots_I_W(n):
    
    # create 2 by n array for coordinates
    coords = np.zeros((n, 2), dtype=int)

    # generate random x-coordinate: multiplying random value between 0 and 1
    # by the length of x-dimension of image
    # same for y-coordinate
    for i in range(n):
        coords[i, 0] = int(read_np_image_arrays().shape[0] * random.random())
        coords[i, 1] = int(read_np_image_arrays().shape[1] * random.random())

    for x, y in coords:
        plot_I_W(x, y)

plot_I_W(x_mid, y_mid)
n_plots_I_W(10)












        
    


