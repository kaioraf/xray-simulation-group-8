"""
Collection of functions to analyse the image arrays, taking their average and their standard deviation,
either of an entire layer of images or a single layer of pixels
"""

from fileIO import *
import time

VOLTAGES: list = {'30', '45', '60', '75', '90'}
WATTAGES: list = {'10', '20', '30', '40'}
COUNTS = 20
BIGCOUNTS = 512
ONEOVERTENTWENTYFOUR = 1/20

# take all the files within some folder e.g. 75kV/10W/, and then averages all their values into a single new image
def average_full_images(images, voltage_type = 'darkfield', save_file = False):
      # get the dimensions of the images
      height = int(images.shape[1])
      width = int(images.shape[0])
      depth = int(images.shape[2])
      
      start = time.time()
      
      # create an empty array
      avg_array_xy: np.ndarray = np.zeros((width, height))
      
      #start the sum with the first layer of the images
      sum_array: np.ndarray = images[:, :, 0]
      
      #compute the average
      for z in range(1, depth):
            sum_array = sum_array + images[:, :, z]
      avg_array_xy = sum_array * ONEOVERTENTWENTYFOUR
      end = time.time()
      print("Average computed in:", end - start, "seconds")
      
      if save_file:
            dirname: str = os.path.dirname(p = __file__)
            # remove the slash from the filename
            safe_path: str = voltage_type[:4] + voltage_type[5:]
            # save values to .npy file to read out the image: avg_image = np.load("avg_array_75kV_10W.npy")
            np.save(file = f"{dirname}{SLASH}Numpy image arrays{SLASH}{voltage_type}{SLASH}avg_array_{safe_path}.npy", arr = avg_array_xy)
      return np.transpose(avg_array_xy) #transposed array is used everywhere else, this makes it width-height

# take all the files within some folder e.g. 75kV/10W/, and for each pixel calculate the variance of the 20 images
# so it outputs a 2d array with each pixel entry being its variance
def variance_full_images(images, voltage_type = 'darkfield', save_file = False):

      height = int(images.shape[1])
      width = int(images.shape[0])
      depth = int(images.shape[2])
      
      start = time.time()
      
      # vectorized version of the algorithm at https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Computing_shifted_data
      # this is done to avoid catastrophic cancellation
      Ex = np.zeros((width, height))
      Ex2 = np.zeros((width, height))
      
      #take a random sample of the data
      K = images[:,:,4]
      for z in range(depth):
            Ex += images[:, :, z] - K
            Ex2 += (images[:, :, z] - K)**2
      #       print("ex2", Ex2[0,0],
      #             "ex", Ex[0,0])
      # print("EXes", Ex[0,0], Ex2[0,0])
      var_array_xy = (Ex2 - Ex**2 * ONEOVERTENTWENTYFOUR) / (COUNTS)
      end = time.time()
      print("Variance computed in:", end - start, "seconds")
      
      if save_file:
            dirname: str = os.path.dirname(__file__)
            # remove the slash from the filename
            safe_path: str = voltage_type[:4] + voltage_type[5:]
            # save values to .npy file to read out the image: var_image = np.load("var_array_75kV_10W.npy")
            np.save(file = f"{dirname}{SLASH}Numpy image arrays{SLASH}{voltage_type}{SLASH}var_array_{safe_path}.npy", arr = var_array_xy) # macos/linux

      return np.transpose(var_array_xy)

# take the stack of 20 images and average their values for a single pixel
def average_single_pixel(images, x, y):
      return np.average(images[x, y])
      
def get_variance_single_pixel(images, x, y):
      return np.var(images[x, y])

# go from an image array to a .png, use exposure to adjust the brightness
def create_image(image, exposure = 1, filename = 'result.png'):
      print("Image created at:", filename)
      image: Image = image * exposure
      picture: Image = Image.fromarray(obj = image.astype(np.uint16))
      picture.save(filename)
      
def create_images(save_image = False, parent_directory_name = "Numpy image arrays"): # very long function, do not run if the files are already created!
      start = time.time()

      dirname: str = os.path.dirname(p = __file__)
      path: str = 'darkfield'
      print(f"\nDoing darkfield")
      images: np.ndarray = images_to_array(voltage_type = path)
      avg: np.ndarray = average_full_images(images = images, voltage_type = path, save_file = True)
      var: np.ndarray = variance_full_images(images = images, voltage_type = path, save_file = True)
      
      if save_image:
            safe_path: str = path[:4] + path[5:]
            full_path: str = f"{dirname}{SLASH}{parent_directory_name}{SLASH}{path}{SLASH}avg_array_{safe_path}.png"
            create_image(image = avg, filename = full_path)
            full_path = f"{dirname}{SLASH}{parent_directory_name}{SLASH}{path}{SLASH}var_array_{safe_path}.png"
            create_image(image = var, filename = full_path)   
             
      dirname: str = os.path.dirname(p = __file__)          
      for voltage in VOLTAGES:
            for wattage in WATTAGES:
                  print(f"\nDoing {voltage}kV at {wattage}W")
                  path: str = voltage + "kV" + SLASH + wattage + "W" # linux/macos only, but this will only run once anyway
                  images: np.ndarray = images_to_array(voltage_type = path)
                  avg: np.ndarray = average_full_images(images, voltage_type = path, save_file = True)
                  var: np.ndarray = variance_full_images(images, voltage_type = path, save_file = True)
                  
                  if save_image:
                        safe_path: str = path[:4] + path[5:]
                        full_path: str = f"{dirname}{SLASH}{parent_directory_name}{SLASH}{path}{SLASH}avg_array_{safe_path}.png"
                        create_image(image = avg, filename = full_path)
                        full_path = f"{dirname}{SLASH}{parent_directory_name}{SLASH}{path}{SLASH}var_array_{safe_path}.png"
                        create_image(image = var, filename = full_path)
      end = time.time()
      print(f"Computed all averages and variances in {end-start} seconds")
                          
def create_folder_structure(parent_directory_name = "test"):
      dirname: str = os.path.dirname(p = __file__)
      parent_directory_path: str = f'{dirname}{SLASH}{parent_directory_name}{SLASH}'
      os.mkdir(parent_directory_path)
      os.mkdir(f'{parent_directory_path}darkfield{SLASH}')
      for voltage in VOLTAGES:
            voltage_directory = f"{parent_directory_path}{voltage}kV{SLASH}"
            os.mkdir(voltage_directory)
            for wattage in WATTAGES:
                  wattage_directory_path: str = f"{voltage_directory}{wattage}W{SLASH}"
                  os.mkdir(wattage_directory_path)
                  print(parent_directory_path)
                  
create_images(save_image=True)
print(read_np_image_arrays(dist_type='var').shape)
# create_folder_structure()