# builds the scalar variance model by fitting one global k value for each voltage.
import os
import platform

import matplotlib.pyplot as plt
import numpy as np

from fileIO import read_np_image_arrays


# this file creates the scalar voltage-dependent proportionality function for
# the real x-ray signal, not for the darkfield offset:
#
# Var_real = k(V) * I_real
#
# with:
# I_real = I_total - I_dark
# Var_real = Var_total - Var_dark
#
# The final variance function should use:
# Var_total(P, V) = Var_dark + k(V) * I_real(P, V)

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


def get_real_mean_intensity_and_variance(voltage, wattage):
    average_map: np.ndarray = read_np_image_arrays(
        voltage_type = voltage_type(voltage = voltage, wattage = wattage),
        dist_type = 'avg'
    )
    variance_map: np.ndarray = read_np_image_arrays(
        voltage_type = voltage_type(voltage = voltage, wattage = wattage),
        dist_type = 'var'
    )
    darkfield_average_map: np.ndarray = read_np_image_arrays(
        voltage_type = 'darkfield',
        dist_type = 'avg'
    )
    darkfield_variance_map: np.ndarray = read_np_image_arrays(
        voltage_type = 'darkfield',
        dist_type = 'var'
    )

    real_intensity_map: np.ndarray = average_map - darkfield_average_map
    real_variance_map: np.ndarray = variance_map - darkfield_variance_map

    mask: np.ndarray = (
        np.isfinite(real_intensity_map)
        & np.isfinite(real_variance_map)
        & (real_intensity_map > 0)
    )

    mean_real_intensity: float = np.mean(a = real_intensity_map[mask])
    mean_real_variance: float = np.mean(a = real_variance_map[mask])

    return mean_real_intensity, mean_real_variance


def fit_slope_through_origin(x_values, y_values):
    x_values: np.ndarray = np.array(object = x_values, dtype = float)
    y_values: np.ndarray = np.array(object = y_values, dtype = float)

    valid: np.ndarray = np.isfinite(x_values) & np.isfinite(y_values) & (x_values > 0)
    x_values = x_values[valid]
    y_values = y_values[valid]

    slope: float = np.sum(a = x_values * y_values) / np.sum(a = x_values**2)
    y_fit: np.ndarray = slope * x_values

    residuals: np.ndarray = y_values - y_fit
    ss_res: float = np.sum(a = residuals**2)
    ss_tot: float = np.sum(a = (y_values - np.mean(a = y_values))**2)
    r_squared: float = 1 - ss_res / ss_tot
    rmse: float = np.sqrt(np.mean(a = residuals**2))

    return slope, r_squared, rmse


def fit_k_values_for_voltages():
    k_values: np.ndarray = np.zeros(shape = len(voltages))
    r_squared_values: np.ndarray = np.zeros(shape = len(voltages))
    relative_rmse_values: np.ndarray = np.zeros(shape = len(voltages))

    for i in range(len(voltages)):
        voltage: int = voltages[i]

        real_intensity_means: list = []
        real_variance_means: list = []

        for wattage in wattages:
            mean_real_intensity: float
            mean_real_variance: float
            mean_real_intensity, mean_real_variance = get_real_mean_intensity_and_variance(
                voltage = voltage,
                wattage = wattage
            )

            real_intensity_means.append(mean_real_intensity)
            real_variance_means.append(mean_real_variance)

        slope: float
        r_squared: float
        rmse: float
        slope, r_squared, rmse = fit_slope_through_origin(
            x_values = real_intensity_means,
            y_values = real_variance_means
        )

        k_values[i] = slope
        r_squared_values[i] = r_squared
        relative_rmse_values[i] = 100 * rmse / np.mean(a = real_variance_means)

    return k_values, r_squared_values, relative_rmse_values


def get_real_intensity_and_variance_means_for_voltage(voltage):
    real_intensity_means: list = []
    real_variance_means: list = []

    for wattage in wattages:
        mean_real_intensity: float
        mean_real_variance: float
        mean_real_intensity, mean_real_variance = get_real_mean_intensity_and_variance(
            voltage = voltage,
            wattage = wattage
        )

        real_intensity_means.append(mean_real_intensity)
        real_variance_means.append(mean_real_variance)

    return np.array(object = real_intensity_means, dtype = float), np.array(object = real_variance_means, dtype = float)


def fit_k_as_function_of_voltage():
    k_values: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    k_values, r_squared_values, relative_rmse_values = fit_k_values_for_voltages()

    # k(V) = q2 * V**2 + q1 * V + q0
    k_fit_parameters: np.ndarray = np.polyfit(x = kV, y = k_values, deg = 2)
    k_fit: np.ndarray = np.polyval(p = k_fit_parameters, x = kV)

    residuals: np.ndarray = k_values - k_fit
    ss_res: float = np.sum(a = residuals**2)
    ss_tot: float = np.sum(a = (k_values - np.mean(a = k_values))**2)
    r_squared: float = 1 - ss_res / ss_tot
    rmse: float = np.sqrt(np.mean(a = residuals**2))

    return k_fit_parameters, k_values, r_squared_values, relative_rmse_values, r_squared, rmse


