import os, glob
from PIL import Image
import scipy as sp
import numpy as np
import platform

#take the path to the directory that will be processed, accounting for windows/unix filesystems
dirname = os.path.dirname(__file__)
if (platform.system() == 'Linux' or platform.system() == 'Darwin'): 
      path = os.path.join(dirname, '2026-06-08_Detector_noise_calibration/darkfield')
else:
      path = os.path.join(dirname, '2026-06-08_Detector_noise_calibration\darkfield')
      

for filename in glob.glob(os.path.join(path, '*.tif')):
      print(filename)
      # Image.open("2026-06-08_Detector_noise_calibration\darkfield\scan_00.tif")
      # with open(os.path.join(os.getcwd(), filename), 'r') as file: # open in readonly mode
      #       for lines in csvFile:
      #             summ += float(lines[1])
      #             len += 1
      #       avg_list.update({filename: (summ/len)})
      # with open(os.path.join(os.getcwd(), filename), 'r') as file: 
      #       csvFile = csv.reader(file)
      #       next(csvFile)
      #       var = 0
      #       for lines in csvFile:
      #             var += ((float(lines[1]) - (summ/len))**2)
            