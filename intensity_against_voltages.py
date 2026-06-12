
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


plot_I_kV(x_mid, y_mid)
ran_plot_I_kV(n = 5)