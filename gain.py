from fileIO import read_np_image_arrays
import matplotlib.pyplot as plt
import platform
import numpy as np
from imageAnalysis import create_image

if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
      SLASH = '/'
else: # windows
      SLASH = '\\'
            

# Available settings
voltages = [30, 45, 60, 75, 90]
wattages = [10, 20, 30, 40]

pixel_x = 0
pixel_y=0

# (hopefully) Efficient vectorized calculation for the gain for each pixel, stored into an array
def full_image_gain(avg_image, var_image):
    avg_darkfield = read_np_image_arrays(dist_type='avg')
    var_darkfield = read_np_image_arrays(dist_type='var')
    
    true_intensity_avg_image = avg_image - avg_darkfield
    # create_image(true_intensity_avg_image, exposure=5)
    # create_image(var_image - var_darkfield, exposure=5)
            
    with np.errstate(divide='ignore', invalid='ignore'):
        true_intensity_avg_image = np.nan_to_num(np.reciprocal(true_intensity_avg_image))
        
    gain_image = (var_image - var_darkfield) * true_intensity_avg_image
    for i in gain_image:
        for j in i:
            print(j)        
    create_image(gain_image, exposure=100, filename="gaintest.png")

# avg_image = read_np_image_arrays(voltage_type='30kV/20W',dist_type='avg')
# var_image = read_np_image_arrays(voltage_type='30kV/20W',dist_type='var')
# full_image_gain(avg_image, var_image)

# Calculate gain for single pixels
#------------------------------------------------------------------------------------------
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

def plot_gain():
    #make directory to save gain per setting
    gain_by_voltage = {}

    #loop over all settings
    for voltage in voltages:
        gain_lst = []

        for watt in wattages:
            folder = f"{voltage}kV{SLASH}{watt}W"
            images_avg = read_np_image_arrays(voltage_type=folder, dist_type='avg')
            images_var = read_np_image_arrays(voltage_type=folder, dist_type='var')

            gain_value = gain(images_avg, images_var, pixel_x, pixel_y)
            gain_lst.append(gain_value)

            print(f"{voltage} kV, {watt} W: gain = {gain_value}")

        gain_by_voltage[voltage] = gain_lst

        # RESULTS:
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
    # --------------------------------------------------------------------------------------------

    # Plot wattage against gain for every constant voltage
    for voltage, gains in gain_by_voltage.items():
        plt.plot(wattages, gains, marker="o", label=f"{voltage} kV")

    plt.xlabel("Wattage (W)")
    plt.ylabel("Gain")
    plt.title(f"Gain vs Wattage for Different Voltages, PIXEL{pixel_x, pixel_y}")
    plt.legend()
    plt.grid(True, which="both")
    plt.savefig(f"gain pixel({pixel_x}, {pixel_y}).png")
    plt.show()

plot_gain()
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

# # all settings
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
