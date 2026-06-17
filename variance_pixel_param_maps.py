import os
import platform
import random

import matplotlib.pyplot as plt
import numpy as np

from fileIO import read_np_image_arrays


# Per-pixel version of the corrected variance model:
#
# I_real = I_total - I_dark
# Var_real = Var_total - Var_dark
# Var_real = k_map(V) * I_real
#
# Then, for every pixel:
# k_map(V) = q2_map * V**2 + q1_map * V + q0_map
#
# The final variance function can later use:
# Var_total(P, V) = Var_dark + k_map(V) * I_real(P, V)

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


def load_real_maps_for_voltage(voltage):
    darkfield_average_map: np.ndarray = read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'avg')
    darkfield_variance_map: np.ndarray = read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'var')

    height: int = darkfield_average_map.shape[0]
    width: int = darkfield_average_map.shape[1]

    real_intensity_stack: np.ndarray = np.zeros(shape = (len(wattages), height, width))
    real_variance_stack: np.ndarray = np.zeros(shape = (len(wattages), height, width))

    for i in range(len(wattages)):
        wattage: int = wattages[i]
        voltage_type: str = make_voltage_type(voltage = voltage, wattage = wattage)

        average_map: np.ndarray = read_np_image_arrays(voltage_type = voltage_type, dist_type = 'avg')
        variance_map: np.ndarray = read_np_image_arrays(voltage_type = voltage_type, dist_type = 'var')

        real_intensity_stack[i, :, :] = average_map - darkfield_average_map
        real_variance_stack[i, :, :] = variance_map - darkfield_variance_map

    return real_intensity_stack, real_variance_stack


def fit_real_variance_against_real_intensity_for_voltage(voltage):
    real_intensity_stack: np.ndarray
    real_variance_stack: np.ndarray
    real_intensity_stack, real_variance_stack = load_real_maps_for_voltage(voltage = voltage)

    valid: np.ndarray = (
        np.isfinite(real_intensity_stack)
        & np.isfinite(real_variance_stack)
        & (real_intensity_stack > 0)
    )

    I_real: np.ndarray = np.where(valid, real_intensity_stack, np.nan)
    Var_real: np.ndarray = np.where(valid, real_variance_stack, np.nan)

    numerator: np.ndarray = np.nansum(a = I_real * Var_real, axis = 0)
    denominator: np.ndarray = np.nansum(a = I_real**2, axis = 0)
    n: np.ndarray = np.sum(a = valid, axis = 0)

    good_fit: np.ndarray = (n >= 2) & np.isfinite(denominator) & (denominator > 0)

    k_map: np.ndarray = np.full(shape = denominator.shape, fill_value = np.nan)
    k_map[good_fit] = numerator[good_fit] / denominator[good_fit]

    return k_map


def fit_real_variance_against_real_intensity_all_voltages():
    darkfield_average_map: np.ndarray = read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'avg')
    height: int = darkfield_average_map.shape[0]
    width: int = darkfield_average_map.shape[1]

    k_maps: np.ndarray = np.zeros(shape = (len(voltages), height, width))

    for i in range(len(voltages)):
        voltage: int = voltages[i]
        print(f'Fitting real variance against real intensity for {voltage} kV...')

        k_map: np.ndarray = fit_real_variance_against_real_intensity_for_voltage(voltage = voltage)
        k_maps[i, :, :] = k_map

    return k_maps


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


def fit_per_pixel_real_variance_model_maps():
    k_maps: np.ndarray = fit_real_variance_against_real_intensity_all_voltages()

    print('Fitting real-signal k maps against voltage...')
    k_q2_map: np.ndarray
    k_q1_map: np.ndarray
    k_q0_map: np.ndarray
    k_q2_map, k_q1_map, k_q0_map = quadratic_voltage_fit_maps(parameter_stack = k_maps)

    return k_maps, k_q2_map, k_q1_map, k_q0_map


