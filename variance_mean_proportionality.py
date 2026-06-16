import os
import platform

import numpy as np

from fileIO import read_np_image_arrays


# This file creates the scalar voltage-dependent proportionality function:
# Var_total = k(V) * I_total + intercept
#
# The final variance function can later use:
# Var_total(P, V) = k(V) * I_total(P, V) + intercept(V)

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


def voltage_type(voltage, wattage):
    return f'{voltage}kV{slash}{wattage}W'


def linear_fit(x_values, y_values):
    x_values: np.ndarray = np.array(object = x_values, dtype = float)
    y_values: np.ndarray = np.array(object = y_values, dtype = float)

    fit_parameters: np.ndarray = np.polyfit(x = x_values, y = y_values, deg = 1)
    y_fit: np.ndarray = np.polyval(p = fit_parameters, x = x_values)

    residuals: np.ndarray = y_values - y_fit
    ss_res: float = np.sum(a = residuals**2)
    ss_tot: float = np.sum(a = (y_values - np.mean(a = y_values))**2)
    r_squared: float = 1 - ss_res / ss_tot
    rmse: float = np.sqrt(np.mean(a = residuals**2))

    slope: float = fit_parameters[0]
    intercept: float = fit_parameters[1]

    return slope, intercept, r_squared, rmse


def get_mean_intensity_and_variance(voltage, wattage):
    average_map: np.ndarray = read_np_image_arrays(
        voltage_type = voltage_type(voltage = voltage, wattage = wattage),
        dist_type = 'avg'
    )
    variance_map: np.ndarray = read_np_image_arrays(
        voltage_type = voltage_type(voltage = voltage, wattage = wattage),
        dist_type = 'var'
    )

    mask: np.ndarray = (
        np.isfinite(average_map)
        & np.isfinite(variance_map)
        & (average_map > 0)
        & (variance_map > 0)
    )

    mean_intensity: float = np.mean(a = average_map[mask])
    mean_variance: float = np.mean(a = variance_map[mask])

    return mean_intensity, mean_variance


def fit_k_values_for_voltages():
    k_values: np.ndarray = np.zeros(shape = len(voltages))
    intercepts: np.ndarray = np.zeros(shape = len(voltages))
    r_squared_values: np.ndarray = np.zeros(shape = len(voltages))
    relative_rmse_values: np.ndarray = np.zeros(shape = len(voltages))

    for i in range(len(voltages)):
        voltage: int = voltages[i]

        intensity_means: list = []
        variance_means: list = []

        for wattage in wattages:
            mean_intensity: float
            mean_variance: float
            mean_intensity, mean_variance = get_mean_intensity_and_variance(
                voltage = voltage,
                wattage = wattage
            )

            intensity_means.append(mean_intensity)
            variance_means.append(mean_variance)

        slope: float
        intercept: float
        r_squared: float
        rmse: float
        slope, intercept, r_squared, rmse = linear_fit(
            x_values = intensity_means,
            y_values = variance_means
        )

        k_values[i] = slope
        intercepts[i] = intercept
        r_squared_values[i] = r_squared
        relative_rmse_values[i] = 100 * rmse / np.mean(a = variance_means)

    return k_values, intercepts, r_squared_values, relative_rmse_values


def fit_k_as_function_of_voltage():
    k_values: np.ndarray
    intercepts: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    k_values, intercepts, r_squared_values, relative_rmse_values = fit_k_values_for_voltages()

    # k(V) = q2 * V**2 + q1 * V + q0
    k_fit_parameters: np.ndarray = np.polyfit(x = kV, y = k_values, deg = 2)
    k_fit: np.ndarray = np.polyval(p = k_fit_parameters, x = kV)

    # intercept(V) = r2 * V**2 + r1 * V + r0
    intercept_fit_parameters: np.ndarray = np.polyfit(x = kV, y = intercepts, deg = 2)

    residuals: np.ndarray = k_values - k_fit
    ss_res: float = np.sum(a = residuals**2)
    ss_tot: float = np.sum(a = (k_values - np.mean(a = k_values))**2)
    r_squared: float = 1 - ss_res / ss_tot
    rmse: float = np.sqrt(np.mean(a = residuals**2))

    return k_fit_parameters, intercept_fit_parameters, k_values, intercepts, r_squared_values, relative_rmse_values, r_squared, rmse


def print_k_fit_report():
    k_fit_parameters: np.ndarray
    k_values: np.ndarray
    intercept_fit_parameters: np.ndarray
    intercepts: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    r_squared: float
    rmse: float
    k_fit_parameters, intercept_fit_parameters, k_values, intercepts, r_squared_values, relative_rmse_values, r_squared, rmse = fit_k_as_function_of_voltage()

    print('Fit per voltage: Var_total = k * I_total + intercept')
    print('V(kV)        k      intercept       R^2    rel RMSE')

    for i in range(len(voltages)):
        print(f'{voltages[i]:5d} {k_values[i]:9.5f} {intercepts[i]:14.3f} {r_squared_values[i]:9.6f} {relative_rmse_values[i]:9.3f}%')

    print()
    print('Quadratic voltage fit: k(V) = q2 * V**2 + q1 * V + q0')
    print(f'q2 = {k_fit_parameters[0]}')
    print(f'q1 = {k_fit_parameters[1]}')
    print(f'q0 = {k_fit_parameters[2]}')
    print(f'R^2 = {r_squared}')
    print(f'RMSE = {rmse}')
    print()
    print('Quadratic voltage fit: intercept(V) = r2 * V**2 + r1 * V + r0')
    print(f'r2 = {intercept_fit_parameters[0]}')
    print(f'r1 = {intercept_fit_parameters[1]}')
    print(f'r0 = {intercept_fit_parameters[2]}')


def save_k_fit_parameters():
    k_fit_parameters: np.ndarray
    intercept_fit_parameters: np.ndarray
    k_values: np.ndarray
    intercepts: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    r_squared: float
    rmse: float
    k_fit_parameters, intercept_fit_parameters, k_values, intercepts, r_squared_values, relative_rmse_values, r_squared, rmse = fit_k_as_function_of_voltage()

    output_folder: str = project_path('Final parameter maps')
    os.makedirs(name = output_folder, exist_ok = True)

    np.save(file = os.path.join(output_folder, 'variance_k_quadratic_coefficients.npy'), arr = k_fit_parameters)
    np.save(file = os.path.join(output_folder, 'variance_intercept_quadratic_coefficients.npy'), arr = intercept_fit_parameters)
    np.save(file = os.path.join(output_folder, 'variance_k_values.npy'), arr = k_values)



print_k_fit_report()
save_k_fit_parameters()
