import os
import platform

import matplotlib.pyplot as plt
import numpy as np

from fileIO import read_np_image_arrays


# This file creates a per-pixel version of the variance model.
#
# For every pixel and every voltage:
# Var(I) = k_map(V) * I + intercept_map(V)
#
# Then, for every pixel:
# k_map(V) = q2_map * V**2 + q1_map * V + q0_map
# intercept_map(V) = r2_map * V**2 + r1_map * V + r0_map
#
# The final variance function can later use:
# I = eind_baas(P, V)
# Var(I) = k_map(V) * I + intercept_map(V)

voltages: list = [30, 45, 60, 75, 90]
wattages: list = [10, 20, 30, 40]
kV: np.ndarray = np.array(object = voltages, dtype = float)

if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
    slash: str = "/"
else:
    slash: str = "\\"


def project_path(*parts):
    dirname: str = os.path.dirname(__file__)
    return os.path.join(dirname, *parts)


def make_voltage_type(voltage, wattage):
    return f'{voltage}kV{slash}{wattage}W'


def load_maps_for_voltage(voltage):
    example_map: np.ndarray = read_np_image_arrays(
        voltage_type = make_voltage_type(voltage = voltage, wattage = wattages[0]),
        dist_type = 'avg'
    )

    height: int = example_map.shape[0]
    width: int = example_map.shape[1]

    average_stack: np.ndarray = np.zeros(shape = (len(wattages), height, width))
    variance_stack: np.ndarray = np.zeros(shape = (len(wattages), height, width))

    for i in range(len(wattages)):
        wattage: int = wattages[i]
        voltage_type: str = make_voltage_type(voltage = voltage, wattage = wattage)

        average_stack[i, :, :] = read_np_image_arrays(voltage_type = voltage_type, dist_type = 'avg')
        variance_stack[i, :, :] = read_np_image_arrays(voltage_type = voltage_type, dist_type = 'var')

    return average_stack, variance_stack


def fit_variance_against_intensity_for_voltage(voltage):
    average_stack: np.ndarray
    variance_stack: np.ndarray
    average_stack, variance_stack = load_maps_for_voltage(voltage = voltage)

    valid: np.ndarray = (
        np.isfinite(average_stack)
        & np.isfinite(variance_stack)
        & (average_stack > 0)
        & (variance_stack > 0)
    )

    I: np.ndarray = np.where(valid, average_stack, np.nan)
    Var_I: np.ndarray = np.where(valid, variance_stack, np.nan)

    n: np.ndarray = np.sum(a = valid, axis = 0).astype(float)
    Sx: np.ndarray = np.nansum(a = I, axis = 0)
    Sy: np.ndarray = np.nansum(a = Var_I, axis = 0)
    Sxx: np.ndarray = np.nansum(a = I**2, axis = 0)
    Sxy: np.ndarray = np.nansum(a = I * Var_I, axis = 0)

    denominator: np.ndarray = n * Sxx - Sx**2
    good_fit: np.ndarray = (n >= 2) & np.isfinite(denominator) & (denominator != 0)

    k_map: np.ndarray = np.full(shape = Sx.shape, fill_value = np.nan)
    intercept_map: np.ndarray = np.full(shape = Sx.shape, fill_value = np.nan)

    k_map[good_fit] = (n[good_fit] * Sxy[good_fit] - Sx[good_fit] * Sy[good_fit]) / denominator[good_fit]
    intercept_map[good_fit] = (Sxx[good_fit] * Sy[good_fit] - Sx[good_fit] * Sxy[good_fit]) / denominator[good_fit]

    return k_map, intercept_map


