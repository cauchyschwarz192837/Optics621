# Requirements review and revised project structure

Reviewed 5 November 2026 against **Final Project Expectations – Advanced Optics Fall 2026**, both pages, and the supplied Combined Optics Proposal and current implementation.

## Verdict

The selected architecture is suitable for the assignment. It already identifies a source, propagation, modulation, coherent detection, noise, bandwidth/resolution and a realistic engineering tradeoff. It is not yet a completed final submission: the main interference results, manuscript, presentation and actual author contributions remain unfinished. The rubric permits optics calculations/simulations; it does not mandate Tidy3D, a fabricated device, a full Maxwell solution of the system, or reproduction of the reference laser.

Keep the title **Interference rejection and precision limits in intensity-coded FMCW LiDAR**. Keep one stationary target and one foreign transmitter. Do not add a laser resonator simulation merely to make the project appear more complete. The source is a behavioral model motivated by Snigirev et al.; the separate MZM is our proposed extension.

## Requirement-to-evidence matrix

| Requirement | Existing evidence | Revision and remaining evidence |
|---|---|---|
| One complete photonic system | Source → MZM → target → receiver → estimator | Explicit pre-MZM LO/calibration split; field and flux ledger below |
| At least four course units | Material response, interference, diffraction, detection/noise | Map to actual syllabus unit names before submission; five conceptual connections below |
| At least three original quantities | Beat, resolution, link budget, noise bound | New `requirements_review.py` exports 21 reproducible quantities with assumptions |
| Clear block diagram and field/flux explanation | Proposal diagram and system code | Updated `system_architecture.svg`; field ledger below |
| Dominant limitation | Correlation, calibration, phase noise discussed | Quantify deterministic carrier/sideband tradeoff now; establish measured regime boundary with selected Monte Carlo points |
| Realistic alternative design | Uncoded baseline and sideband estimator | Equal-source-power uncoded bypass is the primary alternative; compare full power allocation |
| Original quantitative analysis | Tested simulator and preliminary outputs | Do not label a planned campaign as a result or a transfer of coding as proven novelty |
| Multiple appropriate references | Five proposal references | Preserve distinction among Nature source, coded phase-shift motivation, and optional TFLN component method |
| 6–10 manuscript pages, excluding references | Proposal incorrectly says 5–8 | Supersede with 8-page main-text plan below |
| 25-minute conference presentation | No timed final structure | Timed joint presentation below |
| Both partners contribute to both outputs | Planned roles only | Actual contribution template; fill after work is done |
| Different from previous Spotlight topic | Not established by available project files | Team must compare its actual prior Spotlight topic; different application is not automatically sufficient |

## Coherent architecture and model boundary

Laser A is split into (i) an uncoded LO, (ii) a delay-MZI calibration branch, and (iii) the transmit branch containing the coding MZM. Transmit/collection optics connect to a stationary extended target. A separate laser B contributes unwanted received light. An ideal optical combiner and balanced detector mix the desired and foreign fields with A's LO; an electrical filter precedes the ADC. DSP fits amplitude and phase while searching range, using independent calibration. The MZI calibration detector is a separate supporting measurement, represented by synthetic phase data rather than a complete second receiver circuit.

An optical background filter is included only through aggregate transmission/background assumptions, not as a wavelength-resolved transfer function. Transmit/receive isolation, polarization stability, detector linearity and pointing are idealized or lumped; no physical circulator layout is claimed. A source-power allocation is now explicitly calculated, but its efficiency is an assumption rather than measured hardware performance.

### Field and photon-flux ledger

Fields have units sqrt(W). Optical photon flux is P/(hν); coherent-mode power is only a fraction of collected power.

| Stage | Transformation | Physical interpretation |
|---|---|---|
| Source | E₀(t)=√P₀ exp[iφ(t)] | Prescribed chirp and shared Wiener phase history; cavity and locking are excluded |
| Split | Eⱼ=√ηⱼ E₀ | LO and calibration tap require source power in addition to the transmit branch |
| Coding MZM | Eₜ=m[V(t)]Ebranch | Signed complex field retained; mean power uses ⟨abs(m)²⟩ |
| Propagation and target | Eᵣ(t)=h Eₜ(t−τ), τ=2nR/c+τinternal | Delay, target phase and attenuation; Lambertian collection and mode overlap assumed |
| Foreign source | Eᵦ with independent phase/chirp/code | ISR refers to coherent received powers; fixed absolute foreign-power cases are separate |
| Balanced detection | i=2ℜ Re[ELO* (Eᵣ+Eᵦ)] + noise | Optical phase difference becomes an electrical beat; ideal common-mode cancellation |
| Filter/ADC | Sample filtered i(t) | Finite bandwidth and potential clipping; oversampling convergence required |
| Estimation | Fit quadrature templates across range | Calibration uncertainty remains distinct from hidden true parameters |

