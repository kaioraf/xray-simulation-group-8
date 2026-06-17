
from fileIO import *
import matplotlib.pyplot as plt
import random

# voltages and wattages lists with names in numpy image arrays to extract data
voltages: list = ['30kV', '45kV', '60kV', '75kV', '90kV']
wattages: list = ['10W', '20W', '30W', '40W']


# arrays with actual values of wattages and voltages to plot later on
kV_list: list = [0, 30, 45, 60, 75, 90]
W_list: list = [10, 20, 30, 40]
kV: np.ndarray = np.array(object = kV_list)
W: np.ndarray = np.array(object = W_list)


# find x- and y-coordinate of middle pixel for later use
x_mid: int = read_np_image_arrays().shape[0] // 2
y_mid: int = read_np_image_arrays().shape[1] // 2


# outputs a 2D mean intensity array for pixel x, y
# first dimension for wattages, second for voltages
def intensity_array_func(x, y):

    # create an array for pixel x, y
    intensity_array: np.ndarray = np.zeros((4, 6))

    # add dark field intensity to first voltage entry, for each wattage
    intensity_array[0, 0] = read_np_image_arrays()[x, y]
    intensity_array[1, 0] = read_np_image_arrays()[x, y]
    intensity_array[2, 0] = read_np_image_arrays()[x, y]
    intensity_array[3, 0] = read_np_image_arrays()[x, y]

    # insert each intensity entry
    for wattage in wattages:
        i: int = wattages.index(wattage)

        for voltage in voltages:
            j: int = voltages.index(voltage)

            # start voltage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
                intensity_array[i, j + 1] = read_np_image_arrays(
                    voltage_type = f'{voltage}/{wattage}'
                )[x, y]
            else: # windows
                intensity_array[i, j + 1] = read_np_image_arrays(
                    voltage_type = f'{voltage}\\{wattage}'
                )[x, y]

    return intensity_array


