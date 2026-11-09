# Experiments, evidence and manuscript workflow

## What a result can establish

The completed package allows a computational study. A successful run establishes behavior of the declared model, not performance of the cited laser, a fabricated MZM or a finished LiDAR. Label parameters as literature-supported, assumed, numerically extracted, calibrated or swept. Retain seeds and versions with every plotted data series.

## Stage gates

1. **Physical correctness:** tests pass; noiseless off-grid ranges agree; collected/coherent power and noise ENBW agree with independent calculations.
2. **Numerical convergence:** compare at least 4×, 8× and 16× rates. Refine time resolution, prehistory and search grid until the metric or claimed advantage is stable. Repeat at the largest drive, highest frequency offset and largest ISR used in conclusions.
3. **Calibration:** inspect fit residuals; include MZI-delay uncertainty; do not call exact simulator values a calibration. Separate synthetic calibration noise from unmodeled hardware effects.
4. **No-interference precision:** measure bias and RMSE before introducing B. Compare the white-noise case against its local Fisher bound, then add linewidth and speckle.
5. **Interference comparison:** use matching acquisition time, launch power, bandwidth, target distribution, foreign-code distribution and paired seeds. Report both full-band and sideband results.
6. **Power fairness:** repeat at fixed source power; distinguish fixed received ISR from fixed foreign watts. Report source, mean launch and peak launch power explicitly.
7. **Component connection:** verify modes and EO extraction, then compare designs at the same drive in volts. Changing only normalized `Vm/Vpi` conceals much of the value of a lower Vπ.
8. **Detection validity:** inspect held-out H0 false-alarm rate and its confidence interval. If it does not support the 1% target, increase H0 count or use a conservatively calibrated order statistic. Do not report Pd as being at 1% PFA merely because `.99` was requested.

## Metrics

- Bias: mean signed range error.
- Precision: sample standard deviation (not interchangeable with RMSE).
- RMSE: square root of mean squared range error.
- Gross error: absolute error greater than `c/(4 n_air B)`.
- Detection: maximum full-search score exceeds the independently calibrated threshold. A detection may still have the wrong range, so it must be reported alongside gross errors.
- Binomial intervals: exact two-sided Clopper–Pearson 95% intervals.
- Tolerable ISR: largest tested point with RMSE ≤1 cm, gross errors ≤1%, and Pd ≥95%. The code uses point estimates for this screening; require confidence-qualified criteria before calling it a guaranteed limit.

Zero failures in 500 trials still gives an approximately 0.735% upper two-sided 95% bound. Twenty trials cannot substantiate a 1% gross-error objective. At 1% probability and 2,000 validation trials, only about 20 events are expected: meaningful uncertainty remains. Increase counts for sharp rare-event claims.

Thresholds are separately calibrated for each method/ISR/scenario. This answers whether the desired target can be detected under a known distribution of foreign interference. A deployed detector with unknown ISR cannot assume access to those condition-specific thresholds. To examine that deployment question, calibrate one threshold against a declared mixture/worst case and reuse it across ISR values. That is an additional experiment, not the interpretation of the present conditional thresholds.

## Recommended figures for the 5–8 page manuscript

| Figure | Source | What to explain |
|---|---|---|
| Optical system and simulation boundary | Proposal diagram | Source vs MZM vs MZI; optical path and sampling boundary |
| Component mode and EO extraction | `results/design_*/` after successful local solve | Crystal axes, mode identity, numerical convergence and RF approximation |
| Coded/uncoded spectra and ambiguity | `demo.png`, `cross_ambiguity.png` | Persistent carrier and sideband sensitivity cost |
| RMSE / failures / detection vs ISR | Full campaign `performance.png` and CSVs | Condition-specific thresholds and statistical intervals |
| Bias/drive and power tradeoff | `bias_drive.csv` and component comparisons | Fixed volts, mean/peak power, and no-interference penalty |

Avoid crowding four weak figures into one plot. Use raw CSVs to make final figures after selecting the defensible experiment subset. The supplied plots are useful defaults; the smoke-test curves are not final manuscript evidence.

## Interpretation checklist

- If coding helps only in sidebands, quantify the energy discarded and extra source power required.
- If full-field coding fails, examine the persistent common carrier and field cross-ambiguity; this can be the main result.
- If noise-only performance is poor, inspect calibration, whitening, timing and conditioning before attributing it to interference.
- If the out-of-band control causes errors, inspect finite filter rejection, phase-noise skirts, shot noise and numerical aliasing. ADC clipping is only one dynamic-range effect.
- If a mode solve is converged but its RF field is assumed, label Vπ as a model prediction under that approximation.
- If the largest tested ISR passes, extend the ISR grid; the boundary has not been located.
- Report a simpler uncoded calibrated LiDAR as the alternative when coding's sensitivity/power cost exceeds its benefit.

## Scope deliberately not claimed

This is not an optical-carrier FDTD simulation, a laser self-injection-locking model, an RF electrode optimization, a fabrication design, a general multiuser canceller, a scanning/velocity system, or a complete laboratory calibration chain. Those are unnecessary for the declared computational question but must not be implied by the manuscript.