### Course-unit connections to make explicit

1. **Waves in anisotropic media:** LN dielectric tensor, guided modes and electro-optic overlap; source/material assumptions determine the voltage response.
2. **Nonlinear optics:** Δ(ε⁻¹)ᵢⱼ=rᵢⱼₖEₖ from the Pockels interaction χ²(ω;ω,0). The MZM cosine is interferometric nonlinearity, not by itself a nonlinear-material argument.
3. **Interference and coherence:** MZM arm interference, delay-MZI calibration, coherent receiver mixing and exp(−πΔντ).
4. **Gaussian beams and propagation:** Rayleigh range, beam radius, receiver aperture and the conditions for the extended-target link budget.
5. **Photodetection/statistical optics:** photon flux, shot noise, bandwidth, Fisher precision and speckle. Distinguish isolated-target precision from two-target resolution.

These are conceptual mappings; the actual course syllabus was not supplied. Verify its named units rather than claiming five official units have been confirmed.

## Added quantitative budget and engineering consequences

Run `python requirements_review.py` from the project root. The CSV/JSON records formulas through code and labels every assumption. Default results:

| Quantity | Result | Interpretation |
|---|---:|---|
| Sweep resolution scale | 0.299792 m | Does not imply a 30 cm error for an isolated target |
| 50 m target beat | 1.667820 MHz | 500 MHz in 100 μs |
| Collected / coherent power | 37.5 / 3.75 pW | Assumed coupling 0.1 |
| Coherent-mode photons per ramp | 2,926 | Before detector quantum efficiency; not total collected photons |
| LO shot-noise density | 12.008 pA/√Hz | One-sided PSD |
| White-noise integrated CNR | 35.552 dB | Includes electronics; equal-power unmodulated reference |
| White-noise range bound | 2.758 mm | Not the bound for a selected coded sideband or a phase-noisy instrument |
| Coherence magnitude at 50 m | 0.94895 | Assumed 50 kHz Lorentzian linewidth |
| Gaussian radius at 50 m | 7.024 mm | Assumed 5 mm waist, ideal beam |
| MZM-incident branch power | 39.905 mW | 10 mW average launch, 3 dB insertion, quadrature |
| Total source allocation | 42.637 mW | Includes 0.5 mW LO, assumed 0.1 mW calibration tap, 95% allocation efficiency |
| Uncoded bypass source allocation | 11.158 mW | Same launch, LO, calibration and efficiency |
| Single-term slope tolerance for 1 cm | 200 ppm | Other errors must leave room in a combined budget |
| Single-term delay tolerance for 1 cm | 66.713 ps | Internal delays require calibration |

The coded design needs roughly **3.82 times total source power** under the stated allocation assumptions. That is a meaningful architecture tradeoff; the reference laser is not asserted to supply it. `source_w` in existing simulation configs remains the transmit-branch incident power, not total laser output. This revision adds an explicit allocation calculation without silently changing past results.

For absolute accuracy, linearize R=c(f/S−τinternal)/(2n). The signed first-order error is approximately δR = c δf/(2nS) − R δS/S − R δn/n − c δτinternal/(2n), neglecting the internal-delay contribution to the slope term when small. Correlated systematics should not automatically be summed in quadrature. A 0.1% slope bias alone gives about 5 cm error at 50 m. The simulated millimetre white-noise precision therefore cannot be presented as millimetre absolute accuracy.

## Dominant limitation and alternative

Existing deterministic calculations show full-field overlap about 0.882–0.921 at zero foreign beat offset over sampled asynchronous delays. At +20 dB received ISR, ISR×abs(μ)² is approximately 78–85: interference can dominate the matched-template projection. This is a projection diagnostic, not a range-error probability.

The selected sideband overlap is approximately 0.017–0.278 on that grid: the same diagnostic spans 0.029–7.73. It is not uniformly below one. Moreover, the selected band retains only about 5.29% of processed quadrature energy, a 12.77 dB energy penalty. That penalty is not automatically the same number in range RMSE, since frequency information also changes. The existing white-noise verification shows roughly 2.8–2.9 mm full-band RMSE and 10.7 mm sideband RMSE, with the limits stated in the original verification record.

Thus the supported limitation is **a strong common carrier and code-dependent overlap competing with sideband energy loss**. The dominant limitation in the complete noisy system still needs regime-specific results. At small interference, calibration and phase noise can supersede receiver noise; during fades coupling may dominate. Test these rather than declaring a universal dominant noise source.

