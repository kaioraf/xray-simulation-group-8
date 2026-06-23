# fits the power-slope maps against voltage to create alpha, beta, and gamma maps.
import os
import platform

import matplotlib.pyplot as plt
import numpy as np


# these maps describe how the power-slope changes with voltage:
# power_slope(V) = alpha * V**2 + beta * V + gamma
voltages: list = ['30kV', '45kV', '60kV', '75kV', '90kV']
kV: np.ndarray = np.array([30, 45, 60, 75, 90], dtype = float)


def project_path(*parts):
    dirname: str = os.path.dirname(__file__)
    return os.path.join(dirname, *parts)


def load_power_slope_maps():
    example_map: np.ndarray = np.load(project_path('Parameter maps', 'a_map_30kV.npy'))
    x_len: int = example_map.shape[0]
    y_len: int = example_map.shape[1]

    slope_maps: np.ndarray = np.zeros((len(voltages), x_len, y_len))
    slope_maps[0, :, :] = example_map

    for i in range(1, len(voltages)):
        voltage: str = voltages[i]
        slope_maps[i, :, :] = np.load(project_path('Parameter maps', f'a_map_{voltage}.npy'))

    return slope_maps


def fit_slope_voltage_maps():
    slope_maps: np.ndarray = load_power_slope_maps()

    # Design matrix for: power_slope(V) = alpha * V**2 + beta * V + gamma
    design_matrix: np.ndarray = np.column_stack((kV**2, kV, np.ones_like(kV)))
    pseudo_inverse: np.ndarray = np.linalg.pinv(design_matrix)

    fit_parameters: np.ndarray = np.tensordot(pseudo_inverse, slope_maps, axes = (1, 0))

    alpha_map: np.ndarray = fit_parameters[0, :, :]
    beta_map: np.ndarray = fit_parameters[1, :, :]
    gamma_map: np.ndarray = fit_parameters[2, :, :]

    return alpha_map, beta_map, gamma_map


def save_slope_voltage_maps():
    alpha_map: np.ndarray
    beta_map: np.ndarray
    gamma_map: np.ndarray
    alpha_map, beta_map, gamma_map = fit_slope_voltage_maps()

    output_folder: str = project_path('Final parameter maps')
    os.makedirs(output_folder, exist_ok = True)

    np.save(file = os.path.join(output_folder, 'alpha_map.npy'), arr = alpha_map)
    np.save(file = os.path.join(output_folder, 'beta_map.npy'), arr = beta_map)
    np.save(file = os.path.join(output_folder, 'gamma_map.npy'), arr = gamma_map)



def color_map_power_slope(voltage):
    alpha_map: np.ndarray
    beta_map: np.ndarray
    gamma_map: np.ndarray
    alpha_map, beta_map, gamma_map = fit_slope_voltage_maps()

    slope_map: np.ndarray = alpha_map * voltage**2 + beta_map * voltage + gamma_map

    # ignore nan values and scale around the useful slope range
    vmin: float = np.nanpercentile(slope_map, 1)
    vmax: float = np.nanpercentile(slope_map, 99)

    plt.figure()
    plt.imshow(X = slope_map, vmin = vmin, vmax = vmax)
    plt.colorbar(label = 'intensity increase per watt')
    plt.title(label = rf'Power-slope map at ${voltage}$ kV')
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    plt.show()


save_slope_voltage_maps()
color_map_power_slope(voltage = 90)
