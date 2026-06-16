# mean real intensity I_r (without darkfield) is a function of power and potential:
# I_r(P) = a_p * P, and 
# I_r(V) = a * V**2 + b * V
# P and V are independent variables, so 
# I_r(P, V) = I_r(P)I_r(V) = a_p * P * (a * V**2 + b * V)
# Total intensity I = I_r + d_e:
# I = a_p * P * (a * V**2 + b * V) + d_e

import numpy as np
import os, glob
from PIL import Image
import scipy as sp
import platform
import matplotlib.pyplot as plt



# a_p is de lineaire coefficient van power; a, b en c zijn de coefficienten van voltage
def eind_baas(P, V):
    dirname: str = os.path.dirname(__file__)

    # import a_p map for 90kV
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Parameter maps/a_map_90kV.npy"
    else: # windows
        full_path: str = f"{dirname}\\Parameter maps\\a_map_90kV.npy"
    a_p_array: np.ndarray = np.load(full_path)

    # import a map for 40W
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Parameter maps/a_map_40W.npy"
    else: # windows
        full_path: str = f"{dirname}\\Parameter maps\\a_map_40W.npy"
    a_array: np.ndarray = np.load(full_path)

    # import b map for 40W
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Parameter maps/b_map_40W.npy"
    else: # windows
        full_path: str = f"{dirname}\\Parameter maps\\b_map_40W.npy"
    b_array: np.ndarray = np.load(full_path)

    # import c map for 40W
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Parameter maps/c_map_40W.npy"
    else: # windows
        full_path: str = f"{dirname}\\Parameter maps\\c_map_40W.npy"
    c_array: np.ndarray = np.load(full_path)

    # create function
    I: np.ndarray = (1 / 7234) * a_p_array * P * (a_array * V**2 + b_array * V) + c_array

    return I

def color_map_eind_baas(P, V):
    I: np.ndarray = eind_baas(P, V)

    # ignore nan values
    vmin: float = np.nanpercentile(I, 1)
    vmax: float = np.nanpercentile(I, 99)

    plt.subplot(121)
    plt.imshow(X = I, vmin = vmin, vmax = vmax)
    plt.colorbar(label = 'mean Intensity I')
    plt.title(label = 'mean intensity $I$ color map')
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    


def color_map_avg_array_90kV40W():
    dirname: str = os.path.dirname(__file__)

    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Numpy image arrays/90kV/40W/avg_array_90kV40W.npy"
    else: # windows
        full_path: str = f"{dirname}\\Numpy image arrays\\90kV\\40W\\avg_array_90kV40W.npy"

    avg_array: np.ndarray = np.load(full_path)

    # ignore nan values and scale around the useful intensity range
    vmin: float = np.nanpercentile(avg_array, 1)
    vmax: float = np.nanpercentile(avg_array, 99)

    plt.figure()
    plt.imshow(X = avg_array, vmin = vmin, vmax = vmax)
    plt.colorbar(label = 'mean intensity I')
    plt.title(label = r'Average intensity map for $90$ kV, $40$ W')
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    plt.show()


color_map_eind_baas(P = 20, V = 75)
color_map_avg_array_90kV40W()
