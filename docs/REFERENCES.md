# Sources and implementation references

## Supplied project sources

- `Combined_Optics_Proposal.tex`: the four-page combined project proposal supplied in this conversation. Source for research scope, baseline parameters, proposed comparisons and performance objectives.
- `Optic Project(1).pdf`: prior project-planning conversation supplied in this conversation. The relevant final sections specify the Python system / Tidy3D component division, local mode characterization, power normalization, independent calibration and staged experiments. Earlier unrelated project ideas are not implemented.

The following bibliography entries are retained from the supplied proposal. Their numerical claims are not independently re-validated by this code package:

1. V. Snigirev et al., “Ultrafast tunable lasers using lithium niobate integrated photonics,” Nature 615, 411–417 (2023). https://doi.org/10.1038/s41586-023-05724-2
2. X. Zhang, J. Pouls, and M. C. Wu, “Laser frequency sweep linearization by iterative learning pre-distortion for FMCW LiDAR,” Optics Express 27, 9965–9974 (2019). https://doi.org/10.1364/OE.27.009965
3. E. Baumann et al., “Speckle phase noise in coherent laser ranging: fundamental precision limitations,” Optics Letters 39, 4776–4779 (2014). https://doi.org/10.1364/OL.39.004776
4. Y. Hai et al., “Immunity to mutual interference in coded phase-shift LiDAR,” Journal of Lightwave Technology 41, 570–577 (2023). https://doi.org/10.1109/JLT.2022.3219920
5. S. M. Kay, Fundamentals of Statistical Signal Processing, Vol. I: Estimation Theory (1993).

Hai's architecture differs from optical FMCW coherent detection. This implementation tests the transfer hypothesis; it does not treat the paper as proof of a coding advantage here.

## Official component documentation consulted during implementation

- Flexcompute TFLN electro-optic modulator tutorial: https://www.flexcompute.com/tidy3d/examples/notebooks/TFLNTidy3d/
- Local ModeSolver API: https://docs.flexcompute.com/projects/tidy3d/en/latest/api/_autosummary/tidy3d.plugins.mode.ModeSolver.html
- ModeSolver tutorial: https://www.flexcompute.com/tidy3d/examples/notebooks/ModeSolver/
- Anisotropic material API: https://docs.flexcompute.com/projects/tidy3d/en/stable/api/mediums.html

The official TFLN tutorial uses an optical/RF workflow and refers to Ying Li et al., ACS Omega 8, 9644–9651 (2023), https://doi.org/10.1021/acsomega.3c00310. The included component script is deliberately simpler: local optical mode solves with an assumed uniform RF field. It is not a reproduction of that device or its reported VπL.

Documentation was checked during package preparation. Optional Tidy3D execution remains unverified in this environment. Record the actual installed version, use one consistent solver interface, and inspect local-solver warnings about smoothing or optional extras.
