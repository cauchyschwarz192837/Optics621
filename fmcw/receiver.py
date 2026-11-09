"""Oversampled causal Butterworth receiver and stationary PSD weighting.

Digital Butterworth at fsim approximates the analog receiver. Compare 4x/8x/16x.
The weighting includes aliases of receiver noise and restricts the analysis band.
Finite-window covariance is approximated by a circulant covariance; H0 thresholds
are therefore obtained from independent simulations, never an analytic chi-square.
"""
import numpy as np
from scipy.signal import butter, sosfilt, sosfreqz
from scipy.integrate import trapezoid
from .config import Q

class Receiver:
    def __init__(self,cfg,band="full"):
        self.cfg=cfg
        self.n=round(cfg.duration_s*cfg.adc_hz)
        self.pre=round(cfg.prehistory_s*cfg.sim_hz)
        self.t=np.arange(-self.pre,self.n*cfg.oversample)/cfg.sim_hz
        self.sos=butter(cfg.filter_order,cfg.receiver_hz,fs=cfg.sim_hz,output="sos")
        self.freq=np.fft.rfftfreq(self.n,1/cfg.adc_hz)
        shape=np.zeros_like(self.freq)
        for k in range(cfg.oversample):
            _,h=sosfreqz(self.sos,worN=2*np.pi*(self.freq+k*cfg.adc_hz)/cfg.sim_hz)
            shape+=abs(h)**2
        keep=(self.freq>=.05e6)&(self.freq<=.95*cfg.receiver_hz)
        if band=="sideband": keep &= (self.freq>=cfg.sideband_low_hz)&(self.freq<=cfg.sideband_high_hz)
        if band not in ("full","sideband"): raise ValueError(band)
        self.weight=keep/np.sqrt(np.maximum(shape,1e-8))
        self.band=band
    def sample(self,x):
        return sosfilt(self.sos,x,axis=-1)[...,self.pre::self.cfg.oversample][...,:self.n]
    def whiten(self,x):
        return np.fft.irfft(np.fft.rfft(x,axis=-1)*self.weight,n=self.n,axis=-1)
    def process(self,x): return self.whiten(self.sample(x))
    def noise_psd(self,pa=0.,pb=0.):
        c=self.cfg
        return 2*Q*c.responsivity*(c.lo_w+pa+pb+c.background_w)+c.electronics_a_rt_hz**2
    def enbw(self):
        f=np.linspace(0,self.cfg.sim_hz/2,65537)
        _,h=sosfreqz(self.sos,worN=f,fs=self.cfg.sim_hz)
        return trapezoid(abs(h)**2,f)
