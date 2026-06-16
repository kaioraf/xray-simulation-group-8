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
        full_path: str = f"{dirname}/Final parameter maps/alpha_map.npy"
    else: # windows
        full_path: str = f"{dirname}\\Final parameter maps\\alpha_map.npy"
    alpha_array: np.ndarray = np.load(full_path)

    # import b map for 40W
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Final parameter maps/beta_map.npy"
    else: # windows
        full_path: str = f"{dirname}\\Final parameter maps\\beta_map.npy"
    beta_array: np.ndarray = np.load(full_path)

    # import c map for 40W
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Final parameter maps/gamma_map.npy"
    else: # windows
        full_path: str = f"{dirname}\\Final parameter maps\\gamma_map.npy"
    gamma_array: np.ndarray = np.load(full_path)


    # import darkfield map
    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Numpy image arrays/darkfield/avg_array_darkield.npy"
    else: # windows
        full_path: str = f"{dirname}\\Numpy image arrays\\darkfield\\avg_array_darkield.npy"
    darkfield_array: np.ndarray = np.load(full_path)

    # create function
    I: np.ndarray = darkfield_array + P * (alpha_array * V**2 + beta_array * V + gamma_array)

    return I

def color_map_eind_baas(P, V):
    I: np.ndarray = eind_baas(P, V)

    # ignore nan values
    vmin: float = np.nanpercentile(I, 1)
    vmax: float = np.nanpercentile(I, 99)

    plt.figure()
    plt.imshow(X = I, vmin = vmin, vmax = vmax)
    plt.colorbar(label = 'mean Intensity I')
    plt.title(label = 'mean intensity $I$ color map')
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    plt.show()


def color_map_avg_array(P, V):
    dirname: str = os.path.dirname(__file__)

    if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
        full_path: str = f"{dirname}/Numpy image arrays/{V}kV/{P}W/avg_array_{V}kV{P}W.npy"
    else: # windows
        full_path: str = f"{dirname}\\Numpy image arrays\\{V}kV\\{P}W\\avg_array_{V}kV{P}W.npy"

    avg_array: np.ndarray = np.load(full_path)

    # ignore nan values and scale around the useful intensity range
    vmin: float = np.nanpercentile(avg_array, 1)
    vmax: float = np.nanpercentile(avg_array, 99)

    plt.figure()
    plt.imshow(X = avg_array, vmin = vmin, vmax = vmax)
    plt.colorbar(label = 'mean intensity I')
    plt.title(label = f'Average intensity map for ${V}$ kV, ${P}$ W')
    plt.xlabel(xlabel = f'$y$ (pixel)')
    plt.ylabel(ylabel = f'$x$ (pixel)')
    plt.show()





color_map_eind_baas(P = 40, V = 90)
color_map_avg_array(P = 40, V = 90)
