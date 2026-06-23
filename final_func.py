import os
import platform

import matplotlib.pyplot as plt
import numpy as np
from fileIO import *
dataset_type = '1000' # of '20' als je de oude wilt doen


if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
    slash: str = '/'
else: # windows
    slash: str = '\\'


POWER_VALUES: list = [10, 20, 30, 40]
VOLTAGE_VALUES: list = [30, 45, 60, 75, 90]


def project_path(*parts):
    dirname: str = os.path.dirname(__file__)
    return f'{dirname}{slash}' + f'{slash}'.join(parts)


def load_array(*parts):
    full_path: str = project_path(*parts)
    return np.load(full_path)


def darkfield_avg_array():
    return read_np_image_arrays(voltage_type='darkfield', filetype='npy', dist_type='avg')

# for comparing generated var models at P = 0, V = 0 with darkfield var directly from data
def darkfield_var_array():
    return read_np_image_arrays(voltage_type='darkfield', filetype='npy', dist_type='var')

# for comparing generated var models at desired P, V with flatfield var directly from data
def var_array(P, V):
    return read_np_image_arrays(voltage_type=f'{V}kV{slash}{P}W', filetype='npy', dist_type='var')


def relative_rmse(predicted_array, measured_array):
    mask: np.ndarray = (
        np.isfinite(predicted_array)
        & np.isfinite(measured_array)
    )
    difference_array: np.ndarray = predicted_array[mask] - measured_array[mask]
    rmse: float = np.sqrt(np.mean(a = difference_array**2))
    relative_rmse_percent: float = 100 * rmse / np.abs(np.mean(a = measured_array[mask]))

    return rmse, relative_rmse_percent


def relative_root_median_squared_error(predicted_array, measured_array):
    mask: np.ndarray = (
        np.isfinite(predicted_array)
        & np.isfinite(measured_array)
    )
    difference_array: np.ndarray = predicted_array[mask] - measured_array[mask]
    root_median_squared_error: float = np.sqrt(np.median(a = difference_array**2))
    relative_root_median_squared_error_percent: float = (
        100
        * root_median_squared_error
        / np.abs(np.median(a = measured_array[mask]))
    )

    return root_median_squared_error, relative_root_median_squared_error_percent


def relative_error_metrics(predicted_array, measured_array):
    rmse: float
    relative_rmse_percent: float
    rmse, relative_rmse_percent = relative_rmse(
        predicted_array = predicted_array,
        measured_array = measured_array
    )

    root_median_squared_error: float
    relative_root_median_squared_error_percent: float
    (
        root_median_squared_error,
        relative_root_median_squared_error_percent
    ) = relative_root_median_squared_error(
        predicted_array = predicted_array,
        measured_array = measured_array
    )

    return {
        'rmse': rmse,
        'relative_rmse_percent': relative_rmse_percent,
        'root_median_squared_error': root_median_squared_error,
        'relative_root_median_squared_error_percent': relative_root_median_squared_error_percent
    }


def poster_map_errors_for_setting(P, V):
    predicted_mean_array: np.ndarray = eind_baas(P = P, V = V)
    measured_mean_array: np.ndarray = read_np_image_arrays(
        voltage_type = f'{V}kV{slash}{P}W',
        filetype = 'npy',
        dist_type = 'avg'
    )
    predicted_variance_array: np.ndarray = var_eind_baas_per_pixel(P = P, V = V)
    predicted_global_variance_array: np.ndarray = var_eind_baas(P = P, V = V)
    measured_variance_array: np.ndarray = var_array(P = P, V = V)

    mean_metrics: dict = relative_error_metrics(
        predicted_array = predicted_mean_array,
        measured_array = measured_mean_array
    )

    variance_metrics: dict = relative_error_metrics(
        predicted_array = predicted_variance_array,
        measured_array = measured_variance_array
    )

    global_variance_metrics: dict = relative_error_metrics(
        predicted_array = predicted_global_variance_array,
        measured_array = measured_variance_array
    )

    return {
        'mean': mean_metrics,
        'variance_per_pixel': variance_metrics,
        'variance_global': global_variance_metrics
    }