def fit_variance_against_intensity_all_voltages():
    example_map: np.ndarray = read_np_image_arrays(
        voltage_type = make_voltage_type(voltage = voltages[0], wattage = wattages[0]),
        dist_type = 'avg'
    )

    height: int = example_map.shape[0]
    width: int = example_map.shape[1]

    k_maps: np.ndarray = np.zeros(shape = (len(voltages), height, width))
    intercept_maps: np.ndarray = np.zeros(shape = (len(voltages), height, width))

    for i in range(len(voltages)):
        voltage: int = voltages[i]
        print(f'Fitting variance against intensity for {voltage} kV...')

        k_map: np.ndarray
        intercept_map: np.ndarray
        k_map, intercept_map = fit_variance_against_intensity_for_voltage(voltage = voltage)

        k_maps[i, :, :] = k_map
        intercept_maps[i, :, :] = intercept_map

    return k_maps, intercept_maps


def quadratic_voltage_fit_maps(parameter_stack, chunk_rows = 128):
    height: int = parameter_stack.shape[1]
    width: int = parameter_stack.shape[2]

    q2_map: np.ndarray = np.full(shape = (height, width), fill_value = np.nan)
    q1_map: np.ndarray = np.full(shape = (height, width), fill_value = np.nan)
    q0_map: np.ndarray = np.full(shape = (height, width), fill_value = np.nan)

    V: np.ndarray = kV[:, np.newaxis, np.newaxis]

    for row_start in range(0, height, chunk_rows):
        row_stop: int = min(row_start + chunk_rows, height)
        y: np.ndarray = parameter_stack[:, row_start:row_stop, :]

        valid: np.ndarray = np.isfinite(y)
        y_clean: np.ndarray = np.where(valid, y, np.nan)

        n: np.ndarray = np.sum(a = valid, axis = 0).astype(float)
        S0: np.ndarray = n
        S1: np.ndarray = np.sum(a = valid * V, axis = 0)
        S2: np.ndarray = np.sum(a = valid * V**2, axis = 0)
        S3: np.ndarray = np.sum(a = valid * V**3, axis = 0)
        S4: np.ndarray = np.sum(a = valid * V**4, axis = 0)

        T0: np.ndarray = np.nansum(a = y_clean, axis = 0)
        T1: np.ndarray = np.nansum(a = y_clean * V, axis = 0)
        T2: np.ndarray = np.nansum(a = y_clean * V**2, axis = 0)

        rows: int = row_stop - row_start
        A: np.ndarray = np.zeros(shape = (rows, width, 3, 3))
        B: np.ndarray = np.zeros(shape = (rows, width, 3))

        A[:, :, 0, 0] = S4
        A[:, :, 0, 1] = S3
        A[:, :, 0, 2] = S2
        A[:, :, 1, 0] = S3
        A[:, :, 1, 1] = S2
        A[:, :, 1, 2] = S1
        A[:, :, 2, 0] = S2
        A[:, :, 2, 1] = S1
        A[:, :, 2, 2] = S0

        B[:, :, 0] = T2
        B[:, :, 1] = T1
        B[:, :, 2] = T0

        good_fit: np.ndarray = n >= 3
        A_flat: np.ndarray = A[good_fit]
        B_flat: np.ndarray = B[good_fit]

        coefficients_flat: np.ndarray = np.linalg.pinv(A_flat) @ B_flat[:, :, np.newaxis]
        coefficients_flat = coefficients_flat[:, :, 0]

        q2_chunk: np.ndarray = q2_map[row_start:row_stop, :]
        q1_chunk: np.ndarray = q1_map[row_start:row_stop, :]
        q0_chunk: np.ndarray = q0_map[row_start:row_stop, :]

        q2_chunk[good_fit] = coefficients_flat[:, 0]
        q1_chunk[good_fit] = coefficients_flat[:, 1]
        q0_chunk[good_fit] = coefficients_flat[:, 2]

    return q2_map, q1_map, q0_map


