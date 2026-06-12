import matplotlib.pyplot as plt
from fileIO import *

# voltages en wattages lists with names in numpy image arrays to extract data
voltages: list = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages: list = ['10W', '20W', '30W', '40W']

# arrays with actual values of wattages and voltages to plot later on
kV_list: list = [30, 45, 60, 75, 90]
W_list: list = [10, 20, 30, 40]
kV: np.ndarray = np.array(object = kV_list, dtype = float)
W: np.ndarray = np.array(object = W_list, dtype = float)

# find x- and y-coordinate of middle pixel for later use
x_mid: int = read_np_image_arrays().shape[0] // 2
y_mid: int = read_np_image_arrays().shape[1] // 2

# filepath
if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
    slash: str = "/"
else:
    slash: str = "\\"


# outputs a 3D mean-intensity stack for one wattage
# first dimension is voltage
# second and third dimensions are image coordinates
def intensity_stack_func(wattage):

    example_image: np.ndarray = read_np_image_arrays(voltage_type = f'30kV' + slash + f'{wattage}')

    x_len: int = example_image.shape[0]
    y_len: int = example_image.shape[1]

    # create stack:
    # entry 0 = 30kV
    # entry 1 = 45kV
    # entry 2 = 60kV
    # entry 3 = 75kV
    # entry 4 = 90kV
    intensity_stack: np.ndarray = np.zeros((5, x_len, y_len))

    # insert each intensity image
    for voltage in voltages:
        i: int = voltages.index(voltage)
        intensity_stack[i, :, :] = read_np_image_arrays(voltage_type = f'{voltage}' + slash + f'{wattage}')

    return intensity_stack


# outputs a 3D standard-deviation stack for one wattage
# first dimension is voltage
# second and third dimensions are image coordinates
def sigma_stack_func(wattage):

    example_var_image: np.ndarray = read_np_image_arrays(
        voltage_type = f'30kV' + slash + f'{wattage}',
        dist_type = 'var'
    )

    x_len: int = example_var_image.shape[0]
    y_len: int = example_var_image.shape[1]

    # create stack:
    # entry 0 = 30kV sigma
    # entry 1 = 45kV sigma
    # entry 2 = 60kV sigma
    # entry 3 = 75kV sigma
    # entry 4 = 90kV sigma
    sigma_stack: np.ndarray = np.zeros((5, x_len, y_len))

    # insert each sigma image
    for voltage in voltages:
        i: int = voltages.index(voltage)

        var_image: np.ndarray = read_np_image_arrays(
            voltage_type = f'{voltage}' + slash + f'{wattage}',
            dist_type = 'var'
        )

        sigma_stack[i, :, :] = np.sqrt(var_image)

    return sigma_stack


# quadratic fit function: I = aU^2 + bU + c
def quadratic_fit(U, a, b, c):
    return a * U**2 + b * U + c


# efficient weighted quadratic fit for all pixels at one wattage
def fit_maps_for_wattage(wattage):

    # I has shape (5, x_len, y_len)
    I: np.ndarray = intensity_stack_func(wattage = wattage)

    # sigma has shape (5, x_len, y_len)
    sigma: np.ndarray = sigma_stack_func(wattage = wattage)

    # avoid division by zero
    # if sigma is greater than zero, it keeps it's value
    # if sigma is zero or negative, it is converted to not a number (nan)
    sigma = np.where(sigma > 0, sigma, np.nan)

    # weighted least squares uses 1 / sigma**2
    weights = 1 / sigma**2

    # reshape kV from shape (5,) to shape (5, 1, 1)
    # this lets kV broadcast over all pixels
    U: np.ndarray = kV[:, np.newaxis, np.newaxis]

    # weighted sums over voltage axis
    # np.nansum takes sum, but ignores values that are not numbers (nan)
    S0: np.ndarray = np.nansum(a = weights, axis = 0)
    S1: np.ndarray = np.nansum(a = weights * U, axis = 0)
    S2: np.ndarray = np.nansum(a = weights * U**2, axis = 0)
    S3: np.ndarray = np.nansum(a = weights * U**3, axis = 0)
    S4: np.ndarray = np.nansum(a = weights * U**4, axis = 0)

    T0: np.ndarray = np.nansum(a = weights * I, axis = 0)
    T1: np.ndarray = np.nansum(a = weights * U * I, axis = 0)
    T2: np.ndarray = np.nansum(a = weights * U**2 * I, axis = 0)

    x_len: int = I.shape[1]
    y_len: int = I.shape[2]

    # normal equation matrix for every pixel
    A: np.ndarray = np.zeros((x_len, y_len, 3, 3))
    B: np.ndarray = np.zeros((x_len, y_len, 3))

    A[:, :, 0, 0] = S4
    A[:, :, 0, 1] = S3
    A[:, :, 0, 2] = S2

    A[:, :, 1, 0] = S3
    A[:, :, 1, 1] = S2
    A[:, :, 1, 2] = S1

    A[:, :, 2, 0] = S2
    A[:, :, 2, 1] = S1
    A[:, :, 2, 2] = S0

    B[:, :, 0] = T2
    B[:, :, 1] = T1
    B[:, :, 2] = T0

    # solve for a, b and c maps
    fit_parameters: np.ndarray = np.matmul(np.linalg.pinv(A), B[:, :, :, np.newaxis])[:, :, :, 0]

    a_map: np.ndarray = fit_parameters[:, :, 0]
    b_map: np.ndarray = fit_parameters[:, :, 1]
    c_map: np.ndarray = fit_parameters[:, :, 2]

    return a_map, b_map, c_map


