"""Periodic declared codes with continuous raised-cosine transitions; complex MZM."""
import numpy as np


def chips(seed, length):
    return np.random.default_rng(seed).choice([-1., 1.], length)


def shaped_code(t, cfg, seed):
    """Periodic code, including negative-time history; transition begins at each chip edge."""
    seq = chips(seed, cfg.code_length)
    x = np.asarray(t)*cfg.chip_hz
    j = np.floor(x).astype(int)
    frac = x-j
    width = min(cfg.code_rise_s*cfg.chip_hz, 1.)
    w = .5-.5*np.cos(np.pi*np.minimum(frac/width, 1.))
    return seq[(j-1) % len(seq)]*(1-w)+seq[j % len(seq)]*w


def voltage(t, cfg, seed):
    return cfg.bias_v + cfg.drive_v*shaped_code(t,cfg,seed)*np.cos(2*np.pi*cfg.carrier_hz*t)


def transfer(v, cfg):
    """V is differential arm voltage: phi1-phi2=pi*V/Vpi.

    Imbalance is fractional ARM POWER imbalance. Insertion is common power loss.
    residual_chirp multiplies the differential phase to give common phase / 2.
    """
    d = np.pi*np.asarray(v)/cfg.vpi_v
    a = np.sqrt(1+cfg.arm_imbalance)
    b = np.sqrt(1-cfg.arm_imbalance)
    return np.sqrt(10**(-cfg.insertion_db/10))*.5*(a*np.exp(.5j*d)+b*np.exp(-.5j*d))*np.exp(.5j*cfg.residual_chirp*d)


def field(t, cfg, coded=True, seed=None, small=False):
    if not coded: return np.ones_like(t, dtype=complex)
    seed = cfg.code_seed_a if seed is None else seed
    v = voltage(t,cfg,seed)
    if not small: return transfer(v,cfg)
    eps = cfg.vpi_v*1e-5
    derivative = (transfer(cfg.bias_v+eps,cfg)-transfer(cfg.bias_v-eps,cfg))/(2*eps)
    return transfer(cfg.bias_v,cfg)+derivative*(v-cfg.bias_v)


def power_budget(cfg, coded=True):
    t = np.arange(round(cfg.duration_s*cfg.sim_hz))/cfg.sim_hz
    m = field(t,cfg,coded)
    transmission = float(np.mean(abs(m)**2))
    if transmission < 1e-12: raise ValueError("MZM transmits effectively no power")
    source = cfg.launch_w/transmission if cfg.power_mode == "equal_launch" else cfg.source_w
    launch = source*transmission
    area = np.pi*(cfg.aperture_m/2)**2
    collected = launch*cfg.reflectance*area*cfg.path_transmission/(np.pi*cfg.range_m**2)
    return dict(transmission=transmission, source_w=source, launch_w=launch,
                peak_launch_w=float(source*np.max(abs(m)**2)), collected_w=collected,
                coherent_w=collected*cfg.coupling)


def normalized_field(t,cfg,coded=True,seed=None,small=False):
    ref = np.arange(round(cfg.duration_s*cfg.sim_hz))/cfg.sim_hz
    norm = np.sqrt(np.mean(abs(field(ref,cfg,coded,seed,small))**2))
    return field(t,cfg,coded,seed,small)/max(norm,1e-15)
