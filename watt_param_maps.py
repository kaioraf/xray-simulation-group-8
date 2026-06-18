import matplotlib.pyplot as plt
from fileIO import *
import platform
import os, glob
dataset_type = '1000' # of '20' als je de oude wilt doen


# voltages en wattages lists with names in numpy image arrays to extract data
voltages: list = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages: list = ['10W', '20W', '30W', '40W']

# arrays with actual values of wattages and voltages to plot later on
kV_list: list = [30, 45, 60, 75, 90]
W_list: list = [0, 10, 20, 30, 40]
kV: np.ndarray = np.array(object = kV_list)
W: np.ndarray = np.array(object = W_list, dtype = float)

# find x- and y-coordinate of middle pixel for later use
x_mid: int = read_np_image_arrays().shape[0] // 2
y_mid: int = read_np_image_arrays().shape[1] // 2

# filpath
if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
    slash: str = "/"
else:
    slash: str = "\\"

# outputs a 3D mean-intensity stack for one voltage
# first dimension is wattage
# second and third dimensions are image coordinates
def intensity_stack_func(voltage):

    # read dark field image
    dark_image: str = read_np_image_arrays()

    x_len: int = dark_image.shape[0]
    y_len: int = dark_image.shape[1]

    # create stack:
    # entry 0 = dark field, W = 0
    # entry 1 = 10W
    # entry 2 = 20W
    # entry 3 = 30W
    # entry 4 = 40W
    intensity_stack: np.ndarray = np.zeros((5, x_len, y_len))

    # add dark field image to first wattage entry
    intensity_stack[0, :, :] = dark_image

    # insert each intensity image
    for wattage in wattages:
        j: int = wattages.index(wattage)
        intensity_stack[j + 1, :, :] = read_np_image_arrays(voltage_type = f'{voltage}' + slash + f'{wattage}')

    return intensity_stack


# outputs a 3D standard-deviation stack for one voltage
# first dimension is wattage
# second and third dimensions are image coordinates
def sigma_stack_func(voltage):

    # read dark field variance image
    dark_var_image: str = read_np_image_arrays(dist_type = 'var')

    x_len: int = dark_var_image.shape[0]
    y_len: int = dark_var_image.shape[1]

    # create stack:
    # entry 0 = dark field sigma, W = 0
    # entry 1 = 10W sigma
    # entry 2 = 20W sigma
    # entry 3 = 30W sigma
    # entry 4 = 40W sigma
    sigma_stack: np.ndarray = np.zeros((5, x_len, y_len))

    # add dark field sigma to first wattage entry
    sigma_stack[0, :, :] = np.sqrt(dark_var_image)

    # insert each sigma image
    for wattage in wattages:
        j: int = wattages.index(wattage)
        var_image: str = read_np_image_arrays(
            voltage_type = f'{voltage}' + slash + f'{wattage}',
            dist_type = 'var'
        )
        
        sigma_stack[j + 1, :, :] = np.sqrt(var_image)

    return sigma_stack


# linear fit function: I = aP + b
def linear_fit(P, a, b):
    return a * P + b


# efficient weighted linear fit for all pixels at one voltage
def fit_maps_for_voltage(voltage):

    # I has shape (5, x_len, y_len)
    I: np.ndarray = intensity_stack_func(voltage = voltage)

    # sigma has shape (5, x_len, y_len)
    sigma: np.ndarray = sigma_stack_func(voltage = voltage)

    # avoid division by zero
    # if sigma is greater than zero, it keeps it's value
    # if sigma is zero or negative, it is converted to not a number (nan)
    sigma = np.where(sigma > 0, sigma, np.nan)

    # weighted least squares uses 1 / sigma**2
    weights = 1 / sigma**2

    # reshape W from shape (5,) to shape (5, 1, 1)
    # this lets W broadcast over all pixels
    P: np.ndarray = W[:, np.newaxis, np.newaxis]

    # weighted sums over wattage axis
    # np.nansum take sum, but ignores values that are not numbers (nan)
    S: float = np.nansum(a = weights, axis = 0)
    SP: float = np.nansum(a = weights * P, axis = 0)
    SI: float = np.nansum(a = weights * I, axis = 0)
    SPP: float = np.nansum(a = weights * P**2, axis = 0)
    SPI : float = np.nansum(a = weights * P * I, axis = 0)

    denominator: float = S * SPP - SP**2

    # a and b maps
    a_map: float = (S * SPI - SP * SI) / denominator
    b_map: float = (SPP * SI - SP * SPI) / denominator

    return a_map, b_map


