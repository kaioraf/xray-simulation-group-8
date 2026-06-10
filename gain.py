from imageAnalysis import average_single_pixel, get_variance_single_pixel
from fileIO import images_to_array


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
images = images_to_array(voltage_type="30kV\\10W")
pixel_x = 0
pixel_y = 0

gain(images, pixel_x, pixel_y)