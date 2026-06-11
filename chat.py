
import matplotlib.pyplot as plt
from fileIO import *

# voltages en wattages lists with names in numpy image arrays to extract data
voltages = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages = ['10W', '20W', '30W', '40W']

# arrays with actual values of wattages and voltages to plot later on
kV_list = [30, 45, 60, 75, 90]
kV = np.array(kV_list)

W_list = [0, 10, 20, 30, 40]
W = np.array(W_list, dtype=float)

# find x- and y-coordinate of middle pixel for later use
x_mid = read_np_image_arrays().shape[0] // 2
y_mid = read_np_image_arrays().shape[1] // 2


# outputs a 3D mean-intensity stack for one voltage
# first dimension is wattage
# second and third dimensions are image coordinates
def intensity_stack_func(voltage):

    # read dark field image
    dark_image = read_np_image_arrays()

    x_len = dark_image.shape[0]
    y_len = dark_image.shape[1]

    # create stack:
    # entry 0 = dark field, W = 0
    # entry 1 = 10W
    # entry 2 = 20W
    # entry 3 = 30W
    # entry 4 = 40W
    intensity_stack = np.zeros((5, x_len, y_len))

    # add dark field image to first wattage entry
    intensity_stack[0, :, :] = dark_image

    # insert each intensity image
    for wattage in wattages:
        j = wattages.index(wattage)

        intensity_stack[j + 1, :, :] = read_np_image_arrays(
            voltage_type=f'{voltage}\\{wattage}'
        )

    return intensity_stack


# outputs a 3D standard-deviation stack for one voltage
# first dimension is wattage
# second and third dimensions are image coordinates
def sigma_stack_func(voltage):

    # read dark field variance image
    dark_var_image = read_np_image_arrays(dist_type='var')

    x_len = dark_var_image.shape[0]
    y_len = dark_var_image.shape[1]

    # create stack:
    # entry 0 = dark field sigma, W = 0
    # entry 1 = 10W sigma
    # entry 2 = 20W sigma
    # entry 3 = 30W sigma
    # entry 4 = 40W sigma
    sigma_stack = np.zeros((5, x_len, y_len))

    # add dark field sigma to first wattage entry
    sigma_stack[0, :, :] = np.sqrt(dark_var_image)

    # insert each sigma image
    for wattage in wattages:
        j = wattages.index(wattage)

        var_image = read_np_image_arrays(
            voltage_type=f'{voltage}\\{wattage}',
            dist_type='var'
        )

        sigma_stack[j + 1, :, :] = np.sqrt(var_image)

    return sigma_stack


# linear fit function: I = aP + b
def linear_fit(P, a, b):
    return a * P + b


# efficient weighted linear fit for all pixels at one voltage
def fit_maps_for_voltage(voltage):

    # I has shape: (5, x_len, y_len)
    I = intensity_stack_func(voltage)

    # sigma has shape: (5, x_len, y_len)
    sigma = sigma_stack_func(voltage)

    # avoid division by zero
    #if sigma is greater than zero, it keeps it's value
    #if sigma is zero or negative, it is converted to not a number (nan)
    sigma = np.where(sigma > 0, sigma, np.nan)

    # weighted least squares uses 1/sigma^2
    weights = 1 / sigma**2

    # reshape W from shape (5,) to shape (5, 1, 1)
    # this lets W broadcast over all pixels
    P = W[:, np.newaxis, np.newaxis]

    # weighted sums over wattage axis
    #np.nansum take sum, but ignores values that are not numbers (nan)
    S = np.nansum(weights, axis=0)
    SP = np.nansum(weights * P, axis=0)
    SI = np.nansum(weights * I, axis=0)
    SPP = np.nansum(weights * P**2, axis=0)
    SPI = np.nansum(weights * P * I, axis=0)

    denominator = S * SPP - SP**2

    # a and b maps
    a_map = (S * SPI - SP * SI) / denominator
    b_map = (SPP * SI - SP * SPI) / denominator

    return a_map, b_map


# fit all pixels for all voltages
def fit_maps_all_voltages():

    example_image = read_np_image_arrays()
    x_len = example_image.shape[0]
    y_len = example_image.shape[1]

    a_maps = np.zeros((5, x_len, y_len))
    b_maps = np.zeros((5, x_len, y_len))

    for voltage in voltages:
        i = voltages.index(voltage)

        print(f'Fitting {voltage}...')

        a_map, b_map = fit_maps_for_voltage(voltage)

        a_maps[i, :, :] = a_map
        b_maps[i, :, :] = b_map

    return a_maps, b_maps


# plot one fit-parameter image
def plot_fit_map(fit_map, title, colorbar_label):

    plt.figure()
    plt.imshow(fit_map)
    plt.colorbar(label=colorbar_label)
    plt.title(title)
    plt.xlabel('y pixel')
    plt.ylabel('x pixel')
    plt.show()


# plot data and fit for one pixel, just for checking
def plot_I_W_with_numpy_fit(x, y):

    plt.figure()

    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    W_fit = np.linspace(0, 40, 100)

    for voltage in voltages:
        i = voltages.index(voltage)
        color = colors[i]

        intensity_stack = intensity_stack_func(voltage)
        sigma_stack = sigma_stack_func(voltage)

        I_values = intensity_stack[:, x, y]
        sigma_values = sigma_stack[:, x, y]

        a_map, b_map = fit_maps_for_voltage(voltage)

        a = a_map[x, y]
        b = b_map[x, y]

        I_fit = linear_fit(W_fit, a, b)

        plt.errorbar(
            W,
            I_values,
            yerr=sigma_values,
            fmt='o',
            color=color,
            ecolor=color,
            markersize=3,
            capsize=6,
            label=voltage
        )

        plt.plot(
            W_fit,
            I_fit,
            '-',
            color=color
        )

    plt.xlabel('Power P in Watt (W)')
    plt.ylabel('Average Intensity I (detector units)')
    plt.legend()
    plt.show()


# run all fits
a_maps, b_maps = fit_maps_all_voltages()

# save fit parameter maps
for voltage in voltages:
    i = voltages.index(voltage)

    np.save(f'a_map_{voltage}.npy', a_maps[i, :, :])
    np.save(f'b_map_{voltage}.npy', b_maps[i, :, :])

# example: plot 30kV maps
plot_fit_map(a_maps[0, :, :], 'Slope map a for 30kV', 'a')
plot_fit_map(b_maps[0, :, :], 'Intercept map b for 30kV', 'b')

# example: check middle pixel
plot_I_W_with_numpy_fit(x_mid, y_mid)