def save_per_pixel_variance_model_maps(save_intermediate = True):
    k_maps: np.ndarray
    k_q2_map: np.ndarray
    k_q1_map: np.ndarray
    k_q0_map: np.ndarray
    k_maps, k_q2_map, k_q1_map, k_q0_map = fit_per_pixel_real_variance_model_maps()

    output_folder: str = project_path('Final parameter maps')
    os.makedirs(name = output_folder, exist_ok = True)

    np.save(file = os.path.join(output_folder, 'variance_pixel_real_k_q2_map.npy'), arr = k_q2_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_real_k_q1_map.npy'), arr = k_q1_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_real_k_q0_map.npy'), arr = k_q0_map)

    # Keep the old filenames usable, but with the corrected real-signal meaning.
    np.save(file = os.path.join(output_folder, 'variance_pixel_k_q2_map.npy'), arr = k_q2_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_k_q1_map.npy'), arr = k_q1_map)
    np.save(file = os.path.join(output_folder, 'variance_pixel_k_q0_map.npy'), arr = k_q0_map)

    if save_intermediate:
        for i in range(len(voltages)):
            voltage: int = voltages[i]
            np.save(file = os.path.join(output_folder, f'variance_pixel_real_k_map_{voltage}kV.npy'), arr = k_maps[i, :, :])
            np.save(file = os.path.join(output_folder, f'variance_pixel_k_map_{voltage}kV.npy'), arr = k_maps[i, :, :])


def load_per_pixel_variance_model_maps():
    input_folder: str = project_path('Final parameter maps')

    k_q2_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_real_k_q2_map.npy'))
    k_q1_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_real_k_q1_map.npy'))
    k_q0_map: np.ndarray = np.load(file = os.path.join(input_folder, 'variance_pixel_real_k_q0_map.npy'))

    return k_q2_map, k_q1_map, k_q0_map


def variance_from_intensity_map(intensity_map, V):
    darkfield_average_map: np.ndarray = read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'avg')
    darkfield_variance_map: np.ndarray = read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'var')

    k_q2_map: np.ndarray
    k_q1_map: np.ndarray
    k_q0_map: np.ndarray
    k_q2_map, k_q1_map, k_q0_map = load_per_pixel_variance_model_maps()

    real_intensity_map: np.ndarray = intensity_map - darkfield_average_map
    k_map: np.ndarray = k_q2_map * V**2 + k_q1_map * V + k_q0_map

    variance_map: np.ndarray = darkfield_variance_map + k_map * real_intensity_map

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


def random_pixel():
    darkfield_average_map: np.ndarray = read_np_image_arrays(voltage_type = 'darkfield', dist_type = 'avg')
    height: int = darkfield_average_map.shape[0]
    width: int = darkfield_average_map.shape[1]

    row: int = int(height * random.random())
    column: int = int(width * random.random())

    return row, column


def real_intensity_and_variance_values_for_pixel(voltage, row, column):
    real_intensity_stack: np.ndarray
    real_variance_stack: np.ndarray
    real_intensity_stack, real_variance_stack = load_real_maps_for_voltage(voltage = voltage)

    real_intensity_values: np.ndarray = real_intensity_stack[:, row, column]
    real_variance_values: np.ndarray = real_variance_stack[:, row, column]

    return real_intensity_values, real_variance_values


def fit_k_for_single_pixel_and_voltage(voltage, row, column):
    real_intensity_values: np.ndarray
    real_variance_values: np.ndarray
    real_intensity_values, real_variance_values = real_intensity_and_variance_values_for_pixel(
        voltage = voltage,
        row = row,
        column = column
    )

    valid: np.ndarray = (
        np.isfinite(real_intensity_values)
        & np.isfinite(real_variance_values)
        & (real_intensity_values > 0)
    )

    numerator: float = np.sum(a = real_intensity_values[valid] * real_variance_values[valid])
    denominator: float = np.sum(a = real_intensity_values[valid]**2)

    if denominator <= 0:
        return np.nan

    k: float = numerator / denominator

    return k


def k_values_for_single_pixel(row, column):
    k_values: np.ndarray = np.zeros(shape = len(voltages))

    for i in range(len(voltages)):
        voltage: int = voltages[i]
        k_values[i] = fit_k_for_single_pixel_and_voltage(
            voltage = voltage,
            row = row,
            column = column
        )

    return k_values


def quadratic_k_fit_for_single_pixel(row, column):
    k_values: np.ndarray = k_values_for_single_pixel(row = row, column = column)
    valid: np.ndarray = np.isfinite(k_values)

    if np.sum(a = valid) < 3:
        return np.array([np.nan, np.nan, np.nan]), k_values

    fit_parameters: np.ndarray = np.polyfit(x = kV[valid], y = k_values[valid], deg = 2)

    return fit_parameters, k_values