# outputs a 2D st_dev-of-intensity array for pixel x, y
# first dimension for wattages, second for voltages
def sigma_intensity_array_func(x, y):

    # create an array for pixel x, y
    sigma_intensity_array: np.ndarray = np.zeros((4, 6))

    # add dark field sigmas to first voltage entry, for each wattage
    sigma_intensity_array[0, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[1, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[2, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])
    sigma_intensity_array[3, 0] = np.sqrt(read_np_image_arrays(dist_type = 'var')[x, y])

    # insert each st_dev-of-intensity entry
    for wattage in wattages:
        i: int = wattages.index(wattage)

        for voltage in voltages:
            j: int = voltages.index(voltage)

            # start voltage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
                sigma_intensity_array[i, j + 1] = np.sqrt(read_np_image_arrays(
                    voltage_type = f'{voltage}/{wattage}',
                    dist_type = 'var'
                )[x, y])
            else: # windows
                sigma_intensity_array[i, j + 1] = np.sqrt(read_np_image_arrays(
                    voltage_type = f'{voltage}\\{wattage}',
                    dist_type = 'var'
                )[x, y])

    return sigma_intensity_array


# outputs a 2D variance-of-intensity array for pixel x, y
# first dimension for wattages, second for voltages
def variance_intensity_array_func(x, y):

    # create an array for pixel x, y
    variance_intensity_array: np.ndarray = np.zeros((4, 6))

    # add dark field variances to first voltage entry, for each wattage
    variance_intensity_array[0, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[1, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[2, 0] = read_np_image_arrays(dist_type = 'var')[x, y]
    variance_intensity_array[3, 0] = read_np_image_arrays(dist_type = 'var')[x, y]

    # insert each variance-of-intensity entry
    for wattage in wattages:
        i: int = wattages.index(wattage)

        for voltage in voltages:
            j: int = voltages.index(voltage)

            # start voltage entries at entry 1, not 0, since 0 is for dark field
            if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
                variance_intensity_array[i, j + 1] = read_np_image_arrays(
                    voltage_type = f'{voltage}/{wattage}',
                    dist_type = 'var'
                )[x, y]
            else: # windows
                variance_intensity_array[i, j + 1] = read_np_image_arrays(
                    voltage_type = f'{voltage}\\{wattage}',
                    dist_type = 'var'
                )[x, y]

    return variance_intensity_array


# for pixel [x, y], plot intensity entries against voltages
# includes st_dev
def plot_I_kV(x, y):

    # get intensity array and st_dev-of-intensity array of chosen pixel
    intensity_array: np.ndarray = intensity_array_func(x = x, y = y)
    sigma_intensity_array: np.ndarray = sigma_intensity_array_func(x = x, y = y)

    plt.figure()

    for i in range(4):
        plt.errorbar(
            x = kV,
            y = intensity_array[i, :],
            yerr = sigma_intensity_array[i, :],
            fmt = '-o',
            markersize = 2,
            capsize = 8,
            label = wattages[i]
        )
    plt.title(f'x, y = {int(x)}, {int(y)}')
    plt.xlabel(xlabel = r'Voltage $U$ ($kV$)')
    plt.ylabel(ylabel = r'Average Intensity $I$ (detector units)')
    plt.legend()
    plt.show()


# similar to plot_I_kV(x, y)
# but creates n figures for n random coordinates
def ran_plot_I_kV(n):

    # create x and y coordinate arrays
    x_coords: np.ndarray = np.zeros(n)
    y_coords: np.ndarray = np.zeros(n)

    for i in range(n):
        x_coords[i] = int(read_np_image_arrays().shape[0] * random.random())
        y_coords[i] = int(read_np_image_arrays().shape[1] * random.random())

        plot_I_kV(int(x_coords[i]), int(y_coords[i]))


#plot_I_kV(x_mid, y_mid)
#ran_plot_I_kV(n = 5)

# quadratic fit function: I = aU^2 + bU + c
def quadratic_fit(U, a, b, c):
    return a * U**2 + b * U + c


# plot quadratic fits of intensity against voltage for one pixel
def plot_I_kV_quadratic_fit(x, y):

    intensity_array: np.ndarray = intensity_array_func(x = x, y = y)
    sigma_intensity_array: np.ndarray = sigma_intensity_array_func(x = x, y = y)

    plt.figure()

    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    kV_fit: np.ndarray = np.linspace(start = 0, stop = 90, num = 100)

    # use only the real voltage data for fitting, so not the darkfield at 0 kV
    kV_fit_data: np.ndarray = kV[1:]

    for i in range(4):
        I_values: np.ndarray = intensity_array[i, 1:]
        sigma_values: np.ndarray = sigma_intensity_array[i, 1:]

        sigma_values = np.where(sigma_values > 0, sigma_values, np.nan)

        weights: np.ndarray = 1 / sigma_values**2

        S0: float = np.nansum(weights)
        S1: float = np.nansum(weights * kV_fit_data)
        S2: float = np.nansum(weights * kV_fit_data**2)
        S3: float = np.nansum(weights * kV_fit_data**3)
        S4: float = np.nansum(weights * kV_fit_data**4)

        T0: float = np.nansum(weights * I_values)
        T1: float = np.nansum(weights * kV_fit_data * I_values)
        T2: float = np.nansum(weights * kV_fit_data**2 * I_values)

        A: np.ndarray = np.array([
            [S4, S3, S2],
            [S3, S2, S1],
            [S2, S1, S0]
        ])

        B: np.ndarray = np.array([T2, T1, T0])

        a: float
        b: float
        c: float
        a, b, c = np.linalg.pinv(A) @ B

        I_fit: np.ndarray = quadratic_fit(U = kV_fit, a = a, b = b, c = c)

        plt.errorbar(
            x = kV_fit_data,
            y = I_values,
            yerr = sigma_values,
            fmt = 'o',
            color = colors[i],
            ecolor = colors[i],
            markersize = 3,
            capsize = 6,
            label = wattages[i]
        )

        ymin = np.max(I_values)
        ymax = np.min(I_values)
        plt.plot(
            [25, 25], 
            [2000, 10000], 
            'k--'
        )

        plt.plot(kV_fit, I_fit, '-', color = colors[i])

    plt.title(label = f'Pixel ({x}, {y})')
    plt.xlabel(xlabel = r'Voltage $U$ ($kV$)')
    plt.ylabel(ylabel = r'Average Intensity $I$ (detector units)')
    plt.legend()
    plt.show()


# plot quadratic fits of variance against voltage for one pixel
def plot_Var_kV_quadratic_fit(x, y):

    variance_intensity_array: np.ndarray = variance_intensity_array_func(x = x, y = y)

    plt.figure()

    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red']
    kV_fit: np.ndarray = np.linspace(start = 30, stop = 90, num = 100)

    # fit only the real voltage data, not the darkfield point at 0 kV
    kV_fit_data: np.ndarray = kV[1:]

    for i in range(4):
        Var_values: np.ndarray = variance_intensity_array[i, 1:]

        valid: np.ndarray = np.isfinite(Var_values)
        a: float
        b: float
        c: float
        a, b, c = np.polyfit(x = kV_fit_data[valid], y = Var_values[valid], deg = 2)

        Var_fit: np.ndarray = quadratic_fit(U = kV_fit, a = a, b = b, c = c)

        plt.plot(
            kV_fit_data[valid],
            Var_values[valid],
            'o',
            color = colors[i],
            markersize = 3,
            label = wattages[i]
        )

        plt.plot(kV_fit, Var_fit, '-', color = colors[i])

    plt.title(label = f'Pixel ({x}, {y})')
    plt.xlabel(xlabel = r'Voltage $U$ ($kV$)')
    plt.ylabel(ylabel = r'Variance of intensity $\mathrm{Var}(I)$')
    plt.legend()
    plt.show()


# creates n quadratic-fit plots for random pixels
def ran_plot_I_kV_quadratic_fit(n):

    for i in range(n):
        x: int = int(read_np_image_arrays().shape[0] * random.random())
        y: int = int(read_np_image_arrays().shape[1] * random.random())

        print(x, y)
        plot_I_kV_quadratic_fit(x = x, y = y)


# creates n variance-against-voltage quadratic-fit plots for random pixels
def ran_plot_Var_kV_quadratic_fit(n):

    for i in range(n):
        x: int = int(read_np_image_arrays().shape[0] * random.random())
        y: int = int(read_np_image_arrays().shape[1] * random.random())

        print(x, y)
        plot_Var_kV_quadratic_fit(x = x, y = y)


ran_plot_I_kV_quadratic_fit(n = 5)
# ran_plot_I_kV(5)
#ran_plot_Var_kV_quadratic_fit(n = 5)
