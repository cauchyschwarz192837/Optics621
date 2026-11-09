"""One explicit, serializable parameter interface for every experiment."""
from dataclasses import dataclass, asdict, replace
import json
from pathlib import Path

C = 299792458.0
Q = 1.602176634e-19

@dataclass(frozen=True)
class Config:
    wavelength_m: float = 1550e-9
    sweep_hz: float = 0.5e9
    duration_s: float = 100e-6
    adc_hz: float = 50e6
    oversample: int = 4
    prehistory_s: float = 8e-6
    receiver_hz: float = 20e6
    filter_order: int = 8
    range_m: float = 50.0
    search_min_m: float = 10.0
    search_max_m: float = 100.0
    search_step_m: float = 0.075
    air_index: float = 1.0
    internal_delay_s: float = 0.0
    launch_w: float = 10e-3
    source_w: float = 40e-3
    power_mode: str = "equal_launch"
    reflectance: float = 0.20
    aperture_m: float = 0.025
    path_transmission: float = 0.30
    coupling: float = 0.10
    lo_w: float = 0.5e-3
    responsivity: float = 0.9
    electronics_a_rt_hz: float = 5e-12
    background_w: float = 0.0
    noise: bool = True
    linewidth_hz: float = 50e3
    interferer_linewidth_hz: float = 50e3
    chirp_error_hz: float = 0.0
    chirp_cycles: float = 2.0
    slope_error: float = 0.0
    vpi_v: float = 4.0
    bias_v: float = 2.0
    drive_v: float = 1.2
    insertion_db: float = 3.0
    arm_imbalance: float = 0.0
    residual_chirp: float = 0.0
    carrier_hz: float = 5e6
    chip_hz: float = 1e6
    code_length: int = 100
    code_rise_s: float = 0.1e-6
    code_seed_a: int = 621
    code_seed_b: int = 622
    seed: int = 20261104
    isr_db: float | None = None
    foreign_reference_coherent_w: float | None = None
    interferer_offset_hz: float = 0.0
    interferer_slope_ratio: float = 1.0
    interferer_delay_s: float = 400e-9
    interferer_coded: bool = True
    sideband_low_hz: float = 4.5e6
    sideband_high_hz: float = 10e6
    clipping_a: float | None = None
    scatterer_count: int = 1
    depth_std_m: float = 0.0
    mzi_delay_s: float = 1.468 * 10 / C
    mzi_delay_fraction_error: float = 0.0
    calibration_noise: float = 0.003

    @property
    def slope(self): return self.sweep_hz / self.duration_s
    @property
    def sim_hz(self): return self.adc_hz * self.oversample
    @property
    def resolution_m(self): return C / (2*self.air_index*self.sweep_hz)
    def delay(self, r): return 2*self.air_index*r/C + self.internal_delay_s
    def updated(self, **kwargs): return replace(self, **kwargs)
    def validate(self):
        if self.power_mode not in ("equal_launch", "equal_source"):
            raise ValueError("power_mode must be equal_launch or equal_source")
        if not isinstance(self.oversample, int) or self.oversample < 2:
            raise ValueError("Use integer oversample >=2; perform rate convergence")
        if not 0 < self.receiver_hz < self.adc_hz/2:
            raise ValueError("Receiver cutoff must be below ADC Nyquist")
        if not 0 < self.search_min_m < self.search_max_m:
            raise ValueError("Invalid positive range search")
        if not self.search_min_m <= self.range_m <= self.search_max_m:
            raise ValueError("Target must lie within search")
        if self.search_step_m > self.resolution_m/3:
            raise ValueError("Search spacing too coarse: use <= resolution/3")
        if self.prehistory_s < max(self.delay(self.search_max_m), self.interferer_delay_s)+2e-6:
            raise ValueError("Insufficient prehistory")
        if min(self.vpi_v,self.duration_s,self.chip_hz,self.code_rise_s,self.coupling) <= 0:
            raise ValueError("Positive physical parameters required")
        if not 0 <= self.arm_imbalance < 1 or self.scatterer_count < 1:
            raise ValueError("Invalid arm imbalance/scatterer count")
        if self.depth_std_m < 0 or self.linewidth_hz < 0 or self.interferer_linewidth_hz < 0:
            raise ValueError("Negative stochastic scale")
        if self.foreign_reference_coherent_w is not None and self.foreign_reference_coherent_w <= 0:
            raise ValueError("Foreign reference power must be positive")
        # Conservative finite numerical guard, not a proof of band limitation.
        ends = [0, self.duration_s]
        beat = max(abs(self.interferer_offset_hz + self.slope*(self.interferer_slope_ratio-1)*t
                       - self.slope*self.interferer_slope_ratio*self.interferer_delay_s) for t in ends)
        if self.isr_db is not None and beat+6*self.carrier_hz+5*self.chip_hz > .45*self.sim_hz:
            raise ValueError("Interferer/harmonics too close to internal Nyquist: increase oversample")
        return self
    def save(self, path): Path(path).write_text(json.dumps(asdict(self), indent=2)+"\n")


def load(path=None):
    return (Config(**json.loads(Path(path).read_text())) if path else Config()).validate()
