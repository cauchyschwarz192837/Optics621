# PHYSICS 621 | Evidence review and run guide
Read this alongside the submitted README. The source tree and original results are retained; everything added by this review is in review/. No paid cloud jobs or GDS files are needed. The compact kit omits Git/macOS metadata and large regenerated HDF5 files; the design scripts regenerate them. Run shell commands from the Optics621 directory.

## Decision and rubric
Proceed with the existing question: when is it worth discarding the carrier to identify the correct return? There is already an end-to-end coherent field model, a quantitative calibration/noise/link budget, and a controlled counterexample to universal coding benefit. This is stronger than a literature review. It is not yet a characterised instrument or an operating envelope. The proposal asks when coding helps and how bias/drive affect that benefit. A single favourable collision plus a power/energy sweep does not answer the whole question.

The attached expectations take precedence over the proposal's earlier length: 25 minutes; 6 to 10 pages excluding references; both partners contribute to the talk and manuscript. The rendered draft has 8 body pages and a ninth page for references/provenance. It covers source, propagation, modulator, LO, detection, noise, resolution, block diagram and more than three original estimates. Optical systems, materials, nonlinear polarisation, statistical optics and detection are identifiable. Originality resides in comparing processing on the same optical system, not inventing the laser or proving immunity. Confirm distinction from your Spotlight; the files do not establish that. Replace the contribution placeholders with work each person actually did, including the oral and written components.

## What was checked
* Executed all 14 submitted unittest checks, the baseline budget and temporal convergence script. All passed; convergence numbers reproduced. Independently recalculated errors and detection outcomes from the supplied target-present trial rows. Replayed the first two saved seeds per method and condition in both studies (18 frames); their range estimates matched. This was not a rerun of the full detection campaign.
* At 50 m: 1.667820 MHz beat, 0.299792 m sweep-resolution scale, 37.5 pW collected and 3.75 pW coherently coupled, 35.55 dB integrated uncoded CNR, 2.758 mm isolated white-noise standard-deviation bound including electronics. The proposal's ~2.5 mm is the shot-noise-only reference. Both are bounds, not achieved accuracy specifications.
* Positive-frequency estimates follow the magnitude of a negative signed target beat. The code preserves the signed complex MZM field, uses the same laser history at delayed times for A/LO, a separate laser B, and filters before ADC sampling. Subspace projection fits unknown phase and amplitude. Receiver whitening assumes stationary noise with periodic covariance; calibration uses independent synthetic data with known chirp-error basis, not measured hardware.
* With only receiver noise, full-field and uncoded RMSE are statistically compatible with the analytical scale. With a foreign beat deliberately placed 0.45 m farther (about 15 kHz separation; reciprocal ramp length = 10 kHz), an estimate 0.449 m too large is the foreign peak. This is a near collision, not the exactly coincident-beat case.
* Correct detection = threshold crossing AND absolute range error at most 0.149896 m. In the +10 dB case: uncoded 13/20 threshold crossings but 0/20 correctly localised detections; full-field 11/20 and 0/20; sideband 17/20 and 17/20. The 3 sideband misses were still included in all-trial RMSE. No sideband gross errors in 20 trials allows a 95% exact upper bound of 16.84%. None of this demonstrates a 1% failure specification.
* Seeds repeat across saved studies. In particular the short no-interference H1 run overlaps the 60-trial run. Do not pool them as 80 independent observations. Preserve paired trial identities when comparing methods.
* The 4.5 to 10 MHz band retains 5.29% of whitened quadrature energy at nominal bias/drive, not 5.29% of optical power. At 50 m the carrier beat and fundamental sidebands lie around 1.668, 3.332 and 6.668 MHz. The band retains the upper lobe and rejects the carrier and most of the lower lobe. At other ranges the retained fraction changes.
* Section 7's ISR times squared overlap is a normalised-template diagnostic. For a physical input ISR include the ratio of B and A processed energy per input watt, plus phase dependence. Subspace overlap is maximised over nuisance phases. It is not a detection probability or necessarily the actual output power ratio.
* Small code inconsistency: requirements_review.py passes coherent power to Receiver.noise_psd; fmcw/experiments.py and the receiver model use collected power for desired-light shot noise. In requirements_review.py replace b['coherent_w'] with b['collected_w'] ONLY in the noise_psd call; retain coherent power in the beat numerator. Negligible here under LO dominance, conceptually significant otherwise. No submitted source was patched.
* Default config/baseline.json has 50 kHz linewidth but no interferer. The two multi-trial results plotted in the paper used zero linewidth. Each threshold is calibrated with the interference condition known, and each campaign conditions on one calibration. These are model boundaries, not deployment guarantees.

