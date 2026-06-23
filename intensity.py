# plots and fits single-pixel mean intensity and variance against tube power.
# this is mostly for visual pruposes: to see how fits behave for a single pixel
from fileIO import *
import matplotlib.pyplot as plt
import random

# voltages en wattages lists with names in numpy image arrays to extract data
voltages: list = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages: list = ['10W', '20W', '30W', '40W']


# arrays with actual values of wattages and voltages to plot later on
kV_list: list = [30, 45, 60, 75, 90]
W_list: list = [0, 10, 20, 30, 40]
kV: np.ndarray = np.array(object = kV_list)
W: np.ndarray = np.array(object = W_list)


# find x- and y-coordinate of middle pixel for later use
x_mid: int = read_np_image_arrays().shape[0] // 2
y_mid: int = read_np_image_arrays().shape[1] // 2

# outputs a 2D (mean) intensity array for pixel x, y
# first dimension for voltages, second for wattages
def intensity_array_func(x, y):
    
    # create an array for pixel x, y
    intensity_array: np.ndarray = np.zeros((5, 5))

    # add dark field intensity to first wattage entry (for each voltage)
    intensity_array[0, 0] = read_np_image_arrays()[x, y]
    intensity_array[1, 0] = read_np_image_arrays()[x, y]
    intensity_array[2, 0] = read_np_image_arrays()[x, y]
    intensity_array[3, 0] = read_np_image_arrays()[x, y]
    intensity_array[4, 0] = read_np_image_arrays()[x, y]
    
    # insert each intensity entry 
    for voltage in voltages:
        i: int = voltages.index(voltage)
        for wattage in wattages:
            j: int = wattages.index(wattage)
            # start wattage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
                intensity_array[i, j + 1] = (read_np_image_arrays(voltage_type = f'{voltage}/{wattage}')[x, y])
            else: #windows
                intensity_array[i, j + 1] = (read_np_image_arrays(voltage_type = f'{voltage}\\{wattage}')[x, y])

    return intensity_array


