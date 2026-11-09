"""Unknown-amplitude/phase subspace search, using filtered real quadratures."""
import numpy as np
from scipy.optimize import minimize_scalar
from .receiver import Receiver
from .source import target_phase
from .modulator import normalized_field
from .config import C

class Estimator:
    def __init__(self,cfg,coded=True,small=False,band="full"):
        self.cfg=cfg; self.coded=coded; self.small=small
        self.rx=Receiver(cfg,band)
        self.ranges=np.arange(cfg.search_min_m,cfg.search_max_m+cfg.search_step_m/2,cfg.search_step_m)
        self.ranges=self.ranges[self.ranges<=cfg.search_max_m]
        if self.ranges[-1]<cfg.search_max_m: self.ranges=np.r_[self.ranges,cfg.search_max_m]
        self.bank=np.stack([self.basis(r) for r in self.ranges])
        self.flat=self.bank.reshape(-1,self.rx.n)
    def basis(self,r):
        tau=self.cfg.delay(r); t=self.rx.t
        z=normalized_field(t-tau,self.cfg,self.coded,small=self.small)*np.exp(1j*target_phase(t,tau,self.cfg))
        h=self.rx.process(np.stack([z.real,-z.imag])).T
        # QR handles nonorthogonal quadratures and unequal filtered energies.
        q,_=np.linalg.qr(h,mode='reduced')
        return q.T
    def scores(self,y):
        projections=(self.flat@y).reshape(-1,2)
        return np.sum(projections**2,axis=1)
    def estimate(self,y,refine=True):
        scores=self.scores(y)
        j=int(np.argmax(scores)); r=float(self.ranges[j]); score=float(scores[j])
        if refine:
            lo=self.ranges[max(0,j-1)]; hi=self.ranges[min(len(scores)-1,j+1)]
            if hi>lo:
                fit=minimize_scalar(lambda x:-float(np.sum((self.basis(x)@y)**2)),
                     bounds=(lo,hi),method='bounded',options={'xatol':1e-5})
                if -fit.fun>score: r,score=float(fit.x),float(-fit.fun)
        return r,score
    def overlap(self,r1,r2):
        """Largest principal overlap, maximized over both unknown phases."""
        return float(np.linalg.svd(self.basis(r1)@self.basis(r2).T,compute_uv=False)[0])


def fft_range(adc,cfg):
    """Uncoded spectral initializer; continuous template refinement is the main result."""
    n=len(adc); spec=abs(np.fft.rfft(adc*np.hanning(n),n=8*n))
    f=np.fft.rfftfreq(8*n,1/cfg.adc_hz)
    r=(f/(cfg.slope*(1+cfg.slope_error))-cfg.internal_delay_s)*C/(2*cfg.air_index)
    mask=(r>=cfg.search_min_m)&(r<=cfg.search_max_m)
    j=np.flatnonzero(mask)[np.argmax(spec[mask])]
    return float(r[j])


def fisher_bound(estimator,range_m,amplitude_a,noise_psd,phase=0.):
    """Local projected-template information under stationary whitened-noise approximation.

    Includes unknown amplitude/phase nuisance parameters. No phase noise/interference.
    Finite window whitening is approximate, as it is for the estimator.
    """
    cfg=estimator.cfg; rx=estimator.rx
    def waveform(r):
        tau=cfg.delay(r)
        z=normalized_field(rx.t-tau,cfg,estimator.coded,small=estimator.small)*np.exp(1j*(target_phase(rx.t,tau,cfg)+phase))
        return amplitude_a*rx.process(z.real)
    eps=1e-4
    derivative=(waveform(range_m+eps)-waveform(range_m-eps))/(2*eps)
    q=estimator.basis(range_m)
    residual=derivative-q.T@(q@derivative)
    info=np.dot(residual,residual)/(noise_psd*cfg.adc_hz/2)
    return float(1/np.sqrt(info))
