import glob
import os
import random

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

from final_func import (
      POWER_VALUES,
      VOLTAGE_VALUES,
      color_map,
      eind_baas,
      relative_root_median_squared_error,
      relative_rmse,
      var_eind_baas_per_pixel
)


# Outline:
# Take the predicted mean image, then add spatially correlated Gaussian noise
# using the predicted standard deviation for every pixel individually.


def standard_deviation_from_variance(variance_array):
      positive_variance_array: np.ndarray = np.clip(a = variance_array, a_min = 0, a_max = None)

      return np.sqrt(positive_variance_array)


def correlated_standard_normal_noise(shape, blur_sigma = 1.0):
      white_noise: np.ndarray = np.random.normal(loc = 0, scale = 1, size = shape)
      correlated_noise: np.ndarray = gaussian_filter(
            input = white_noise,
            sigma = blur_sigma,
            mode = 'reflect'
      )
      correlated_noise = correlated_noise - np.nanmean(a = correlated_noise)
      correlated_noise_standard_deviation: float = np.nanstd(a = correlated_noise)

      if correlated_noise_standard_deviation == 0:
            return correlated_noise

      return correlated_noise / correlated_noise_standard_deviation


# Create randomly made array with per-pixel variance model and spatially correlated noise.
def ran_parameters_to_image_per_pixel_model_correlated_noise(P, V, blur_sigma = 1.0):
      mean_array = eind_baas(P, V)
      sigma_array = standard_deviation_from_variance(variance_array = var_eind_baas_per_pixel(P, V))
      correlated_noise = correlated_standard_normal_noise(
            shape = mean_array.shape,
            blur_sigma = blur_sigma
      )

      return mean_array + correlated_noise * sigma_array


# Create color map of randomly made array with per-pixel variance model and spatially correlated noise.
def color_map_rand_parameters_to_image_per_pixel_model_correlated_noise(
      P,
      V,
      blur_sigma = 1.0,
      bottom_percentile = 25,
      top_percentile = 75
):
      color_map(
            array = ran_parameters_to_image_per_pixel_model_correlated_noise(
                  P = P,
                  V = V,
                  blur_sigma = blur_sigma
            ),
            title = (
                  f'Randomly generated image, per-pixel model with correlated noise, '
                  f'voltage = {V} kV, power = {P} W'
            ),
            colorbar_label = r'generated intensity $I$',
            bottom_percentile = bottom_percentile,
            top_percentile = top_percentile
      )


# Return one randomly selected raw image from the old 20-image .tif dataset.
def old_tif_paths(P, V):
      dirname: str = os.path.dirname(__file__)
      folder_path: str = os.path.join(
            dirname,
            '2026-06-08_Detector_noise_calibration',
            f'{V}kV',
            f'{P}W'
      )
      tif_paths: list = sorted(glob.glob(os.path.join(folder_path, 'scan_*.tif')))

      if len(tif_paths) == 0:
            raise FileNotFoundError(f'No old .tif scan images found in {folder_path}')

      return tif_paths


# Return one randomly selected raw image from the old 20-image .tif dataset.
def random_old_tif_image(P, V):
      tif_paths: list = old_tif_paths(P = P, V = V)
      selected_tif_path: str = random.choice(tif_paths)
      image_array: np.ndarray = np.array(object = Image.open(fp = selected_tif_path), dtype = float).T

      return image_array, selected_tif_path


# Create comparison color map from one randomly selected old raw .tif image.
def color_map_random_old_tif_image(P, V, bottom_percentile = 25, top_percentile = 75):
      image_array: np.ndarray
      selected_tif_path: str
      image_array, selected_tif_path = random_old_tif_image(P = P, V = V)
      selected_tif_name: str = os.path.basename(selected_tif_path)

      color_map(
            array = image_array,
            title = f'Random measured raw image, {selected_tif_name}, voltage = {V} kV, power = {P} W',
            colorbar_label = r'measured raw intensity $I$',
            bottom_percentile = bottom_percentile,
            top_percentile = top_percentile
      )