def plot_real_variance_against_real_intensity_for_pixel(row, column):
    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

    plt.figure()

    for i in range(len(voltages)):
        voltage: int = voltages[i]

        real_intensity_values: np.ndarray
        real_variance_values: np.ndarray
        real_intensity_values, real_variance_values = real_intensity_and_variance_values_for_pixel(
            voltage = voltage,
            row = row,
            column = column
        )

        k: float = fit_k_for_single_pixel_and_voltage(
            voltage = voltage,
            row = row,
            column = column
        )

        intensity_fit: np.ndarray = np.linspace(
            start = 0,
            stop = np.nanmax(real_intensity_values),
            num = 100
        )
        variance_fit: np.ndarray = k * intensity_fit

        plt.plot(
            real_intensity_values,
            real_variance_values,
            'o',
            color = colors[i],
            label = f'{voltage} kV data'
        )
        plt.plot(
            intensity_fit,
            variance_fit,
            '-',
            color = colors[i],
            label = f'{voltage} kV fit'
        )

    plt.title(label = f'Pixel ({row}, {column}): real variance against real intensity')
    plt.xlabel(xlabel = r'Real intensity $I - I_{\mathrm{dark}}$')
    plt.ylabel(ylabel = r'Real variance $\mathrm{Var}(I) - \mathrm{Var}_{\mathrm{dark}}$')
    plt.legend()
    plt.show()


def plot_k_against_voltage_for_pixel(row, column):
    fit_parameters: np.ndarray
    k_values: np.ndarray
    fit_parameters, k_values = quadratic_k_fit_for_single_pixel(row = row, column = column)

    kV_fit: np.ndarray = np.linspace(start = np.min(a = kV), stop = np.max(a = kV), num = 100)
    k_fit: np.ndarray = np.polyval(p = fit_parameters, x = kV_fit)

    plt.figure()
    plt.plot(kV, k_values, 'o', label = r'fitted $k$ values')
    plt.plot(kV_fit, k_fit, '-', label = 'quadratic fit')
    plt.title(label = f'Pixel ({row}, {column}): k against voltage')
    plt.xlabel(xlabel = 'Voltage (kV)')
    plt.ylabel(ylabel = r'$k$ in $\mathrm{Var}_{\mathrm{real}} = k I_{\mathrm{real}}$')
    plt.legend()
    plt.show()


def plot_saved_k_fit_against_voltage_for_pixel(row, column):
    k_values: list = []

    for voltage in voltages:
        k_map: np.ndarray = np.load(
            file = project_path('Final parameter maps', f'variance_pixel_real_k_map_{voltage}kV.npy')
        )
        k_values.append(k_map[row, column])

    q2_map: np.ndarray
    q1_map: np.ndarray
    q0_map: np.ndarray
    q2_map, q1_map, q0_map = load_per_pixel_variance_model_maps()

    q2: float = q2_map[row, column]
    q1: float = q1_map[row, column]
    q0: float = q0_map[row, column]

    kV_fit: np.ndarray = np.linspace(start = np.min(a = kV), stop = np.max(a = kV), num = 100)
    k_fit: np.ndarray = q2 * kV_fit**2 + q1 * kV_fit + q0

    plt.figure()
    plt.plot(kV, k_values, 'o', label = r'saved $k$ maps')
    plt.plot(kV_fit, k_fit, '-', label = 'saved quadratic fit')
    plt.title(label = f'Pixel ({row}, {column}): saved k fit against voltage')
    plt.xlabel(xlabel = 'Voltage (kV)')
    plt.ylabel(ylabel = r'$k$ in $\mathrm{Var}_{\mathrm{real}} = k I_{\mathrm{real}}$')
    plt.legend()
    plt.show()


def random_plot_variance_fitting_process(n):
    for i in range(n):
        row: int
        column: int
        row, column = random_pixel()

        print(f'Pixel ({row}, {column})')
        plot_real_variance_against_real_intensity_for_pixel(row = row, column = column)
        plot_saved_k_fit_against_voltage_for_pixel(row = row, column = column)


if __name__ == '__main__':
    random_plot_variance_fitting_process(n = 3)