## New component results, separate from the submitted evidence
Both original design scripts ran with Tidy3D 2.12.2 locally. Exports in review/design_a and review/design_b passed the supplied 3% relative Vpi tolerance. The final selected mode was index 0 with x-field fractions about 0.966 and 0.973. Solver messages include boundary warnings for nonselected modes; inspect the field plots and convergence CSV before adopting results. At differential arm voltages +V/2 and -V/2, Vpi = wavelength/(2 L |dneff/dVarm|). A: 2.722 V; B: 3.766 V. The code uses a 1 cm section and a uniform RF field. No measurement, metal-loss calculation or self-injection-locking prediction is implied.

At fixed 2 V bias and 1.2 V drive, A needs 65.40 mW branch input and B 43.13 mW for the same 10 mW launch. The difference is largely an operating-point effect: bias/Vpi is 0.735 vs 0.531. A second comparison should independently rebias each to quadrature to separate intentional bias control from geometry sensitivity. Both width and gap change: these two designs alone cannot identify a width-only effect. Paper Table 1/Figures 2 and 3 still use the assumed 4 V device, not these new designs.

## Reproduce the work, in order (macOS/Linux)
1. Extract the ZIP, open a terminal in Optics621 (contains pyproject.toml), then install:
    python3.12 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements-tested.txt
    python -m pip install -e .
    python -m pip check
    python run_tests.py
Use a Python 3.12 installation for the tested pins. For a different supported Python, install only -e . first and verify your resolved versions. The core uses NumPy, SciPy, Matplotlib and threadpoolctl. pandas, PhotonForge and Jupyter are not required. On Windows use .venv/Scripts/Activate.ps1 in PowerShell.

2. Verify analytical and noiseless baselines:
    python -m fmcw.cli baseline --config config/baseline.json
    python -m fmcw.cli demo --config config/noiseless.json --out results/my_noiseless
    python -m fmcw.cli convergence --out results/my_convergence
Look for the analytical numbers above, four estimated ranges near the true target in the noiseless demo, and 4x/8x waveform differences of 1.80%/0.358% versus 16x. These are relative waveform errors, not percentage range errors.

3. View evidence immediately, without recomputing thousands of trials:
    python review/plot_evidence.py
Open review/figures/range_evidence.png, its vector PDF, and verified_metrics.csv. Open docs/system_architecture.svg in a browser. Compare the saved results/demo/demo.png (one realisation), results/tradeoff/bias_drive.png and results/ambiguity/cross_ambiguity.png. To reproduce the latter two:
    python -m fmcw.cli tradeoff --config config/baseline.json --out results/my_tradeoff
    python -m fmcw.ambiguity --config config/baseline.json --out results/my_ambiguity
Optional: python -m pip install -e ".[dev]" and jupyter lab notebooks/01_walkthrough.ipynb.

4. Reproduce the small interference check:
    python -m fmcw.cli mc --config config/white_noise.json --methods uncoded,full_field,sideband --scenario overlap --isr none,10 --trials 20 --null-trials 100 --out results/my_smoke
Read trials.csv, summary.csv, h0_*.json and performance.png. H0 means desired target absent; foreign light stays present for interference cases. Each null-trials value applies separately to calibration AND validation. At a 1% tail, 100 calibration samples give a noisy threshold. The delivered detection_probability counts threshold crossings alone. Compute joint correct localisation before reporting target detection reliability.