The primary realistic alternative is **uncoded, calibrated FMCW with MZM bypass**: lower source/driver complexity, compared at equal launched power and separately equal available branch power with fixed absolute foreign illumination. Sideband processing is a second, receiver-side alternative. A wider sweep can improve the sweep-resolution scale but changes voltage/bandwidth demands and is outside the primary comparison.

## Tidy3D scope and completion gates

The present optional component is a rectangular LN ridge/slab in silica with an assumed uniform RF field. It is not the Nature Si₃N₄–LN resonator and does not use CustomMedium. A local mode calculation gives dn_eff/dV and a differential-voltage Vπ, with declared crystal axes and arm length. Numerical convergence does not validate the uniform-field approximation or predict metal/packaging loss.

For a defensible component result: run both designs; inspect polarization and confinement; check mesh/domain/voltage-step convergence; preserve voltage conventions; compare at identical physical bias/drive voltages; propagate Vπ into system trials. A solved nonuniform electrode field is a future improvement, not a rubric requirement. If these solves cannot be completed, retain Vπ as an assumption and its sensitivity study; omit any claim of a Tidy3D-validated design.

## Minimum final evidence set

1. Use the existing physics checks, analytical budget and noiseless off-grid validation as verification evidence.
2. Run a selected primary overlap comparison for all four estimators, including no interference, 0, +10 and +20 dB ISR; retain independent threshold calibration and validation. Use 500 H1 and 2,000 H0 in each H0 split as a starting point, with confidence intervals rather than a guaranteed rare-error claim.
3. Add one crossing and one out-of-band control at +10 dB; repeat selected conclusions at 16× internal sampling against 8×.
4. Compare equal launched power and equal branch source power with fixed absolute foreign illumination. Report actual ISR and source allocation, not only nominal labels.
5. Use the existing nine-point bias/drive energy-power sweep; select two contrasting points for interference trials instead of running every Cartesian combination.
6. Include one calibration-error and one linewidth sensitivity. Keep rough-target results optional unless completed and interpretable.
7. Plot RMSE, gross errors and measured PFA/Pd with intervals; report all-trial RMSE rather than conditioning it on detection. State whether thresholds assume a known interference distribution.

`python run_submission_plan.py` writes a compact set of commands; `--execute` runs it locally. This is a plan until output files actually exist. The earlier larger campaign remains available.

## Revised manuscript: 8 pages of main text, references additional

| Pages | Content and evidence |
|---|---|
| 1 | Application, literature boundaries, research question, original contribution |
| 2 | Complete block diagram and optical-field/flux ledger |
| 3 | Course connections, Pockels/MZM physics, propagation and coherent receiver |
| 4 | Analytical budget, precision versus resolution, absolute-accuracy budget |
| 5 | Simulation/calibration methods, fairness conditions, numerical validation |
| 6 | Completed interference comparison with uncertainty; no planned results as data |
| 7 | Power/drive tradeoff, alternative design and selected robustness |
| 8 | Dominant regimes, limitations, conclusion and actual contributions |

This replaces the proposal's 5–8-page wording. The assignment requires **6–10 pages excluding references**. Keep the abstract concise; do not pad the paper with tutorial installation steps.

## Revised 25-minute oral structure

| Minutes | Topic | Proposed speaker |
|---|---|---|
| 0–3 | Question, literature and distinction from the source paper | Colin |
| 3–7 | Complete architecture and field transformations | Andre |
| 7–11 | Link, photon/noise budget and performance limits | Colin |
| 11–15 | Modulator/material model and numerical verification | Andre |
| 15–20 | Executed interference results and alternative | Colin |
| 20–23 | Power/drive tradeoff and dominant limitations | Andre |
| 23–25 | Joint conclusions, scope and contributions | Both |

Assumes 25 minutes of presentation; if course Q&A is included, shorten the results segment. Both partners should write and review portions beyond their speaking sections.

## Author-contribution statement to finalize honestly

“[Name]: [completed modeling, calculations, experiments and writing]. [Name]: [completed modeling, calculations, experiments and writing]. Both authors contributed to manuscript revision, interpretation and oral presentation.”

Do not turn the planned assignments into claims of completed student work. Confirm how the course expects computational assistance to be acknowledged.

## Sources and claim boundaries

The assignment PDF is the authority for format and rubric. The supplied Combined Optics Proposal is the authority for the intended hypothesis and assumed baseline. `REFERENCES.md` retains the literature list. The Nature paper motivates the laser/ranging architecture; Hai et al. motivate coding in a different architecture; neither establishes the proposed coherent-FMCW advantage. Existing numerical evidence is in `VERIFICATION.md` and the saved raw results. No new literature novelty assessment or executed Tidy3D result is claimed by this review.
