import os
import platform

import matplotlib.pyplot as plt
import numpy as np


if (platform.system() == 'Linux' or platform.system() == 'Darwin'): # darwin = macos
    slash: str = '/'
else: # windows
    slash: str = '\\'


def project_path(*parts):
    dirname: str = os.path.dirname(__file__)
    return f'{dirname}{slash}' + f'{slash}'.join(parts)


def load_array(*parts):
    full_path: str = project_path(*parts)
    return np.load(full_path)


def darkfield_avg_array():
    return load_array('Numpy image arrays', 'darkfield', 'avg_array_darkield.npy')

# for comparing generated var models at P = 0, V = 0 with darkfield var directly from data
def darkfield_var_array():
    return load_array('Numpy image arrays', 'darkfield', 'var_array_darkield.npy')

# for comparing generated var models at desired P, V with flatfield var directly from data
def var_array(P, V):
    return load_array('Numpy image arrays', f'{V}kV', f'{P}W', f'var_array_{V}kV{P}W.npy')


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
    plt.xlabel(xlabel = r'$y$ (pixel)')
    plt.ylabel(ylabel = r'$x$ (pixel)')
    plt.show()


def color_map_eind_baas(P, V, bottom_percentile = 25, top_percentile = 75):
    I: np.ndarray = eind_baas(P = P, V = V)
    color_map(
        array = I,
        title = f'Mean intensity map, generated, {V} kV, {P} W',
        colorbar_label = r'mean intensity $I$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_var_eind_baas(P, V, bottom_percentile = 25, top_percentile = 75):
    Var_I: np.ndarray = var_eind_baas(P = P, V = V)
    color_map(
        array = Var_I,
        title = f'Variance map, generated global model, {V} kV, {P} W',
        colorbar_label = r'variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_var_eindbaas_per_pixel(P, V, bottom_percentile = 25, top_percentile = 75):
    Var_I: np.ndarray = var_eind_baas_per_pixel(P = P, V = V)
    color_map(
        array = Var_I,
        title = f'Variance map, generated per-pixel model, {V} kV, {P} W',
        colorbar_label = r'variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_avg_array(P, V, bottom_percentile = 25, top_percentile = 75):
    avg_array: np.ndarray = load_array(
        'Numpy image arrays',
        f'{V}kV',
        f'{P}W',
        f'avg_array_{V}kV{P}W.npy'
    )
    color_map(
        array = avg_array,
        title = f'Average intensity map, measured, {V} kV, {P} W',
        colorbar_label = r'mean intensity $I$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_map_var_array(P, V, bottom_percentile = 25, top_percentile = 75):
    var_array: np.ndarray = load_array(
        'Numpy image arrays',
        f'{V}kV',
        f'{P}W',
        f'var_array_{V}kV{P}W.npy'
    )
    color_map(
        array = var_array,
        title = f'Variance map, measured, {V} kV, {P} W',
        colorbar_label = r'variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


def color_dark_field_var(bottom_percentile = 25, top_percentile = 75):
    color_map(
        array = darkfield_var_array(),
        title = 'Variance map, measured darkfield',
        colorbar_label = r'darkfield variance',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )

def color_var(P, V, bottom_percentile = 25, top_percentile = 75):
    color_map(
        array = var_array(P, V),
        title = f'Variance map, measured at {P}W, {V}kV',
        colorbar_label = r'variance $\mathrm{Var}(I)$',
        bottom_percentile = bottom_percentile,
        top_percentile = top_percentile
    )


# remember, standard percentiles taken as a color bounds are 25, 75
# but e.g. input (bottom_percentile = 10, top_percentile = 90) if you want those bounds
if __name__ == '__main__':
    color_map_var_eind_baas(P = 40, V = 90)
    color_map_var_eindbaas_per_pixel(P = 40, V = 90)
    #color_dark_field_var()
    color_var(P = 40, V = 90)