# Load all old raw .tif images for a setting into a stack with shape:
# (number_of_images, image_height, image_width).
def old_tif_image_stack(P, V):
      tif_paths: list = old_tif_paths(P = P, V = V)
      image_stack: list = []

      for tif_path in tif_paths:
            image_array: np.ndarray = np.array(object = Image.open(fp = tif_path), dtype = np.float32).T
            image_stack.append(image_array)

      return np.stack(arrays = image_stack, axis = 0)


def old_tif_residual_stack(P, V):
      image_stack: np.ndarray = old_tif_image_stack(P = P, V = V)
      mean_image: np.ndarray = np.mean(a = image_stack, axis = 0)
      residual_stack: np.ndarray = image_stack - mean_image

      return residual_stack


def generated_image_stack_per_pixel_model_correlated_noise(
      P,
      V,
      number_of_images = 20,
      blur_sigma = 1.0
):
      generated_images: list = []
      mean_array: np.ndarray = eind_baas(P, V)
      sigma_array: np.ndarray = standard_deviation_from_variance(
            variance_array = var_eind_baas_per_pixel(P, V)
      )

      for i in range(number_of_images):
            correlated_noise: np.ndarray = correlated_standard_normal_noise(
                  shape = mean_array.shape,
                  blur_sigma = blur_sigma
            )
            generated_image: np.ndarray = mean_array + correlated_noise * sigma_array
            generated_images.append(generated_image)

      return np.stack(arrays = generated_images, axis = 0)


def generated_residual_stack_per_pixel_model_correlated_noise(
      P,
      V,
      number_of_images = 20,
      blur_sigma = 1.0
):
      mean_array: np.ndarray = eind_baas(P, V)
      generated_image_stack: np.ndarray = generated_image_stack_per_pixel_model_correlated_noise(
            P = P,
            V = V,
            number_of_images = number_of_images,
            blur_sigma = blur_sigma
      )

      return generated_image_stack - mean_array


def spatial_correlation_for_offset(residual_stack, row_offset, column_offset, sampling_step = 4):
      first_values: np.ndarray = residual_stack[
            :,
            0:residual_stack.shape[1] - row_offset:sampling_step,
            0:residual_stack.shape[2] - column_offset:sampling_step
      ]
      second_values: np.ndarray = residual_stack[
            :,
            row_offset::sampling_step,
            column_offset::sampling_step
      ]

      valid: np.ndarray = np.isfinite(first_values) & np.isfinite(second_values)
      first_values = first_values[valid].astype(float)
      second_values = second_values[valid].astype(float)

      first_values = first_values - np.mean(a = first_values)
      second_values = second_values - np.mean(a = second_values)

      numerator: float = np.sum(a = first_values * second_values)
      denominator: float = np.sqrt(
            np.sum(a = first_values**2)
            * np.sum(a = second_values**2)
      )

      if denominator == 0:
            return np.nan

      return numerator / denominator


