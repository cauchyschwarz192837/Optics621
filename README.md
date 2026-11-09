**Current upgrade:** [source and ranging guide](hybrid/README.md) · [revised manuscript](manuscript/FMCW_LiDAR.pdf). Earlier reports below describe the baseline release.

# Intensity-coded FMCW LiDAR: complete computational project

**Authors: Andre and Colin.**

We investigate whether a separate coded intensity modulator reduces interference-induced range error at fixed average launched power, sweep duration and receiver bandwidth. The answer is allowed to be negative. A second comparison holds available source power fixed, revealing modulation losses.

## Assignment review (5 November 2026)

```bash
python requirements_review.py
python run_submission_plan.py
# Run the substantial selected campaign only when ready:
python run_submission_plan.py --execute
```

The new analytical outputs are in `results/requirements_review`. The 10-case submission plan is a smaller alternative to the broad original campaign, not a completed result. The original 14 physics tests were rerun successfully after this revision.

## 1. Install and verify

From the extracted `optics_project` folder, on macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python run_tests.py
python -m fmcw.cli baseline
```

Use Python 3.11 or newer. The delivered core was actually tested with Python 3.12.14. On Windows activate with `.venv\Scripts\Activate.ps1`; the Python commands are unchanged. `run_tests.py` uses standard-library unittest. Optional development dependencies add pytest and Jupyter:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python -m ipykernel install --user --name optics-fmcw --display-name "Optics FMCW"
jupyter lab
```

After the complete installation succeeds:

```bash
python -m pip check
python -m pip freeze > requirements-local-lock.txt
```

## 2. File map

| Path | Responsibility |
|---|---|
| `config/*.json` | Explicit SI-unit parameters and seeds |
| `fmcw/config.py` | Defaults, validation, constants, serialization |
| `fmcw/source.py` | Analytical beat phases and exact jointly sampled Wiener histories |
| `fmcw/modulator.py` | Finite-rise codes, nonlinear complex MZM, launched/source power |
| `fmcw/simulation.py` | Delayed target, independent interferer, coherent scatterers |
| `fmcw/receiver.py` | Shot/electronic noise, causal oversampled filtering, ADC, PSD weighting |
| `fmcw/calibration.py` | Independent synthetic coherent MZM and delay-MZI calibration |
| `fmcw/estimation.py` | Global quadrature-template search, continuous refinement, FFT initializer, Fisher bound |
| `fmcw/experiments.py` | Demo, Monte Carlo, figures, metrics, convergence and bias/drive sweep |
| `fmcw/ambiguity.py` | Asynchronous full-field cross-correlation vs beat-frequency offset |
| `fmcw/metrics.py` | Bias, precision, RMSE, gross errors and binomial intervals |
| `fmcw/cli.py` | Command-line entry point |
| `component/solve_component.py` | Optional local Tidy3D modes, EO perturbation, convergence, Vπ export |
| `component/compare_components.py` | Fixed-voltage component comparison and system configs |
| `run_campaign.py` | Selected primary, power, bias/drive and robustness experiment plans |
| `tests/test_physics.py` | Meaningful physical and numerical checks |
| `notebooks/01_walkthrough.ipynb` | Thin interactive guide calling the same tested modules |
| `docs/` | Physics, interpretation, experiment protocol and source references |
| `results/` | Executed examples, raw records, plots and verification evidence |

## 3. Run in this order

### Stage A: clean baseline

```bash
python -m fmcw.cli demo --config config/noiseless.json --out results/my_noiseless
python -m fmcw.cli demo --config config/white_noise.json --out results/my_white_noise
python -m fmcw.cli demo --config config/baseline.json --out results/my_demo
```

Read `analytical_baselines.json`, `estimates.csv`, `calibration.json`, and `demo.png`. Each `.npz` stores ADC and processed waveforms. One demo is one realization; its error is not an RMSE.

Expected analytical values for the default 50 m target:

| Quantity | Value |
|---|---:|
| Chirp slope | 5 × 10¹² Hz/s |
| Round-trip delay | 333.564 ns |
| Beat frequency | 1.667820 MHz |
| Optical-sweep resolution scale | 0.299792 m |
| ADC samples per ramp | 5,000 |
| Collected return power | 37.5 pW |
| Coherent return power | 3.75 pW |
| LO shot-noise density | 12.008 pA/√Hz |
| White-noise range bound including electronics | approximately 2.76 mm |
| Quadrature MZM incident power for 10 mW average launch | approximately 39.91 mW |

These are assumptions and reference calculations, not demonstrated instrument specifications. The millimetre precision bound concerns one isolated target; it does not imply millimetre two-target resolution.

### Stage B: numerical and coding checks

```bash
python -m fmcw.cli convergence --out results/my_convergence
python -m fmcw.cli tradeoff --out results/my_tradeoff
python -m fmcw.ambiguity --config config/baseline.json --out results/my_ambiguity
```

The convergence command compares the 200, 400 and 800 MS/s internal simulations with identical deterministic waveforms. In the supplied baseline the 4× and 8× waveform errors relative to 16× are about 1.80% and 0.358%, respectively. Do not call the default 4× rate fully converged. Campaigns use 8×; repeat selected final results at 16× and tighten if the conclusion changes. Rise times and MZM harmonics are not strictly bandlimited.

