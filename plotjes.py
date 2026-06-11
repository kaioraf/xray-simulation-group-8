import numpy as np
from fileIO import *
import os, glob
from PIL import Image
from imageAnalysis import *
from fileIO import *
import matplotlib.pyplot as plt

def pixel_average(voltage_type, x, y):
    return average_single_pixel(images_to_array(voltage_type), x, y)

# print(pixel_average('75kV\\40W', 500, 40))

def pixel_variance(voltage_type, x, y):
    return get_variance_single_pixel(images_to_array(voltage_type), x, y)


voltages = [30, 45, 60, 75, 90]
wattages = [10, 20, 30, 40]

pixel_x=600
pixel_y=50

# #plot van gemiddelde pixelwaarde vs wattage voor voltages
for volt in voltages:
    averagewattages_lst=[pixel_average(str(volt)+"kV\\"+str(watt)+"W", pixel_x, pixel_y) for watt in wattages]
    plt.plot(wattages, averagewattages_lst, marker="o", label=f"{volt} kV")
    plt.title("Average pixel value vs wattages for different voltages")
    plt.xlabel("Wattages")
    plt.ylabel("Averages(geen darkfield afgetrokken)")
    plt.legend(["30kV", "45kv", "60kV", "75kV", "90kv"])
plt.show()

# #plot van variantie vs voltage voor verschillende wattages
for watt in wattages:
    variancevoltages_lst=[pixel_variance(str(volt)+"kV\\"+str(watt)+"W", pixel_x, pixel_y) for volt in voltages]
    plt.plot(voltages, variancevoltages_lst, marker="o")
    plt.legend()
    plt.title("Variance vs voltage for 4 different wattages")
    plt.ylabel("variance (darkfield nog niet eraf gehaald)")
    plt.xlabel("voltage")
    plt.legend(["10W", "20W", "30W", "40W"])
plt.show()

#plot van variantie vs wattage voor verschillende voltages
for volt in voltages:
    variancewattages_lst=[pixel_variance(str(volt)+"kV\\"+str(watt)+"W", pixel_x, pixel_y) for watt in wattages]
    plt.plot(wattages, variancewattages_lst, marker="o")
    plt.legend()
    plt.title("Variance vs wattage for 5 different voltages")
    plt.ylabel("variance (darkfield nog niet eraf gehaald)")
    plt.xlabel("wattage")
    plt.legend(["30kV", "45kV", "60kV", "75kV", "90kV"])
plt.show()