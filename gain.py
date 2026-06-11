from imageAnalysis import average_single_pixel, get_variance_single_pixel
from fileIO import images_to_array
import matplotlib.pyplot as plt


def gain(images, pixel_x, pixel_y):
    # Calculate mean intensity and variance for selected pixel
    y = average_single_pixel(images, pixel_x, pixel_y)
    var_y = get_variance_single_pixel(images, pixel_x, pixel_y, y)

    # Load darkfield images once
    dark_images = images_to_array(voltage_type="darkfield")

    # Calculate darkfield mean intensity and variance
    d_e = average_single_pixel(dark_images, pixel_x, pixel_y)
    var_de = get_variance_single_pixel(dark_images, pixel_x, pixel_y, d_e)

    # Avoid division by zero
    if y == d_e:
        raise ValueError("Cannot calculate gain because y and d_e are equal.")

    gain_value = (var_y - var_de) / (y - d_e)
    print(gain_value)
    return gain_value


# Change folder and pixel
pixel_x = 0
pixel_y = 0

# Available settings
voltages = [30, 45, 60, 75, 90]
wattages = [10, 20, 30, 40]


# Store gain values for each voltage (dictionary)
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


# Plot wattage against gain for every constant voltage
for voltage, gains in gain_by_voltage.items():
    plt.plot(wattages, gains, marker="o", label=f"{voltage} kV")

plt.xlabel("Wattage (W)")
plt.ylabel("Gain")
plt.title("Gain vs Wattage for Different Voltages")
plt.xlim(5,46)
plt.ylim(0,2)
plt.legend()
plt.grid(True, which="both")
plt.show()
    