def plot_real_variance_against_real_mean_with_fit():
    colors: list = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple']

    plt.figure()

    for i in range(len(voltages)):
        voltage: int = voltages[i]

        real_intensity_means: np.ndarray
        real_variance_means: np.ndarray
        real_intensity_means, real_variance_means = get_real_intensity_and_variance_means_for_voltage(voltage = voltage)

        slope: float
        r_squared: float
        rmse: float
        slope, r_squared, rmse = fit_slope_through_origin(
            x_values = real_intensity_means,
            y_values = real_variance_means
        )

        intensity_fit: np.ndarray = np.linspace(
            start = 0,
            stop = np.max(a = real_intensity_means),
            num = 100
        )
        variance_fit: np.ndarray = slope * intensity_fit

        plt.plot(
            real_intensity_means,
            real_variance_means,
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

    plt.title(label = 'Real variance against real mean intensity')
    plt.xlabel(xlabel = r'Real mean intensity $I - I_{\mathrm{dark}}$')
    plt.ylabel(ylabel = r'Real variance $\mathrm{Var}(I) - \mathrm{Var}_{\mathrm{dark}}$')
    plt.legend()
    plt.show()


def plot_k_against_voltage_with_fit():
    k_fit_parameters: np.ndarray
    k_values: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    r_squared: float
    rmse: float
    k_fit_parameters, k_values, r_squared_values, relative_rmse_values, r_squared, rmse = fit_k_as_function_of_voltage()

    kV_fit: np.ndarray = np.linspace(start = np.min(a = kV), stop = np.max(a = kV), num = 100)
    k_fit: np.ndarray = np.polyval(p = k_fit_parameters, x = kV_fit)

    plt.figure()
    plt.plot(kV, k_values, 'o', label = 'fitted k values')
    plt.plot(kV_fit, k_fit, '-', label = 'quadratic fit')
    plt.title(label = 'Real-signal proportionality constant against voltage')
    plt.xlabel(xlabel = 'Voltage (kV)')
    plt.ylabel(ylabel = r'$k$ in $\mathrm{Var}_{\mathrm{real}} = k I_{\mathrm{real}}$')
    plt.legend()
    plt.show()


def print_k_fit_report():
    k_fit_parameters: np.ndarray
    k_values: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    r_squared: float
    rmse: float
    k_fit_parameters, k_values, r_squared_values, relative_rmse_values, r_squared, rmse = fit_k_as_function_of_voltage()

    print('Fit per voltage: Var_real = k * I_real')
    print('V(kV)        k       R^2    rel RMSE')

    for i in range(len(voltages)):
        print(f'{voltages[i]:5d} {k_values[i]:9.5f} {r_squared_values[i]:9.6f} {relative_rmse_values[i]:9.3f}%')

    print()
    print('Quadratic voltage fit: k(V) = q2 * V**2 + q1 * V + q0')
    print(f'q2 = {k_fit_parameters[0]}')
    print(f'q1 = {k_fit_parameters[1]}')
    print(f'q0 = {k_fit_parameters[2]}')
    print(f'R^2 = {r_squared}')
    print(f'RMSE = {rmse}')


def save_k_fit_parameters():
    k_fit_parameters: np.ndarray
    k_values: np.ndarray
    r_squared_values: np.ndarray
    relative_rmse_values: np.ndarray
    r_squared: float
    rmse: float
    k_fit_parameters, k_values, r_squared_values, relative_rmse_values, r_squared, rmse = fit_k_as_function_of_voltage()

    output_folder: str = project_path('Final parameter maps')
    os.makedirs(name = output_folder, exist_ok = True)

    np.save(file = os.path.join(output_folder, 'variance_real_k_quadratic_coefficients.npy'), arr = k_fit_parameters)
    np.save(file = os.path.join(output_folder, 'variance_real_k_values.npy'), arr = k_values)

    # Keep the old filename usable, but with the corrected real-signal meaning.
    np.save(file = os.path.join(output_folder, 'variance_k_quadratic_coefficients.npy'), arr = k_fit_parameters)
    np.save(file = os.path.join(output_folder, 'variance_k_values.npy'), arr = k_values)


if __name__ == '__main__':
    print_k_fit_report()
    save_k_fit_parameters()
    plot_real_variance_against_real_mean_with_fit()
    plot_k_against_voltage_with_fit()
