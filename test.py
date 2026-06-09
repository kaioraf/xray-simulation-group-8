from PIL import Image
import scipy as sp
import numpy as np
df00 = Image = Image.open("2026-06-08_Detector_noise_calibration\darkfield\scan_00.tif")
df00array = np.array(df00)
print(df00array[0, 0])
