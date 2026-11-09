# Hybrid source and receiver experiment
Run from the Optics621 directory. For results without running any solver, open manuscript/FMCW_LiDAR.pdf and hybrid/output/*.png. Use the PDF figures for presentations. These are simulations of a proposed geometry, not measured performance.

## Reproduce
Use Python 3.12 and a clean environment:
```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install 'tidy3d==2.12.2'
export OPENBLAS_NUM_THREADS=1
python run_tests.py
python hybrid/source.py
python hybrid/source.py --step .025 --out hybrid/fine
python -m hybrid.ranging
python -m hybrid.figures
```
The mode solves are local; no PhotonForge, GDS, credentials or paid cloud FDTD is needed. Only the first two solver commands need Tidy3D. The original wide-area estimator and experiments remain available via python -m fmcw.cli --help. For custom geometries use a separate --out directory to preserve published results.

## What crosses the model boundary
The optical solver interpolates all three components onto a common grid, selects the core-confined x-polarised mode and finite-differences its effective index across ±0.1% frequency. Material indices are held constant, so the group index includes waveguide but not material dispersion. The DC solver uses harmonic face conductances, insulating outer walls and differential ±0.5 V perfect conductors, 1 µm wide. SiN, oxide, silicon and air have assumed relative static permittivities 7.5, 3.9, 11.7 and 1; the LN lateral and vertical values are assumed 28 and 43. The silicon is treated as a dielectric, not a grounded backplane. The solver uses square cells.

In nondispersive cavity perturbation, the fractional frequency shift is minus one half the electric-field-weighted change in permittivity divided by total electric energy. For the assumed local crystal orientation we retain the extraordinary diagonal term only: delta epsilon_xx = -ne^4 r33 E_bias,x. The effective active fraction multiplies the signed overlap. A real ring requires angular integration with crystal axes and electrode polarity; opposing segments can cancel. The estimated radius only represents equal round-trip delay at the paper's 102 GHz FSR. No optical absorption by tungsten, feedback dynamics or chirp linearity is predicted. The 12% literature participation and our nondispersive electric-energy fraction need not share a normalisation.

## Numerical and physical limits
At 50 and 25 nm the gain is 102 and 114 MHz/V. This is NOT mesh converged at 3%; electrode corners and material interfaces matter. The estimated 50 nm gap trend at 50% effective coverage is 132 to 69 MHz/V for gaps from 3 to 6 µm. This sweep changes the bias field only. The reference measurement (Snigirev et al., Nature 615, 411, 2023, DOI 10.1038/s41586-023-05724-2) is a locked-laser response, not a fitted input. For design budgeting prefer its measured coefficient with its stated operating conditions. Model sensitivity is not a superior device claim.

At 5 Vpp the coarse-grid scenario supplies the bandwidth to fmcw.Config; calibration then fits a synthetic sweep independently. Each point uses one stationary target, assumed linear locking and equal launch power. Foreign timing and phase are random per seed. All three methods share seeds; the two coded methods see identical receiver data. Wrong code changes only the template. Conditional gate 47 to 53 m; no detection threshold, no claims of acquisition or probability of detection. Source and foreign linewidths are both 50 kHz. See raw rows and configuration in output/. With 40 trials the upper tails and RMS estimates are uncertain. No velocity reconstruction or rare-error assurance.
