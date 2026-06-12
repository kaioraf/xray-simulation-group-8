"""
Collection of functions to analyse the image arrays, taking their average and their standard deviation,
either of an entire layer of images or a single layer of pixels
"""

from fileIO import *
import time

VOLTAGES: set = {'30', '45', '60', '75', '90'}
WATTAGES: set = {'10', '20', '30', '40'}
COUNTS = 20


# take all the files within some folder e.g. 75kV/10W/, and then averages all their values into a single new image
def average_full_images(images, voltage_type = 'darkfield', save_file = False):
      
      # get the dimensions of the images
      height = int(images.shape[1])
      width = int(images.shape[0])
      # create an empty array
      avg_array_xy: np.ndarray = np.zeros((width, height))
      
      for y in range(height):
            for x in range(width):                   
                  avg_array_xy[x, y] = average_single_pixel(images, x, y)
      if save_file:
            dirname: str = os.path.dirname(p = __file__)
            # remove the slash from the filename
            safe_path: str = voltage_type[:4] + voltage_type[5:]
            # save values to .npy file to read out the image: avg_image = np.load("avg_array_75kV_10W.npy")
            np.save(file = f"{dirname}/Numpy image arrays/{voltage_type}/avg_array_{safe_path}.npy", arr = avg_array_xy) # macos/linux
            print(voltage_type, safe_path)
      return avg_array_xy

# take all the files within some folder e.g. 75kV/10W/, and for each pixel calculate the variance of the 20 images
# so it outputs a 2d array with each pixel entry being its variance
def variance_full_images(images, voltage_type = 'darkfield', save_file = False):

      # get dimension of the images
      height = int(images.shape[1])
      width = int(images.shape[0])
      # create an empty array
      var_array_xy: np.ndarray = np.zeros((width, height))

      for y in range(height - 1):
            for x in range(width - 1):
                  var_array_xy[x, y] = get_variance_single_pixel(images, x, y)
      
      if save_file:
            dirname: str = os.path.dirname(__file__)
            # remove the slash from the filename
            safe_path: str = voltage_type[:4] + voltage_type[5:]
            # save values to .npy file to read out the image: var_image = np.load("var_array_75kV_10W.npy")
            np.save(file = f"{dirname}/Numpy image arrays/{voltage_type}/var_array_{safe_path}.npy", arr = var_array_xy) # macos/linux

      return var_array_xy

# take the stack of 20 images and average their values
def average_single_pixel(images, x, y):
      return np.average(images[x, y])
      
def get_variance_single_pixel(images, x, y):
      return np.var(images[x, y])

# go from an image array to a .png, use exposure to adjust the brightness
def create_image(image, exposure = 1, filename = 'result.png'):
      print(filename)
      image: Image = image * exposure
      picture: Image = Image.fromarray(obj = (image.transpose()).astype(np.uint16))
      picture.save(filename)
      
def create_flatfield_images(): # very long function, do not run if the files are already created!
      for voltage in VOLTAGES:
            for wattage in WATTAGES:
                  print(voltage, wattage)
                  path: str = voltage + "kV" + "/" + wattage + "W" # linux/macos only, but this will only run once anyway
                  images: np.ndarray = images_to_array(voltage_type = path)
                  avg: np.ndarray = average_full_images(images = images, voltage_type = path, save_file = True)
                  var: np.ndarray = variance_full_images(images = images, voltage_type = path, save_file = True)
                  
                  dirname: str = os.path.dirname(p = __file__)
                  safe_path: str = path[:4] + path[5:]
                  full_path: str = f"{dirname}/Numpy image arrays/{path}/avg_array_{safe_path}.png"
                  create_image(image = avg, filename = full_path)
                  full_path = f"{dirname}/Numpy image arrays/{path}/var_array_{safe_path}.png"
                  create_image(image = var, filename = full_path)
            
def create_darkfield_images():
      path: str = 'darkfield'
      images: np.ndarray = images_to_array(voltage_type = path)
      avg: np.ndarray = average_full_images(images = images, voltage_type = path, save_file = True)
      var: np.ndarray = variance_full_images(images = images, voltage_type = path, save_file = True)
      
      dirname: str = os.path.dirname(p = __file__)
      safe_path: str = path[:4] + path[5:]
      full_path: str = f"{dirname}/Numpy image arrays/{path}/avg_array_{safe_path}.png"
      create_image(image = avg, filename = full_path)
      full_path = f"{dirname}/Numpy image arrays/{path}/var_array_{safe_path}.png"
      create_image(image = var, filename = full_path)
      
create_darkfield_images()
# create_image(average_full_images(images_to_array()))
# start: float = time.perf_counter() # timer
# create_all_images()
# image: np.ndarray = images_to_array()
# avg: float = average_single_pixel(images = image, x = 0, y = 0)
# print(get_variance_single_pixel(images = image, x = 0, y = 0))
# get_variance_single_pixel(images = average_single_pixel(images = images_to_array(), x = 0, y = 0), x = 0, y = 0)
# end: float = time.perf_counter() # timer

# print(f"Duration: {end - start} s") # timer
# average_single_pixel(images = images_to_array(), x = 0, y = 0)