# fit all pixels for all voltages
def fit_maps_all_voltages():

    example_image: str = read_np_image_arrays()
    x_len: int = example_image.shape[0]
    y_len: int = example_image.shape[1]

    a_maps: np.ndarray = np.zeros((5, x_len, y_len))
    b_maps: np.ndarray = np.zeros((5, x_len, y_len))

    for voltage in voltages:
        i: int = voltages.index(voltage)
        print(f'Fitting {voltage}...')
        
        a_map: float
        b_map: float
        a_map, b_map = fit_maps_for_voltage(voltage = voltage)

        a_maps[i, :, :] = a_map
        b_maps[i, :, :] = b_map

    return a_maps, b_maps


# plot one fit-parameter image
def plot_fit_map(fit_map, title, colorbar_label):

    # ignore nan values
    vmin: float = np.nanpercentile(fit_map, 1)
    vmax: float = np.nanpercentile(fit_map, 99)

    plt.figure()
    plt.imshow(X = fit_map, vmin = vmin, vmax = vmax)
    plt.colorbar(label = colorbar_label)
    plt.title(label = title)
    plt.xlabel(xlabel = r'$x$ (pixel)')
    plt.ylabel(ylabel = r'$y$ (pixel)')
    plt.show()


# plot data and fit for one pixel, just for checking
def plot_I_W_with_numpy_fit(x, y):

    plt.figure()

    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    W_fit: np.ndarray = np.linspace(start = 0, stop = 40, num = 100)

    for voltage in voltages:
        i: int = voltages.index(voltage)
        color: str = colors[i]

        intensity_stack: np.ndarray = intensity_stack_func(voltage = voltage)
        sigma_stack: np.ndarray = sigma_stack_func(voltage = voltage)

        I_values: np.ndarray = intensity_stack[:, x, y]
        sigma_values: np.ndarray = sigma_stack[:, x, y]
        
        a_map: np.ndarray
        b_map: np.ndarray
        a_map, b_map = fit_maps_for_voltage(voltage = voltage)
        
        a: float = a_map[x, y]
        b: float = b_map[x, y]

        I_fit: np.ndarray = linear_fit(P = W_fit, a = a, b = b)

        plt.errorbar(
            x = W,
            y = I_values,
            yerr = sigma_values,
            fmt = 'o',
            color = color,
            ecolor = color,
            markersize = 3,
            capsize = 6,
            label = voltage
        )

        plt.plot(W_fit, I_fit, '-', color = color)

    plt.xlabel(xlabel = r'$P$ (W)')
    plt.ylabel(ylabel = r'$\overline{I}$ (detector units)')
    plt.legend()
    plt.show()


# run all fits
a_maps: np.ndarray
b_maps: np.ndarray
a_maps, b_maps = fit_maps_all_voltages()

# save fit parameter maps
for voltage in voltages:
    i: int = voltages.index(voltage)

    if (platform.system() == 'Linux' or platform.system() == 'Darwin'):  # darwin = macos
        np.save(file = f'Parameter maps/a_map_{voltage}.npy', arr = a_maps[i, :, :])
    else:  # windows
        np.save(file = f'Parameter maps\\a_map_{voltage}.npy', arr = a_maps[i, :, :])

    if (platform.system() == 'Linux' or platform.system() == 'Darwin'):  # darwin = macos
        np.save(file = f'Parameter maps/b_map_{voltage}.npy', arr = b_maps[i, :, :])
    else:  # windows
        np.save(file = f'Parameter maps\\b_map_{voltage}.npy', arr = b_maps[i, :, :])


     

# example: plot 30kV maps
plot_fit_map(fit_map = a_maps[0, :, :], title = r'Slope map $a$ for $30$ kV', colorbar_label = r'$a$')
plot_fit_map(fit_map = b_maps[0, :, :], title = r'Intercept map $b$ for $30$ kV', colorbar_label = r'$b$')

# example: check middle pixel
plot_I_W_with_numpy_fit(x = x_mid, y = y_mid)
