# xray-simulation-group-8

This repository contains the analysis code for a project on empirical x-ray detector image simulation 
by UvA bachelor students Physics and Astronomy.

The goal of the project is to predict detector behaviour for different tube powers and acceleration voltages, using measured calibration data. The main outputs are:

- predicted mean intensity maps
- predicted variance maps
- randomly generated detector images based on the predicted mean and variance

## Data folders

- `2026-06-08_Detector_noise_calibration/`: old raw `.tif` images, 20 images per power-voltage setting.
- `Numpy image arrays/`: processed mean and variance arrays from the old 20-image data.
- `2026-06-15_numpy_image_arrays/`: processed mean and variance arrays from the newer 1000-image data.
- `Parameter maps/`: intermediate fit-parameter maps.
- `Final parameter maps/`: final parameter maps used by the prediction functions.

## Main files

- `fileIO.py`: reads raw `.tif` images and saved numpy arrays.
- `imageAnalysis.py`: creates mean and variance arrays from image stacks.
- `intensity.py`: plots single-pixel intensity and variance against tube power.
- `intensity_against_voltages.py`: plots single-pixel intensity and variance against acceleration voltage.
- `watt_param_maps.py`: fits intensity against tube power for all pixels.
- `slope_voltage_param_maps.py`: creates the final mean-intensity fit maps.
- `variance_mean_proportionality.py`: scalar variance-model checks.
- `variance_pixel_param_maps.py`: per-pixel variance-model maps.
- `final_func.py`: final functions for predicted mean and variance maps.
- `image_generator.py`: generates simulated detector images from the predicted maps.

## Requirements

The code uses Python with:

- `numpy`
- `matplotlib`
- `scipy`
- `Pillow`

The `manim/` folder contains optional animation code and requires `manim` if used.

## Credits

The Manim animation code in `manim/` was created by Charlie Mauer and Jaemin Lin.

## Acknowledgements

This project was supervised by Computational Imaging group and FleX-ray Lab at Centrum Wiskunde & Informatica (CWI) and detector data was collected using their X-ray machine.

## Reproducing results on poster

A poster was created with the results, which used:
```python
blur_sigma = 1.0
```

In `image_generator.py`, this is stored as:

```python
POSTER_BLUR_SIGMA = 1.0
```

Later code was added in the same file that can estimate a blur value from residual correlations in the old `.tif` images.

## Notes

The project has one historical orientation convention: some arrays were originally loaded transposed, and the code was built around that. `fileIO.py` documents this and keeps the existing behaviour so older maps and fits still work.

## License

This repository is released under the MIT License. See `LICENSE`.
