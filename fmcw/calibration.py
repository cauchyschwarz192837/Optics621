"""Independent synthetic MZM coherent sweep and noisy delay-MZI phase calibration."""
from dataclasses import asdict
import numpy as np
from scipy.optimize import least_squares
from .modulator import transfer
from .source import target_phase


def calibrate(cfg,seed=77):
    rng=np.random.default_rng(seed)
    # Known voltage sweep, coherently measured field (amplitude AND phase reference).
    v=np.linspace(-1.5*cfg.vpi_v,1.5*cfg.vpi_v,301)
    noise=cfg.calibration_noise
    measured=transfer(v,cfg)+noise*(rng.normal(size=v.size)+1j*rng.normal(size=v.size))
    def residual(p):
        model=transfer(v,cfg.updated(vpi_v=p[0],insertion_db=p[1],arm_imbalance=p[2],residual_chirp=p[3]))
        d=model-measured
        return np.r_[d.real,d.imag]
    fit=least_squares(residual,[cfg.vpi_v*.95,3.,.01,0.],
                      bounds=([cfg.vpi_v*.5,0,0,-1],[cfg.vpi_v*1.5,15,.95,1]))
    # Bias voltage measured by independent readback; driver amplitude assumed known.
    bias=cfg.bias_v+rng.normal(0,noise*cfg.vpi_v)
    # MZI yields unwrapped phase, not an optical-frequency waveform. Fit identifiable
    # slope and the declared sinusoidal error basis, with a free constant phase.
    t=np.linspace(0,cfg.duration_s,2000,endpoint=False)
    actual_tau=cfg.mzi_delay_s*(1+cfg.mzi_delay_fraction_error)
    y=target_phase(t,actual_tau,cfg)+rng.normal(0,noise,len(t))
    base=cfg.updated(slope_error=0,chirp_error_hz=0)
    slope_basis=target_phase(t,cfg.mzi_delay_s,base)
    error_basis=target_phase(t,cfg.mzi_delay_s,base.updated(chirp_error_hz=1))-slope_basis
    design=np.column_stack([slope_basis,error_basis,np.ones_like(t)])
    coefficients=np.linalg.lstsq(design,y,rcond=None)[0]
    est=cfg.updated(vpi_v=float(fit.x[0]),insertion_db=float(fit.x[1]),
        arm_imbalance=float(fit.x[2]),residual_chirp=float(fit.x[3]),bias_v=float(bias),
        slope_error=float(coefficients[0]-1),chirp_error_hz=float(coefficients[1]))
    report={"seed":seed,"measurement":"coherently referenced MZM field; unwrapped MZI phase",
            "fit_success":bool(fit.success),"mzm_residual_rms":float(np.sqrt(np.mean(fit.fun**2))),
            "mzi_residual_rms_rad":float(np.std(y-design@coefficients)),
            "estimated":{k:asdict(est)[k] for k in ['vpi_v','insertion_db','arm_imbalance','residual_chirp','bias_v','slope_error','chirp_error_hz']},
            "caveat":"Synthetic calibration assumes known MZI delay and known chirp-error basis. Delay error remains systematic."}
    return est,report