The bias/drive plot quantifies sideband energy and transmitter power cost. It is not an interference-rejection measurement. Cross-ambiguity includes the complete filtered field and maximizes over nuisance phase. Its finite grid can miss a sharper worst case; refine near maxima.

### Stage C: verify Monte Carlo wiring

```bash
python -m fmcw.cli mc --config config/white_noise.json --trials 20 --null-trials 100 --isr none,10 --methods uncoded,full_field,sideband --out results/my_smoke
```

This deliberately small smoke run tests the pipeline. It cannot establish a 1% false-alarm rate or rare failure probability. Each operating point uses separate H0 threshold-calibration trials, H0 validation trials, and H1 target-present trials. H0 retains the foreign transmitter, if present. The score is maximized over the whole range search and refined before threshold calibration.

### Stage D: primary research comparison

```bash
python run_campaign.py --stage primary
python run_campaign.py --stage primary --execute
```

The first command writes configs and `plan.json`. The second actually runs them. Defaults are 500 target-present trials and 2,000 target-absent trials **for each of threshold calibration and validation**, per method/ISR/case. This is substantially more computation than the demo. Results are checkpointed after each operating point. An interrupted point is restarted by rerunning; there is no automatic resume/skip mechanism.

Or run one selected case directly:

```bash
python -m fmcw.cli mc --config config/baseline.json --trials 500 --null-trials 2000 --isr none,-20,-10,0,10,20,30 --scenario overlap --out results/primary_overlap
```

For final numerical claims prefer an 8× configuration generated by the campaign; compare selected points at 16×. Every run writes its actual configuration and package versions.

Three scenarios are available: an equal-slope foreign beat corresponding to a target 0.45 m beyond the desired target, a 4% slope-mismatch crossing, and a +55 MHz optical-frequency-offset control. These are representative cases, not a sweep over every optical offset. Change parameters or extend the scenario list for the exact operating conditions you wish to defend.

### Stage E: power, drive and robustness

```bash
python run_campaign.py --stage power
python run_campaign.py --stage bias_drive
python run_campaign.py --stage robustness
```

Inspect each plan and add `--execute` to run it. Robustness cases cover linewidth, coupling, range, MZI delay error, coherent scatterers, and ADC clipping. The fixed-source-power comparison bypasses the MZM for uncoded light, and holds **received ISR** fixed. Consequently absolute foreign power changes with the desired power across methods. The power campaign also generates `_fixed_foreign` cases: these use `foreign_reference_coherent_w` to keep absolute foreign power identical across methods at each labeled level. Their x axis is ISR relative to that fixed reference, and `actual_isr_db` records the true ratio for each method. This avoids conflating fixed-ISR and fixed-illumination comparisons.

### Stage F: optional Tidy3D component work

```bash
python -m pip install -e ".[component]"
python -c "import tidy3d; print(tidy3d.__version__)"
python component/solve_component.py --design component/design_a.json --out results/design_a
python component/solve_component.py --design component/design_b.json --out results/design_b
python component/compare_components.py results/design_a/component.json results/design_b/component.json
python -m fmcw.cli demo --config config/baseline.json --component results/design_a/component.json --out results/component_demo_a
python -m fmcw.cli demo --config config/baseline.json --component results/design_b/component.json --out results/component_demo_b
```

**Status:** these optional Tidy3D scripts were syntax-checked, but not executed here because the dependency could not be installed. They use the documented local `ModeSolver.solve()` API. No Tidy3D cloud jobs are submitted. The system simulation is usable without them.

Inspect the mode plots, mode identity, `convergence.csv`, and the declared RF assumptions. The export is rejected by the system CLI unless mesh refinement, domain expansion and voltage-step checks pass the supplied tolerance. If convergence fails, refine the design JSON and rerun. Check field polarization visually even when the numeric checks pass.

`component.json` changes Vπ but does **not** silently rescale the bias/drive voltage, infer insertion loss, or modify the laser tuning coefficient. For interference-versus-component results, run `mc` with the generated `design_0.json` and `design_1.json` configs using identical case lists. Both designs here are illustrative rectangular ridges with a uniform assumed RF field, not published-device reproductions.

## 4. What to read from each Monte Carlo run

- `summary.csv` / `.json`: range bias, standard deviation, RMSE, gross-error probability, detection probability, false-alarm validation and confidence intervals; optical power costs.
- `trials.csv`: every H1 estimate, seed, score, threshold, and clipping fraction.
- `h0_*.json`: independent calibration/validation score arrays and thresholds.
- `performance.png`: RMSE, failures and detection versus ISR.
- `tolerable_isr.json`: largest **tested** ISR passing the declared point-estimate criteria. It is not a proven continuous boundary and not a confidence-qualified specification.

Use the no-interference rows to report sensitivity penalties before describing interference rejection. Declare H0 explicitly: this implementation learns a separate threshold for the stated foreign-interference distribution at each operating point. A threshold calibrated with interference absent is a different detection experiment.

## 5. What has actually been verified

See `docs/VERIFICATION.md`. Core physical tests, demo, bias/drive sweep, receiver convergence and cross-ambiguity checks were run. The included small Monte Carlo run is labeled a smoke test. The full 500-realization campaign and optional Tidy3D component solves are not represented as completed research results.



```bash
git init
git add .
git commit -m "Add reproducible coded FMCW simulation and validation"
git switch -c feature/component-characterization
```

No external repository or remote is assumed. Keep long campaign outputs out of Git or track only compact summaries with their configurations.
