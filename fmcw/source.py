"""Analytical heterodyne phase; no sampling of the 193 THz carrier or optical sweep."""
import numpy as np


def error_phase(t,cfg):
    w = 2*np.pi*cfg.chirp_cycles/cfg.duration_s
    return -2*np.pi*cfg.chirp_error_hz*np.cos(w*t)/w


def target_phase(t,tau,cfg):
    s = cfg.slope*(1+cfg.slope_error)
    return -2*np.pi*s*tau*t + np.pi*s*tau*tau + error_phase(t-tau,cfg)-error_phase(t,cfg)


def foreign_phase(t,cfg):
    sa = cfg.slope*(1+cfg.slope_error)
    sb = cfg.slope*cfg.interferer_slope_ratio
    tau = cfg.interferer_delay_s
    return 2*np.pi*cfg.interferer_offset_hz*t+np.pi*(sb*(t-tau)**2-sa*t*t)-error_phase(t,cfg)


def brownian_at(query_arrays, linewidth, rng):
    """Exact joint Wiener values at arbitrary query times (no rounded delays).

    Build the sorted UNION of query times and sample independent increments there.
    This preserves correlations between delayed A and its LO, even below one timestep.
    """
    sizes = [np.asarray(x).size for x in query_arrays]
    times = np.concatenate(query_arrays)
    unique, inverse = np.unique(times,return_inverse=True)
    dt = np.diff(unique,prepend=unique[0])
    walk = np.cumsum(rng.normal(size=len(unique))*np.sqrt(2*np.pi*linewidth*dt))
    values = walk[inverse]
    return np.split(values,np.cumsum(sizes)[:-1])
