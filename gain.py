from fileIO import read_np_image_arrays
import matplotlib.pyplot as plt
import numpy as np

# Available settings
voltages = [30, 45, 60, 75, 90]
wattages = [10, 20, 30, 40]

pixel_x = 0
pixel_y=0

# Calculate gain for single pixels
# ------------------------------------------------------------------------------------------
def gain(images_avg, images_var, pixel_x, pixel_y):
    # grab avg intensity and var intensity from array of chosen pixel
    y = images_avg[pixel_x, pixel_y]
    var_y = images_var[pixel_x, pixel_y]

    # Load darkfield images once
    dark_images_avg = read_np_image_arrays(dist_type='avg')
    dark_images_var = read_np_image_arrays(dist_type='var')
    # Calculate darkfield mean intensity and variance
    d_e = dark_images_avg[pixel_x, pixel_y]
    var_de = dark_images_var[pixel_x, pixel_y]

    # Avoid division by zero
    if y == d_e:
        raise ValueError("Cannot calculate gain because y and d_e are equal.")

    gain_value = (var_y - var_de) / (y - d_e)
    # print(gain_value)
    return gain_value

#make directory to save gain per setting
gain_by_voltage = {}

#loop over all settings
for voltage in voltages:
    gain_lst = []

    for watt in wattages:
        folder = f"{voltage}kV\\{watt}W"
        images_avg = read_np_image_arrays(voltage_type=folder, dist_type='avg')
        images_var = read_np_image_arrays(voltage_type=folder, dist_type='var')

        gain_value = gain(images_avg, images_var, pixel_x, pixel_y)
        gain_lst.append(gain_value)

        print(f"{voltage} kV, {watt} W: gain = {gain_value}")

    gain_by_voltage[voltage] = gain_lst
# --------------------------------------------------------------------------------------------

# Plot wattage against gain for every constant voltage
for voltage, gains in gain_by_voltage.items():
    plt.plot(wattages, gains, marker="o", label=f"{voltage} kV")

plt.xlabel("Wattage (W)")
plt.ylabel("Gain")
plt.title(f"Gain vs Wattage for Different Voltages, PIXEL({pixel_x},{pixel_y})")
plt.legend()
plt.grid(True, which="both")
plt.show()
# plt.savefig(f"gain pixel({pixel_x}, {pixel_y}).png")


# Calculate gain with the average values of entire image (avg avg and avg var)- !!!not in use!!!
# --------------------------------------------------------------------------------------
# def gain(images_avg, images_var, avg_dark, var_dark):
#     # Calculate mean intensity and variance for full image
#     y = np.mean(images_avg)
#     var_y = np.mean(images_var)

#     # Calculate darkfield mean intensity and variance for full image
#     d_e = np.mean(avg_dark)
#     var_de = np.mean(var_dark)

#     # Avoid division by zero
#     if y == d_e:
#         raise ValueError("Cannot calculate gain because y and d_e are equal.")

#     gain_value = (var_y - var_de) / (y - d_e)
#     # print(gain_value)
#     return gain_value

# # Load darkfield arrays once, because they do not change with voltage or wattage
# avg_dark = read_np_image_arrays(dist_type='avg')
# var_dark = read_np_image_arrays(dist_type='var')

# # Store gain values for each voltage (dictionary)
# gain_by_voltage = {}

#all settings
# VOLTAGES = ["30", "45", "60", "75", "90"]
# WATTAGES = ["10", "20", "30", "40"]


# #runs through all voltages and wattages to calculate gain for each setting
# for voltage in VOLTAGES:
#     gain_lst = []
#     for watt in WATTAGES:
#         folder = f"{voltage}kV\\{watt}W"
#         images_avg = read_np_image_arrays(voltage_type=folder, dist_type='avg')
#         images_var = read_np_image_arrays(voltage_type=folder, dist_type='var')
#         gain_value = gain(images_avg, images_var, avg_dark, var_dark)
#         gain_lst.append(gain_value)

#         print(f"{voltage} kV, {watt} W: gain = {gain_value}")

#     gain_by_voltage[voltage] = gain_lst
# ------------------------------------------------------------------------------------------------