def print_poster_map_errors(P = None, V = None):
    if P is not None and V is not None:
        metrics: dict = poster_map_errors_for_setting(P = P, V = V)

        print(f'Poster map errors, voltage = {V} kV, power = {P} W')
        print(
            'Mean intensity map:              '
            f"relative RMSE = {metrics['mean']['relative_rmse_percent']:.2f}%, "
            f"relative root median squared error = {metrics['mean']['relative_root_median_squared_error_percent']:.2f}%"
        )
        print(
            'Variance map, per-pixel model:   '
            f"relative RMSE = {metrics['variance_per_pixel']['relative_rmse_percent']:.2f}%, "
            f"relative root median squared error = {metrics['variance_per_pixel']['relative_root_median_squared_error_percent']:.2f}%"
        )
        print(
            'Variance map, global model:      '
            f"relative RMSE = {metrics['variance_global']['relative_rmse_percent']:.2f}%, "
            f"relative root median squared error = {metrics['variance_global']['relative_root_median_squared_error_percent']:.2f}%"
        )
        return

    mean_relative_rmse_percentages: list = []
    mean_relative_root_median_squared_error_percentages: list = []
    variance_relative_rmse_percentages: list = []
    variance_relative_root_median_squared_error_percentages: list = []
    global_variance_relative_rmse_percentages: list = []
    global_variance_relative_root_median_squared_error_percentages: list = []

    for voltage in VOLTAGE_VALUES:
        for power in POWER_VALUES:
            metrics: dict = poster_map_errors_for_setting(P = power, V = voltage)
            mean_relative_rmse_percentages.append(metrics['mean']['relative_rmse_percent'])
            mean_relative_root_median_squared_error_percentages.append(
                metrics['mean']['relative_root_median_squared_error_percent']
            )
            variance_relative_rmse_percentages.append(metrics['variance_per_pixel']['relative_rmse_percent'])
            variance_relative_root_median_squared_error_percentages.append(
                metrics['variance_per_pixel']['relative_root_median_squared_error_percent']
            )
            global_variance_relative_rmse_percentages.append(metrics['variance_global']['relative_rmse_percent'])
            global_variance_relative_root_median_squared_error_percentages.append(
                metrics['variance_global']['relative_root_median_squared_error_percent']
            )

    print('Poster map errors averaged over all 20 power-voltage settings')
    print(
        'Mean intensity map: '
        f'mean relative RMSE = {np.mean(a = mean_relative_rmse_percentages):.2f}% '
        f'(range {np.min(a = mean_relative_rmse_percentages):.2f}-{np.max(a = mean_relative_rmse_percentages):.2f}%), '
        f'mean relative root median squared error = {np.mean(a = mean_relative_root_median_squared_error_percentages):.2f}%'
    )
    print(
        'Variance map, per-pixel model: '
        f'mean relative RMSE = {np.mean(a = variance_relative_rmse_percentages):.2f}% '
        f'(range {np.min(a = variance_relative_rmse_percentages):.2f}-{np.max(a = variance_relative_rmse_percentages):.2f}%), '
        f'mean relative root median squared error = {np.mean(a = variance_relative_root_median_squared_error_percentages):.2f}%'
    )
    print(
        'Variance map, global model:    '
        f'mean relative RMSE = {np.mean(a = global_variance_relative_rmse_percentages):.2f}% '
        f'(range {np.min(a = global_variance_relative_rmse_percentages):.2f}-{np.max(a = global_variance_relative_rmse_percentages):.2f}%), '
        f'mean relative root median squared error = {np.mean(a = global_variance_relative_root_median_squared_error_percentages):.2f}%'
    )


# Mean intensity model:
# I(P, V) = I_dark + (alpha * V**2 + beta * V + gamma) * P
def eind_baas(P, V):
    alpha_array: np.ndarray = load_array('Final parameter maps', 'alpha_map.npy')
    beta_array: np.ndarray = load_array('Final parameter maps', 'beta_map.npy')
    gamma_array: np.ndarray = load_array('Final parameter maps', 'gamma_map.npy')
    darkfield_array: np.ndarray = darkfield_avg_array()

    I: np.ndarray = darkfield_array + (alpha_array * V**2 + beta_array * V + gamma_array) * P

    return I


# Global variance model:
# I_real(P, V) = I(P, V) - I_dark
# Var_total(P, V) = Var_dark + k(V) * I_real(P, V)
def var_eind_baas(P, V):
    k_fit_parameters: np.ndarray = load_array(
        'Final parameter maps',
        'variance_real_k_quadratic_coefficients.npy'
    )

    k: float = k_fit_parameters[0] * V**2 + k_fit_parameters[1] * V + k_fit_parameters[2]

    I: np.ndarray = eind_baas(P = P, V = V)
    I_real: np.ndarray = I - darkfield_avg_array()
    Var_I: np.ndarray = darkfield_var_array() + k * I_real

    return Var_I