# fit all pixels for all wattages
def fit_maps_all_wattages():

    example_image: np.ndarray = read_np_image_arrays(voltage_type = '30kV' + slash + '10W')
    x_len: int = example_image.shape[0]
    y_len: int = example_image.shape[1]

    a_maps: np.ndarray = np.zeros((4, x_len, y_len))
    b_maps: np.ndarray = np.zeros((4, x_len, y_len))
    c_maps: np.ndarray = np.zeros((4, x_len, y_len))

    for wattage in wattages:
        i: int = wattages.index(wattage)
        print(f'Fitting {wattage}...')

        a_map: np.ndarray
        b_map: np.ndarray
        c_map: np.ndarray
        a_map, b_map, c_map = fit_maps_for_wattage(wattage = wattage)

        a_maps[i, :, :] = a_map
        b_maps[i, :, :] = b_map
        c_maps[i, :, :] = c_map

    return a_maps, b_maps, c_maps


# plot one fit-parameter image
def plot_fit_map(fit_map, title, colorbar_label):

    # ignore nan values
    vmin: float = np.nanpercentile(fit_map, 1)
    vmax: float = np.nanpercentile(fit_map, 99)

    plt.figure()
    plt.imshow(X = fit_map, vmin = vmin, vmax = vmax)
    plt.colorbar(label = colorbar_label)
    plt.title(label = title)
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    plt.show()


# plot data and fit for one pixel, just for checking
def plot_I_kV_with_numpy_fit(x, y):

    plt.figure()

    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    kV_fit: np.ndarray = np.linspace(start = 30, stop = 90, num = 100)

    for wattage in wattages:
        i: int = wattages.index(wattage)
        color: str = colors[i]

        intensity_stack: np.ndarray = intensity_stack_func(wattage = wattage)
        sigma_stack: np.ndarray = sigma_stack_func(wattage = wattage)

        I_values: np.ndarray = intensity_stack[:, x, y]
        sigma_values: np.ndarray = sigma_stack[:, x, y]

        a_map: np.ndarray
        b_map: np.ndarray
        c_map: np.ndarray
        a_map, b_map, c_map = fit_maps_for_wattage(wattage = wattage)

        a: float = a_map[x, y]
        b: float = b_map[x, y]
        c: float = c_map[x, y]

        I_fit: np.ndarray = quadratic_fit(U = kV_fit, a = a, b = b, c = c)

        plt.errorbar(
            x = kV,
            y = I_values,
            yerr = sigma_values,
            fmt = 'o',
            color = color,
            ecolor = color,
            markersize = 3,
            capsize = 6,
            label = wattage
        )

        plt.plot(kV_fit, I_fit, '-', color = color)

    plt.xlabel(xlabel = r'$U$ (kV)')
    plt.ylabel(ylabel = r'$\overline{I}$ (detector units)')
    plt.legend()
    plt.show()


# run all fits
a_maps: np.ndarray
b_maps: np.ndarray
c_maps: np.ndarray
a_maps, b_maps, c_maps = fit_maps_all_wattages()

# save fit parameter maps
for wattage in wattages:
    i: int = wattages.index(wattage)

    np.save(file = f'a_map_{wattage}.npy', arr = a_maps[i, :, :])
    np.save(file = f'b_map_{wattage}.npy', arr = b_maps[i, :, :])
    np.save(file = f'c_map_{wattage}.npy', arr = c_maps[i, :, :])

# example: plot 10W maps
plot_fit_map(fit_map = a_maps[3, :, :], title = r'Quadratic map $a$ for $40$ W', colorbar_label = r'$a$')
plot_fit_map(fit_map = b_maps[3, :, :], title = r'Linear map $b$ for $40$ W', colorbar_label = r'$b$')
plot_fit_map(fit_map = c_maps[3, :, :], title = r'Constant map $c$ for $40$ W', colorbar_label = r'$c$')

# example: check middle pixel
#plot_I_kV_with_numpy_fit(x = x_mid, y = y_mid)