def poster_image_errors_for_setting(P, V, blur_sigma = 1.0):
      measured_image_stack: np.ndarray = old_tif_image_stack(P = P, V = V)
      generated_image_stack: np.ndarray = generated_image_stack_per_pixel_model_correlated_noise(
            P = P,
            V = V,
            number_of_images = measured_image_stack.shape[0],
            blur_sigma = blur_sigma
      )

      image_relative_rmse_percentages: list = []
      image_relative_root_median_squared_error_percentages: list = []
      for image_index in range(measured_image_stack.shape[0]):
            image_rmse: float
            image_relative_rmse_percent: float
            image_rmse, image_relative_rmse_percent = relative_rmse(
                  predicted_array = generated_image_stack[image_index],
                  measured_array = measured_image_stack[image_index]
            )
            image_root_median_squared_error: float
            image_relative_root_median_squared_error_percent: float
            (
                  image_root_median_squared_error,
                  image_relative_root_median_squared_error_percent
            ) = relative_root_median_squared_error(
                  predicted_array = generated_image_stack[image_index],
                  measured_array = measured_image_stack[image_index]
            )
            image_relative_rmse_percentages.append(image_relative_rmse_percent)
            image_relative_root_median_squared_error_percentages.append(
                  image_relative_root_median_squared_error_percent
            )

      old_residual_stack: np.ndarray = old_tif_residual_stack(P = P, V = V)
      mean_array: np.ndarray = eind_baas(P, V)
      generated_residual_stack: np.ndarray = generated_image_stack - mean_array

      measured_correlation: float = spatial_correlation_for_offset(
            residual_stack = old_residual_stack,
            row_offset = 0,
            column_offset = 1
      )
      generated_correlation: float = spatial_correlation_for_offset(
            residual_stack = generated_residual_stack,
            row_offset = 0,
            column_offset = 1
      )

      return (
            np.mean(a = image_relative_rmse_percentages),
            np.mean(a = image_relative_root_median_squared_error_percentages),
            measured_correlation,
            generated_correlation
      )


def print_poster_image_errors(P = None, V = None, blur_sigma = 1.0, random_seed = 0):
      if random_seed is not None:
            np.random.seed(random_seed)

      if P is not None and V is not None:
            image_relative_rmse_percent: float
            image_relative_root_median_squared_error_percent: float
            measured_correlation: float
            generated_correlation: float
            (
                  image_relative_rmse_percent,
                  image_relative_root_median_squared_error_percent,
                  measured_correlation,
                  generated_correlation
            ) = poster_image_errors_for_setting(P = P, V = V, blur_sigma = blur_sigma)

            print(f'Poster generated-image metrics, voltage = {V} kV, power = {P} W')
            print(f'Mean single-image relative RMSE over 20 TIFFs = {image_relative_rmse_percent:.2f}%')
            print(
                  'Mean single-image relative root median squared error over 20 TIFFs = '
                  f'{image_relative_root_median_squared_error_percent:.2f}%'
            )
            print(f'Measured nearest-neighbour noise correlation = {measured_correlation:.3f}')
            print(f'Generated nearest-neighbour noise correlation = {generated_correlation:.3f}')
            return

      image_relative_rmse_percentages: list = []
      image_relative_root_median_squared_error_percentages: list = []
      measured_correlations: list = []
      generated_correlations: list = []

      for voltage in VOLTAGE_VALUES:
            for power in POWER_VALUES:
                  (
                        image_relative_rmse_percent,
                        image_relative_root_median_squared_error_percent,
                        measured_correlation,
                        generated_correlation
                  ) = poster_image_errors_for_setting(
                        P = power,
                        V = voltage,
                        blur_sigma = blur_sigma
                  )
                  image_relative_rmse_percentages.append(image_relative_rmse_percent)
                  image_relative_root_median_squared_error_percentages.append(
                        image_relative_root_median_squared_error_percent
                  )
                  measured_correlations.append(measured_correlation)
                  generated_correlations.append(generated_correlation)

      print('Poster generated-image metrics averaged over all 20 power-voltage settings')
      print(
            'Mean single-image relative RMSE over all old TIFFs = '
            f'{np.mean(a = image_relative_rmse_percentages):.2f}%'
      )
      print(
            'Mean single-image relative root median squared error over all old TIFFs = '
            f'{np.mean(a = image_relative_root_median_squared_error_percentages):.2f}%'
      )
      print(
            'Measured nearest-neighbour noise correlation = '
            f'{np.mean(a = measured_correlations):.3f}'
      )
      print(
            'Generated nearest-neighbour noise correlation = '
            f'{np.mean(a = generated_correlations):.3f}'
      )


if __name__ == '__main__':
      print_poster_image_errors(blur_sigma = 1.0)