# Per-pixel variance model:
# k_pixel(V) = q2_map * V**2 + q1_map * V + q0_map
# Var_total(P, V) = Var_dark + k_pixel(V) * I_real(P, V)
def var_eind_baas_per_pixel(P, V):
    q0_array: np.ndarray = load_array('Final parameter maps', 'variance_pixel_real_k_q0_map.npy')
    q1_array: np.ndarray = load_array('Final parameter maps', 'variance_pixel_real_k_q1_map.npy')
    q2_array: np.ndarray = load_array('Final parameter maps', 'variance_pixel_real_k_q2_map.npy')

    k_array: np.ndarray = q2_array * V**2 + q1_array * V + q0_array

    I: np.ndarray = eind_baas(P = P, V = V)
    I_real: np.ndarray = I - darkfield_avg_array()
    Var_I: np.ndarray = darkfield_var_array() + k_array * I_real

    return Var_I

# color_map function that will be called by the functions below
# you can input bottom and top percentile of values that are taken as bounds for the color scale, standard is 25/75
def color_map(array, title, colorbar_label, bottom_percentile = 25, top_percentile = 75):
    vmin: float = np.nanpercentile(array, bottom_percentile)
    vmax: float = np.nanpercentile(array, top_percentile)
    colorbar_label_with_percentiles: str = (
        f'{colorbar_label}\n'
        f'{bottom_percentile}th-{top_percentile}th percentile'
    )

    plt.figure()
    plt.imshow(X = array, vmin = vmin, vmax = vmax)
    plt.colorbar(label = colorbar_label_with_percentiles)
    plt.title(label = title)
    plt.xlabel(xlabel = r'$x$ (pixel)')
    plt.ylabel(ylabel = r'$y$ (pixel)')
    plt.show()


def color_map_eind_baas(P, V, bottom_percentile = 25, top_percentile = 75):
    I: np.ndarray = eind_baas(P = P, V = V)
    color_map(
        array = I,
        title = f'Predicted mean intensity map, voltage = {V} kV, power = {P} W',
        colorbar_label = r'predicted mean intensity $I$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_var_eind_baas(P, V, bottom_percentile = 25, top_percentile = 75):
    Var_I: np.ndarray = var_eind_baas(P = P, V = V)
    color_map(
        array = Var_I,
        title = f'Predicted variance map, global model, voltage = {V} kV, power = {P} W',
        colorbar_label = r'predicted variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_var_eindbaas_per_pixel(P, V, bottom_percentile = 25, top_percentile = 75):
    Var_I: np.ndarray = var_eind_baas_per_pixel(P = P, V = V)
    color_map(
        array = Var_I,
        title = f'Predicted variance map, per-pixel model, voltage = {V} kV, power = {P} W',
        colorbar_label = r'predicted variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_avg_array(P, V, bottom_percentile = 25, top_percentile = 75):
    avg_array: np.ndarray = read_np_image_arrays(
        voltage_type = f'{V}kV{slash}{P}W',
        filetype = 'npy',
        dist_type = 'avg'
    )
    color_map(
        array = avg_array,
        title = f'Measured mean intensity map, voltage = {V} kV, power = {P} W',
        colorbar_label = r'measured mean intensity $I$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_var_array(P, V, bottom_percentile = 25, top_percentile = 75):
    variance_array: np.ndarray = read_np_image_arrays(
        voltage_type = f'{V}kV{slash}{P}W',
        filetype = 'npy',
        dist_type = 'var'
    )
    color_map(
        array = variance_array,
        title = f'Measured variance map, voltage = {V} kV, power = {P} W',
        colorbar_label = r'measured variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_dark_field_var(bottom_percentile = 25, top_percentile = 75):
    color_map(
        array = darkfield_var_array(),
        title = 'Measured darkfield variance map',
        colorbar_label = r'measured darkfield variance',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )

def color_var(P, V, bottom_percentile = 25, top_percentile = 75):
    color_map(
        array = var_array(P, V),
        title = f'Measured variance map, voltage = {V} kV, power = {P} W',
        colorbar_label = r'measured variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


if __name__ == '__main__':
    print_poster_map_errors()