def fit_per_pixel_variance_model_maps():
    k_maps: np.ndarray
    intercept_maps: np.ndarray
    k_maps, intercept_maps = fit_variance_against_intensity_all_voltages()

    print('Fitting k maps against voltage...')
    k_q2_map: np.ndarray
    k_q1_map: np.ndarray
    k_q0_map: np.ndarray
    k_q2_map, k_q1_map, k_q0_map = quadratic_voltage_fit_maps(parameter_stack = k_maps)

    print('Fitting intercept maps against voltage...')
    intercept_r2_map: np.ndarray
    intercept_r1_map: np.ndarray
    intercept_r0_map: np.ndarray
    intercept_r2_map, intercept_r1_map, intercept_r0_map = quadratic_voltage_fit_maps(parameter_stack = intercept_maps)

    return k_maps, intercept_maps, k_q2_map, k_q1_map, k_q0_map, intercept_r2_map, intercept_r1_map, intercept_r0_map


def save_per_pixel_variance_model_maps(save_intermediate = True):
    k_maps: np.ndarray
    intercept_maps: np.ndarray
    k_q2_map: np.ndarray
    k_q1_map: np.ndarray
    k_q0_map: np.ndarray
    intercept_r2_map: np.ndarray
    intercept_r1_map: np.ndarray
    intercept_r0_map: np.ndarray
    k_maps, intercept_maps, k_q2_map, k_q1_map, k_q0_map, intercept_r2_map, intercept_r1_map, intercept_r0_map = fit_per_pixel_variance_model_maps()

    output_folder: str = project_path('Final parameter maps')
    os.makedirs(name = output_folder, exist_ok = True)

    np.save(file = os.path.join(output_folder, 'variance_pixel_k_q2_map.npy'), arr = k_q2_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_k_q1_map.npy'), arr = k_q1_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_k_q0_map.npy'), arr = k_q0_map)

    np.save(file = os.path.join(output_folder, 'variance_pixel_intercept_r2_map.npy'), arr = intercept_r2_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_intercept_r1_map.npy'), arr = intercept_r1_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_intercept_r0_map.npy'), arr = intercept_r0_map)

    if save_intermediate:
        for i in range(len(voltages)):
            voltage: int = voltages[i]
            np.save(file = os.path.join(output_folder, f'variance_pixel_k_map_{voltage}kV.npy'), arr = k_maps[i, :, :])
            np.save(file = os.path.join(output_folder, f'variance_pixel_intercept_map_{voltage}kV.npy'), arr = intercept_maps[i, :, :])


def load_per_pixel_variance_model_maps():
    input_folder: str = project_path('Final parameter maps')

    k_q2_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_k_q2_map.npy'))
    k_q1_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_k_q1_map.npy'))
    k_q0_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_k_q0_map.npy'))

    intercept_r2_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_intercept_r2_map.npy'))
    intercept_r1_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_intercept_r1_map.npy'))
    intercept_r0_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_intercept_r0_map.npy'))

    return k_q2_map, k_q1_map, k_q0_map, intercept_r2_map, intercept_r1_map, intercept_r0_map


def variance_from_intensity_map(intensity_map, V):
    k_q2_map: np.ndarray
    k_q1_map: np.ndarray
    k_q0_map: np.ndarray
    intercept_r2_map: np.ndarray
    intercept_r1_map: np.ndarray
    intercept_r0_map: np.ndarray
    k_q2_map, k_q1_map, k_q0_map, intercept_r2_map, intercept_r1_map, intercept_r0_map = load_per_pixel_variance_model_maps()

    k_map: np.ndarray = k_q2_map * V**2 + k_q1_map * V + k_q0_map
    intercept_map: np.ndarray = intercept_r2_map * V**2 + intercept_r1_map * V + intercept_r0_map

    variance_map: np.ndarray = k_map * intensity_map + intercept_map

    return variance_map


def plot_fit_map(fit_map, title, colorbar_label):
    vmin: float = np.nanpercentile(fit_map, 1)
    vmax: float = np.nanpercentile(fit_map, 99)

    plt.figure()
    plt.imshow(X = fit_map, vmin = vmin, vmax = vmax)
    plt.colorbar(label = colorbar_label)
    plt.title(label = title)
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    plt.show()


if __name__ == '__main__':
    save_per_pixel_variance_model_maps(save_intermediate = True)