# outputs a 2D st_dev-of-intensity array for pixel x, y
# first dimension for voltages, second for wattages
def sigma_intensity_array_func(x, y):

    # create an array for pixel x, y
    sigma_intensity_array: np.ndarray = np.zeros((5, 5))

    # add dark field sigmas to first wattage entry (for each voltage)
    sigma_intensity_array[0, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[1, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[2, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[3, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[4, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    
    #insert each st_dev-of-intensity entry 
    for voltage in voltages:
        i: int = voltages.index(voltage)
        for wattage in wattages:
            j: int = wattages.index(wattage)
            # start wattage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
                sigma_intensity_array[i, j + 1] = np.sqrt((read_np_image_arrays(voltage_type = f'{voltage}/{wattage}', dist_type = 'var')[x, y]))
            else:
                sigma_intensity_array[i, j + 1] = np.sqrt((read_np_image_arrays(voltage_type = f'{voltage}\\{wattage}', dist_type = 'var')[x, y]))

    return sigma_intensity_array


# outputs a 2D variance-of-intensity array for pixel x, y
# first dimension for voltages, second for wattages
def variance_intensity_array_func(x, y):

    # create an array for pixel x, y
    variance_intensity_array: np.ndarray = np.zeros((5, 5))

    # add dark field variances to first wattage entry (for each voltage)
    variance_intensity_array[0, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[1, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[2, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[3, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[4, 0] = read_np_image_arrays(dist_type = 'var')[x, y]

    # insert each variance-of-intensity entry
    for voltage in voltages:
        i: int = voltages.index(voltage)
        for wattage in wattages:
            j: int = wattages.index(wattage)
            # start wattage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
                variance_intensity_array[i, j + 1] = read_np_image_arrays(
                    voltage_type = f'{voltage}/{wattage}',
                    dist_type = 'var'
                )[x, y]
            else:
                variance_intensity_array[i, j + 1] = read_np_image_arrays(
                    voltage_type = f'{voltage}\\{wattage}',
                    dist_type = 'var'
                )[x, y]

    return variance_intensity_array

# print(intensity_array_func(x = x_mid, y = y_mid))

# color map voor intensity, wattages op x-as, voltages op y-as
# plt.imshow(X = intensity_array_func(x = x_mid, y = y_mid))
# plt.colorbar()
# plt.show()

# for pixel [x,y], plot intensity entries against wattages, 5 times, one for each voltage
# includes st_dev
def plot_I_W(x, y):

    # get intensity array and st_dev-of-intensity array of chosen pixel
    intensity_array: np.ndarray = intensity_array_func(x = x, y = y)
    sigma_intensity_array: np.ndarray = sigma_intensity_array_func(x = x, y = y)

    plt.figure()

    for i in range(5):
        plt.errorbar(
            x = W,
            y = intensity_array[i, :],
            yerr = sigma_intensity_array[i, :],
            fmt = '--',
            markersize = 2,
            capsize = 8,
            label = voltages[i]
        )
    plt.title(f'PIXEL = {int(x)}, {int(y)}')    
    plt.xlabel(xlabel = r'Power $P$ ($W$)')
    plt.ylabel(ylabel = r'Average Intensity $I$ (detector units)')
    plt.legend()
    plt.show()


# similar to last function plot_I_W(x, y)
# but does not create one figure for coordinates (x, y)
# inestead, creates n figures for n random coordinates
def ran_plot_I_W(n):
    
    # create 2 * n array for coordinates
    x_coords: np.ndarray = np.zeros(n)
    y_coords: np.ndarray = np.zeros(n)
    for i in range(n):
        x_coords[i] = int(read_np_image_arrays().shape[0] * random.random())
        y_coords[i] = int(read_np_image_arrays().shape[1] * random.random())
        print(int(x_coords[i]))
        plot_I_W(int(x_coords[i]), int( y_coords[i]))
    
        


    # generate random x-coordinate: multiplying random value between 0 and 1
    # by the length of x-dimension of image
    # same for y-coordinate
    #for i in range(n):
    #    coords[i, 0] = int(read_np_image_arrays().shape[0] * random.random())
    #    coords[i, 1] = int(read_np_image_arrays().shape[1] * random.random())
    x_coords

    #for x, y in coords:
    #    plot_I_W(x, y)


# linear fit function: I = aP + b
def linear_fit(P, a, b):
    return a * P + b


# plot linear fits of intensity against power for one pixel
def plot_I_W_linear_fit(x, y):

    intensity_array: np.ndarray = intensity_array_func(x = x, y = y)
    sigma_intensity_array: np.ndarray = sigma_intensity_array_func(x = x, y = y)

    plt.figure()

    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    W_fit: np.ndarray = np.linspace(start = 0, stop = 40, num = 100)

    for i in range(5):
        I_values: np.ndarray = intensity_array[i, :]
        sigma_values: np.ndarray = sigma_intensity_array[i, :]

        sigma_values = np.where(sigma_values > 0, sigma_values, np.nan)

        weights: np.ndarray = 1 / sigma_values**2

        S: float = np.nansum(weights)
        SP: float = np.nansum(weights * W)
        SI: float = np.nansum(weights * I_values)
        SPP: float = np.nansum(weights * W**2)
        SPI: float = np.nansum(weights * W * I_values)

        denominator: float = S * SPP - SP**2

        a: float = (S * SPI - SP * SI) / denominator
        b: float = (SPP * SI - SP * SPI) / denominator

        I_fit: np.ndarray = linear_fit(P = W_fit, a = a, b = b)

        plt.errorbar(
            x = W,
            y = I_values,
            yerr = sigma_values,
            fmt = 'o',
            color = colors[i],
            ecolor = colors[i],
            markersize = 3,
            capsize = 6,
            label = voltages[i]
        )

        plt.plot(W_fit, I_fit, '-', color = colors[i])

    plt.title(label = f'Pixel ({x}, {y})')
    plt.xlabel(xlabel = r'Power $P$ ($W$)')
    plt.ylabel(ylabel = r'Average Intensity $I$ (detector units)')
    plt.legend()
    plt.show()


# plot linear fits of variance against power for one pixel
def plot_Var_W_linear_fit(x, y):

    variance_intensity_array: np.ndarray = variance_intensity_array_func(x = x, y = y)

    plt.figure()

    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']
    W_fit: np.ndarray = np.linspace(start = 0, stop = 40, num = 100)

    for i in range(5):
        Var_values: np.ndarray = variance_intensity_array[i, :]

        valid: np.ndarray = np.isfinite(Var_values)
        a: float
        b: float
        a, b = np.polyfit(x = W[valid], y = Var_values[valid], deg = 1)

        Var_fit: np.ndarray = linear_fit(P = W_fit, a = a, b = b)

        plt.plot(
            W[valid],
            Var_values[valid],
            'o',
            color = colors[i],
            markersize = 3,
            label = voltages[i]
        )

        plt.plot(W_fit, Var_fit, '-', color = colors[i])

    plt.title(label = f'Pixel ({x}, {y})')
    plt.xlabel(xlabel = r'Power $P$ ($W$)')
    plt.ylabel(ylabel = r'Variance of intensity $\mathrm{Var}(I)$')
    plt.legend()
    plt.show()


# creates n linear-fit plots for random pixels
def ran_plot_I_W_linear_fit(n):

    for i in range(n):
        x: int = int(read_np_image_arrays().shape[0] * random.random())
        y: int = int(read_np_image_arrays().shape[1] * random.random())

        print(x, y)
        plot_I_W_linear_fit(x = x, y = y)


# creates n variance-against-power linear-fit plots for random pixels
def ran_plot_Var_W_linear_fit(n):

    for i in range(n):
        x: int = int(read_np_image_arrays().shape[0] * random.random())
        y: int = int(read_np_image_arrays().shape[1] * random.random())

        print(x, y)
        plot_Var_W_linear_fit(x = x, y = y)


ran_plot_I_W_linear_fit(n = 5)
#ran_plot_Var_W_linear_fit(n = 5)
ran_plot_I_W(5)
