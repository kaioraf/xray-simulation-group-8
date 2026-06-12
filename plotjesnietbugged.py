from fileIO import *
from imageAnalysis import *
import matplotlib.pyplot as plt

def pixel_average(voltage_type, x, y):
    return read_np_image_arrays(voltage_type = voltage_type, dist_type = 'avg')[y, x]

# print(pixel_average('75kV\\40W', 500, 40))

def pixel_variance(voltage_type, x, y):
    return read_np_image_arrays(voltage_type = voltage_type, dist_type = 'var')[y, x]

voltages: list = [30, 45, 60, 75, 90]
wattages: list = [10, 20, 30, 40]

pixel_x = 50
pixel_y = 50

# filpath
if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
    slash: str = "/"
else:
    slash: str = "\\"


# plot van gemiddelde pixelwaarde vs wattage voor voltages
def plotje_avg_vs_watt():
    for volt in voltages:
        averagewattages_lst: list = [
            pixel_average(
                voltagetype = str(object = volt) + "kV" + slash + str(object = watt) + "W",
                x = pixel_x,
                y = pixel_y
            ) for watt in wattages
        ]    
        plt.plot(wattages, averagewattages_lst, marker = "o", label = f"{volt} kV")
    
    plt.title(label = "Average pixel value vs wattages for different voltages")
    plt.xlabel(xlabel = "Wattages")
    plt.ylabel(ylabel = "Averages(geen darkfield afgetrokken)")
    plt.legend(["30kV", "45kv", "60kV", "75kV", "90kv"])
    plt.show()

# plot van variantie vs voltage voor verschillende wattages
def plotje_var_vs_volt():
    for watt in wattages:
        variancevoltages_lst: list = [
            pixel_variance(
                voltagetype = str(object = volt) + "kV" + slash + str(object = watt) + "W",
                x = pixel_x,
                y = pixel_y
            ) for volt in voltages
        ]
        plt.plot(voltages, variancevoltages_lst, marker = "o")
    
    plt.legend()
    plt.title(label = "Variance vs voltage for 4 different wattages")
    plt.xlabel(xlabel = "voltage")
    plt.ylabel(ylabel = "variance (darkfield nog niet eraf gehaald)")
    plt.legend(["10W", "20W", "30W", "40W"])
    plt.show()

# plot van variantie vs wattage voor verschillende voltages
def plotje_var_vs_watt():
    for volt in voltages:
        variancewattages_lst: list = [
            pixel_variance(
                voltagetype = str(object = volt) + "kV" + slash + str(object = watt) + "W",
                x = pixel_x,
                y = pixel_y
            ) for watt in wattages
        ]
        plt.plot(wattages, variancewattages_lst, marker = "o")
    
    plt.legend()
    plt.title(label = "Variance vs wattage for 5 different voltages")
    plt.ylabel(ylabel = "variance (darkfield nog niet eraf gehaald)")
    plt.xlabel(xlabel = "wattage")
    plt.legend(["30kV", "45kV", "60kV", "75kV", "90kV"])
    plt.show()

# defs to take the average or variance of a pixel value, with the darkfield one subtracted
def true_pixel_average(voltage_type, x, y):
    return read_np_image_arrays(voltage_type = voltage_type, dist_type = 'avg')[y, x] - read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'avg')[y, x]

def true_pixel_variance(voltage_type, x, y):
    return read_np_image_arrays(voltage_type = voltage_type, dist_type = 'var')[y, x] - read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'var')[y, x]

# plotje van darkfieldgecorrigeerde variantie tegen wattage
def plotje_true_var_vs_watt():
    for volt in voltages:
        variancewattages_lst: list = [
            true_pixel_variance(
                voltage_type = str(object = volt) + "kV" + slash + str(object = watt) + "W",
                x = pixel_x,
                y = pixel_y
            ) for watt in wattages
        ]
        plt.plot(wattages, variancewattages_lst, marker = "o")
    
    plt.legend()
    plt.title(label = "True variance vs wattage for 5 different voltages")
    plt.xlabel(xlabel = "wattage")
    plt.ylabel(ylabel = "variance (darkfield nog niet eraf gehaald)")
    plt.legend(["30kV", "45kV", "60kV", "75kV", "90kV"])
    plt.show()

# plotje van darkfieldgecorrigeerde gemeiddelde tegen wattage
def plotje_true_avg_vs_watt():
    for volt in voltages:
        averagewattages_lst: list = [
            true_pixel_average(
                voltage_type = str(object = volt) + "kV" + slash + str(object = watt) + "W",
                x = pixel_x,
                y = pixel_y
            ) for watt in wattages
        ]
        plt.plot(wattages, averagewattages_lst, marker = "o", label = f"{volt} kV")
    
    plt.title(label = "True average pixel value vs wattages for different voltages")
    plt.xlabel(xlabel = "Wattages")
    plt.ylabel(ylabel = "Averages(geen darkfield afgetrokken)")
    plt.legend(["30kV", "45kv", "60kV", "75kV", "90kv"])
    plt.show()

plotje_true_avg_vs_watt()
