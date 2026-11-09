"""One target (optionally coherent scatterers), one independent foreign laser."""
from dataclasses import dataclass
import numpy as np
from .source import target_phase, foreign_phase, brownian_at
from .modulator import normalized_field, power_budget
from .receiver import Receiver

@dataclass
class Trial:
    adc: np.ndarray
    processed: np.ndarray
    noise_psd: float
    budget: dict
    clipped_fraction: float


def simulate(cfg,coded=True,seed=0,target_present=True,band="full"):
    cfg.validate()
    rng=np.random.default_rng(seed)
    rx=Receiver(cfg,band); t=rx.t
    budget=power_budget(cfg,coded)
    pc=budget['coherent_w']; pr=budget['collected_w']
    reference=pc if cfg.foreign_reference_coherent_w is None else cfg.foreign_reference_coherent_w
    pb=0 if cfg.isr_db is None else reference*10**(cfg.isr_db/10)
    # ISR is always referenced to nominal desired power, also under target-absent H0.
    count=cfg.scatterer_count
    ranges=cfg.range_m+(rng.normal(0,cfg.depth_std_m,count) if count>1 else np.zeros(1))
    delays=np.array([cfg.delay(r) for r in ranges])
    if min(delays)<0 or max(delays)>cfg.prehistory_s-2e-6:
        raise ValueError("Scatterer delays outside simulated history")
    histories=brownian_at([t]+[t-tau for tau in delays],cfg.linewidth_hz,rng)
    lo=histories[0]
    current=np.zeros_like(t)
    if target_present:
        for j,tau in enumerate(delays):
            phase=target_phase(t,tau,cfg)+histories[j+1]-lo+rng.uniform(-np.pi,np.pi)
            u=normalized_field(t-tau,cfg,coded)
            current += 2*cfg.responsivity*np.sqrt(cfg.lo_w*pc/count)*np.real(u*np.exp(1j*phase))
    if pb>0:
        offset=rng.uniform(0,cfg.code_length/cfg.chip_hz)
        bphase=brownian_at([t-cfg.interferer_delay_s],cfg.interferer_linewidth_hz,rng)[0]
        phase=foreign_phase(t,cfg)+bphase-lo+rng.uniform(-np.pi,np.pi)
        u=normalized_field(t-cfg.interferer_delay_s-offset,cfg,cfg.interferer_coded,cfg.code_seed_b)
        current += 2*cfg.responsivity*np.sqrt(cfg.lo_w*pb)*np.real(u*np.exp(1j*phase))
    psd=rx.noise_psd(pr if target_present else 0,pb/cfg.coupling)
    if cfg.noise: current += rng.normal(0,np.sqrt(psd*cfg.sim_hz/2),len(t))
    sampled=rx.sample(current)
    clipped=0.
    if cfg.clipping_a is not None:
        clipped=float(np.mean(abs(sampled)>cfg.clipping_a))
        sampled=np.clip(sampled,-cfg.clipping_a,cfg.clipping_a)
    return Trial(sampled,rx.whiten(sampled),psd,budget,clipped)
