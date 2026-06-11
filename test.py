from PIL import Image
import scipy as sp
import numpy as np
from fileIO import *
import os, glob
# lf4090 = Image = Image.open("2026-06-08_Detector_noise_calibration/90kV/40W/scan_00.tif")
# df00array = np.array(lf4090)
# print(df00array[0, 0])
# dict1=images_to_dict(voltage_type= "90kV/10W")
# a=dict1["c:\\Users\\tesom\\Documents\\GitHub\\Project-group-8\\2026-06-08_Detector_noise_calibration\\90kV/10W\\scan_01.tif"]
# print(a[0, 0])


# def eerstepixelwaarde(volt, watt, count):
#     volt=str(volt)
#     watt=str(watt)
#     count=int(count)
#     dirname = os.path.dirname(__file__)
#     voltage_name_maker=volt+"kV/"+watt+"W"
#     dirnamepixel=dirname + "\\2026-06-08_Detector_noise_calibration\\" + volt + "kV" + "\\" +watt+"W\\scan_"+f"{count:02d}"+".tif"
#     imagefolderarray=images_to_array(voltage_type=voltage_name_maker)
#     pixelwaarde=imagefolderarray[0, 0, count]
#     return(pixelwaarde)

# print(eerstepixelwaarde(45, 20, 13))

# dirname = os.path.dirname(__file__)
# array_dir = os.path.join(dirname, "Numpy image arrays")
# print(array_dir)
# print(os.path.exists(array_dir))