from imageAnalysis import average_single_pixel, get_variance_single_pixel, average_full_images, variance_full_images
from fileIO import images_to_array
import matplotlib.pyplot as plt
import numpy as np
import os 

# Available settings
voltages = [30, 45, 60, 75, 90]
wattages = [10, 20, 30, 40]

VOLTAGES = ["30", "45", "60", "75", "90"]
WATTAGES = ["10", "20", "30", "40"]

pixel_x = 750
pixel_y=1000

# Calculate gain for single pixels
# ------------------------------------------------------------------------------------------
def gain(images, pixel_x, pixel_y):
    # Calculate mean intensity and variance for selected pixel
    y = average_single_pixel(images, pixel_x, pixel_y)
    var_y = get_variance_single_pixel(images, pixel_x, pixel_y)

    # Load darkfield images once
    dark_images = images_to_array(voltage_type="darkfield")

    # Calculate darkfield mean intensity and variance
    d_e = average_single_pixel(dark_images, pixel_x, pixel_y)
    var_de = get_variance_single_pixel(dark_images, pixel_x, pixel_y)

    # Avoid division by zero
    if y == d_e:
        raise ValueError("Cannot calculate gain because y and d_e are equal.")

    gain_value = (var_y - var_de) / (y - d_e)
    # print(gain_value)
    return gain_value

gain_by_voltage = {}

for voltage in voltages:
    gain_lst = []

    for watt in wattages:
        folder = f"{voltage}kV\\{watt}W"
        images = images_to_array(voltage_type=folder)

        gain_value = gain(images, pixel_x, pixel_y)
        gain_lst.append(gain_value)

        # print(f"{voltage} kV, {watt} W: gain = {gain_value}")

    gain_by_voltage[voltage] = gain_lst
# --------------------------------------------------------------------------------------------

# Calculate gain with the average values of entire image (avg avg and avg var)
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
# dirname = os.path.dirname(__file__)
# array_dir = os.path.join(dirname, "Numpy image arrays")

# darkfield_avg_path = os.path.join(
#     array_dir,
#     "darkfield",
#     "avg_array_darkield.npy"
# )

# darkfield_var_path = os.path.join(
#     array_dir,
#     "darkfield",
#     "var_array_darkield.npy"
# )

# avg_dark = np.load(darkfield_avg_path)
# var_dark = np.load(darkfield_var_path)

# # Store gain values for each voltage (dictionary)
# gain_by_voltage = {}

# for voltage in VOLTAGES:
#     gain_lst = []
#     for watt in WATTAGES:
#         path = voltage + "kV" + "\\" + watt + "W" 
#         dirname = os.path.dirname(__file__)
#         safe_path = path[:4] + path[5:]
#         full_path = f"{dirname}\\Numpy image arrays\\{path}\\avg_array_{safe_path}.npy"
#         full_path_var = f"{dirname}\\Numpy image arrays\\{path}\\var_array_{safe_path}.npy"
#         images_avg = np.load(full_path)
#         images_var = np.load(full_path_var)
#         gain_value = gain(images_avg, images_var, avg_dark, var_dark)
#         gain_lst.append(gain_value)

#         print(f"{voltage} kV, {watt} W: gain = {gain_value}")

#     gain_by_voltage[voltage] = gain_lst
# ------------------------------------------------------------------------------------------------

# Plot wattage against gain for every constant voltage
for voltage, gains in gain_by_voltage.items():
    plt.plot(wattages, gains, marker="o", label=f"{voltage} kV")

plt.xlabel("Wattage (W)")
plt.ylabel("Gain")
plt.title(f"Gain vs Wattage for Different Voltages, PIXEL({pixel_x},{pixel_y})")
plt.legend()
plt.grid(True, which="both")
plt.savefig(f"gain pixel({pixel_x}, {pixel_y}).png")
    

# RESULTS GAIN FULL AVG:
# 30 kV, 10 W: gain = 0.49732066565733396
# 30 kV, 20 W: gain = 0.49658032272206576
# 30 kV, 30 W: gain = 0.4974014623766823
# 30 kV, 40 W: gain = 0.4982955189648602
# 45 kV, 10 W: gain = 0.7079770380980214
# 45 kV, 20 W: gain = 0.708662168281262
# 45 kV, 30 W: gain = 0.7082068231686385
# 45 kV, 40 W: gain = 0.7096467542608949
# 60 kV, 10 W: gain = 0.8551124239661559
# 60 kV, 20 W: gain = 0.8563697851525969
# 60 kV, 30 W: gain = 0.8579282804948085
# 60 kV, 40 W: gain = 0.8594508876470477
# 75 kV, 10 W: gain = 0.9843940511669307
# 75 kV, 20 W: gain = 0.9846795218421803
# 75 kV, 30 W: gain = 0.9861696699784297
# 75 kV, 40 W: gain = 0.9851329470417651
# 90 kV, 10 W: gain = 1.1098482204501892
# 90 kV, 20 W: gain = 1.1124966302890238
# 90 kV, 30 W: gain = 1.1120634555658473
# 90 kV, 40 W: gain = 1.1119043705511888