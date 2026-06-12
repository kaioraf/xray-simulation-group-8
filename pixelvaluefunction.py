from fileIO import *

def eerstepixelwaarde(volt, watt, count):
    volt=str(volt)
    watt=str(watt)
    count=int(count)
    dirname = os.path.dirname(__file__)
    voltage_name_maker=volt+"kV/"+watt+"W"
    dirnamepixel=dirname + "\\2026-06-08_Detector_noise_calibration\\" + volt + "kV" + "\\" +watt+"W\\scan_"+f"{count:02d}"+".tif"
    imagefolderarray=images_to_array(voltage_type=voltage_name_maker)
    pixelwaarde=imagefolderarray[0, 0, count]
    return(pixelwaarde)

print(eerstepixelwaarde(45, 20, 13))