5. Build the final plan before spending time on it:
    python run_submission_plan.py --root results/my_plan
    python -m fmcw.cli mc --config results/my_plan/primary.json --methods uncoded,small_signal,full_field,sideband --scenario overlap --isr none,0,10,20 --trials 500 --null-trials 2000 --out results/my_primary
The second command is a large calculation. Time one small pilot first. The plan generator alone makes JSON, not scientific results. Use new output folders: the campaign writes checkpoints but does not resume automatically. Add crossing and out_of_band controls afterwards. For the equal-source case, use the plan's source_fixed_foreign.json and compare at identical absolute foreign power; inspect actual_isr_db, foreign_coherent_w and launch_w.

6. Optional: reproduce the new chip results:
    python -m pip install -e ".[component]" "tidy3d==2.12.2"
    python component/solve_component.py --design component/design_a.json --out results/my_design_a
    python component/solve_component.py --design component/design_b.json --out results/my_design_b
    python component/compare_components.py results/my_design_a/component.json results/my_design_b/component.json --out results/my_components
    python -m fmcw.cli demo --component results/my_design_a/component.json --config config/baseline.json --out results/my_component_demo
The two-geometry comparison is a power-budget comparison; running an MC sweep using each export is needed for a component-dependent interference conclusion. If reproducing only the system study, the verified exports already exist under review/.

## Priorities for a defensible final result
1. Run all four estimators under nominal linewidth and matched settings. Add a matched-code vs wrong-code control on identical coded ADC records and the same subband; recalibrate each detector's H0 threshold. This separates the benefit of knowing A's identifier from the benefit of filtering away the carrier.
2. Report all-trial RMSE and joint detection/correct-range rate, alongside validated PFA and binomial intervals. Use paired bootstrap intervals for differences in RMSE with the same physical trial seeds. A 1 cm RMSE target, 15 cm gross-error threshold and 30 cm resolution scale are three different criteria.
3. Repeat the near-collision at different beat spacings, a crossing, and out-of-band control. Zoom the ambiguity grid to 1 or 2 kHz spacing near the ~15 kHz collision; the current 100 kHz spacing misses narrow features. At exact coincidence a small range error can coincide with a false attribution, so retain H0 tests.
4. Recheck selected primary conclusions at 16x versus 8x, with the same operating parameters. Confirm each estimator's refined range and distribution, not merely mean waveform differences. Then compare fixed illumination and fixed source power. Treat a source branch power as a branch power; explicitly include LO, tap and efficiency in a total source budget.
5. Compare MZM bias/drive settings at representative ISR with an actual range metric. Merely increasing sideband energy does not establish optimum rejection. Repeated independent calibrations, linewidth variations and rough-target trials are useful after the main experiment is complete.

## Paper and 25-minute presentation
Keep the architecture paragraph and separation of the two reference papers. Define received interference-to-signal ratio (ISR) and “full-field” at first use. Say explicitly that the proposed chirp laser is behavioural and that coherence of a weak reflected field, not the electrical code alone, determines the beat. End the introduction with a testable statement: “We test whether restricting the receiver to a code-bearing sideband improves the probability of declaring the correct range when a second coherent beat lies nearby, and measure the resulting precision and source-power penalties.” Mention the classical white-noise bound only for the uncoded reference. Update Section 3.2, Section 8.1 and provenance if you adopt the new component results. Supply actual contributions from both partners.

Talk sequence: 3 min question and baseline; 4 min field flow and coherence; 4 min modulation/materials/component results; 5 min trial-level ranging result and its limits; 4 min power and fixed-driver choice; 3 min control experiments and condition-dependent limits; 2 min conclusion/discussion (25 min). For the paper use the trial-level plot beside the spectrum or heat map; the plot makes foreign-peak capture visible where an RMSE bar hides it. In the talk reveal one panel at a time. Place 50.00 m and 50.45 m references on the same axis and identify zero linewidth, 20 trials and the fixed-launch comparison in the caption.
