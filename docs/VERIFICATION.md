# Verification record

Prepared 2026-11-04. These are checks performed on the supplied code, not experimental hardware measurements.

## Environment

- Python 3.12.14
- NumPy 2.3.5
- SciPy 1.17.0
- Matplotlib 3.10.8
- threadpoolctl 3.6.0

The optional Tidy3D dependency could not be installed in this execution environment. Its scripts were syntax-checked and aligned to the documented local ModeSolver interface, but no component result is claimed. The notebook's code cells were parsed; the notebook was not executed through Jupyter. Its substantive module calls were exercised through the terminal.

## Tests actually executed

`python run_tests.py` passed **14 tests**. Full output is in `results/physics_tests.txt`.

1. Internal-frequency alias guard rejects an obviously undersampled interferer.
2. Beat frequency and optical-sweep resolution match independent equations.
3. Zero-failure binomial interval has the expected finite-sample upper bound.
4. Independent synthetic MZM/MZI calibration recovers perturbed parameters within declared tolerances.
5. Noiseless ranging works with a complex, imbalanced, chirping MZM.
6. Fixed foreign-power mode preserves foreign ADC waveform across coded/uncoded source-power comparisons.
7. Fractional-delay phase variance and coherence agree with Wiener theory.
8. +20 dB ISR scales field/current amplitude by ten.
9. Link budget yields 37.5 pW collected and 3.75 pW coherent power.
10. MZM null and negative field are retained.
11. Filtered white-noise variance agrees with numerically integrated ENBW.
12. Noiseless off-grid range is recovered to within 20 µm for both coded and uncoded exact-template models.
13. Equal-launch normalization preserves launched power while exposing incident power cost.
14. Empirical white-noise range precision over 60 trials is consistent with the local template bound within a statistical tolerance.

Tests do not prove all parameter combinations or validate the physical assumptions. Re-run after edits.

## Executed example outputs

| Directory | What was run | Interpretation |
|---|---|---|
| `results/demo` | One baseline realization for all four estimators | Waveforms, spectra, auto-ambiguity, independent calibration |
| `results/noiseless` | Same demo with receiver/laser noise disabled | Calibration noise remains separately specified |
| `results/tradeoff` | Nine bias/drive combinations | Power budget and retained sideband energy |
| `results/convergence` | 4×, 8× and 16× deterministic receiver rates | Numerical-rate sensitivity, not a universal convergence guarantee |
| `results/ambiguity` | 41 asynchronous timing offsets × 41 beat offsets × 2 processing bands | Complete-field normalized cross-ambiguity |
| `results/smoke_mc` | 20 H1 trials; 100 calibration H0 and 100 validation H0 per method/case; three methods, no interference and +10 dB ISR | Wiring/smoke test only |
| `results/no_interference_validation` | 60 H1 trials; 1,000 calibration H0 and 1,000 validation H0 per method; three methods, no interference | More informative noise/threshold check; not a rare-failure guarantee |
| `results/campaign` | Generated plans/configs only | Full campaigns have NOT been executed |

At the default quadrature bias and drive 0.3 Vπ, sideband processing retains about **5.29%** of the full processed quadrature energy. This is the selected upper-sideband fraction, not all code-bearing energy. It explains why stronger discrimination can carry a large sensitivity penalty.

At zero foreign beat offset, the sampled asynchronous full-field overlap ranges approximately **0.882–0.921**, versus **0.017–0.278** in the selected sideband. These are finite-grid, worst-phase overlaps under the baseline ideal deterministic waveform. They are not a universal rejection level or a noise/interference Monte Carlo result.

The receiver waveform differences relative to 16× are **1.80%** at 4× and **0.358%** at 8×. Therefore the default quick-run setting must not be described as fully converged. Campaign configs use 8×, with selected final points requiring 16× checks.

## Preliminary Monte Carlo cautions

The 100-H0 smoke calibration produced held-out no-interference false-alarm estimates of 9%, 4%, and 1% for uncoded/full-field/sideband. These small-sample thresholds do **not** establish 1% PFA. The larger no-interference check is provided specifically to test this. Always report the measured held-out rate and interval instead of assuming the quantile target was achieved.

The smoke +10 dB case placed the foreign beat 0.45 m beyond the desired target. Uncoded/full-field methods followed that beat in these 20 trials; the sideband method had much smaller range errors but lower precision than no-interference full-band processing. This is an illustrative mechanism check, not a general claim that coding succeeds.

See `no_interference_validation_summary.md` for the larger check's exact statistics generated directly from the saved CSV. Any 500-trial interference, power, bias/drive, rough-target, or component comparison remains to be run by the corresponding campaign command.

## 5 November requirements revision

Added an analytical field/photon/source and accuracy budget, rubric traceability, a 10-case submission plan, and a corrected 6–10-page/25-minute deliverable structure. Reran all 14 physics tests successfully; output: `results/requirements_review/physics_tests.txt`. Executed the budget script and validated all generated plan configurations. No new Monte Carlo campaign or Tidy3D solve was executed.
