from fileIO import *

def eerstepixelwaarde(volt, watt, count):
    volt = str(object = volt)
    watt = str(object = watt)
    count = int(count)
    voltage_name_maker: str = volt + "kV/" + watt + "W"
    imagefolderarray: np.ndarray = images_to_array(voltage_type = voltage_name_maker)
    pixelwaarde: int = imagefolderarray[0, 0, count]
    return(pixelwaarde)

print(eerstepixelwaarde(volt = 90, watt = 20, count = 13))