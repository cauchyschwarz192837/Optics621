"""Physics invariants, independently calculated baselines, and statistical sanity checks.

Can run with stdlib unittest or pytest. Reduced search span saves time in CI.
"""
import unittest
import numpy as np
from scipy.signal import sosfreqz
from fmcw.config import Config,C,Q
from fmcw.source import brownian_at,target_phase
from fmcw.modulator import transfer,power_budget,normalized_field
from fmcw.receiver import Receiver
from fmcw.simulation import simulate
from fmcw.estimation import Estimator,fisher_bound
from fmcw.calibration import calibrate
from fmcw.metrics import interval

class PhysicsTests(unittest.TestCase):
    def setUp(self):
        self.c=Config(search_min_m=49.5,search_max_m=50.5,search_step_m=.075,
            noise=False,linewidth_hz=0,interferer_linewidth_hz=0)
    def test_link_budget(self):
        p=power_budget(self.c,False)
        self.assertAlmostEqual(p['collected_w']/37.5e-12,1.,places=12)
        self.assertAlmostEqual(p['coherent_w']/3.75e-12,1.,places=12)
    def test_beat_and_resolution(self):
        t=np.array([0,1e-6]); tau=self.c.delay(50)
        f=abs(np.diff(target_phase(t,tau,self.c))[0]/(2*np.pi*1e-6))
        self.assertAlmostEqual(f,2*50*self.c.slope/C,places=7)
        self.assertAlmostEqual(self.c.resolution_m,.299792458,places=9)
    def test_mzm_signed_field(self):
        c=self.c
        self.assertLess(transfer(1.5*c.vpi_v,c).real,0)
        self.assertAlmostEqual(abs(transfer(c.vpi_v,c)),0.,places=12)
        c=c.updated(arm_imbalance=.15,residual_chirp=.2)
        self.assertGreater(abs(transfer(c.vpi_v,c)),0)
    def test_power_normalization(self):
        t=np.arange(20000)/self.c.sim_hz
        self.assertAlmostEqual(np.mean(abs(normalized_field(t,self.c))**2),1.,places=12)
        a=power_budget(self.c,True); b=power_budget(self.c,False)
        self.assertAlmostEqual(a['launch_w'],b['launch_w'])
        self.assertGreater(a['source_w'],b['source_w'])
    def test_fractional_delay_wiener_variance(self):
        rng=np.random.default_rng(8); tau=3.37e-7; linewidth=50e3
        # Intervals disjoint: independent phase increments with exact fractional delay.
        t=np.arange(50000)*2e-6
        a,b=brownian_at([t,t-tau],linewidth,rng)
        expected=2*np.pi*linewidth*tau
        self.assertLess(abs(np.var(a-b)/expected-1),.025)
        coherence=abs(np.mean(np.exp(1j*(a-b))))
        self.assertAlmostEqual(coherence,np.exp(-np.pi*linewidth*tau),delta=.003)
    def test_noise_enbw(self):
        c=self.c; rx=Receiver(c); rng=np.random.default_rng(9)
        psd=rx.noise_psd()
        x=rng.normal(0,np.sqrt(psd*c.sim_hz/2),1_000_000)
        from scipy.signal import sosfilt
        y=sosfilt(rx.sos,x)[5000:]
        self.assertLess(abs(np.var(y)/(psd*rx.enbw())-1),.02)
    def test_noiseless_off_grid_range(self):
        for coded in [False,True]:
            c=self.c.updated(range_m=50.037)
            tr=simulate(c,coded,12)
            est=Estimator(c,coded)
            r,_=est.estimate(tr.processed)
            self.assertLess(abs(r-c.range_m),2e-5)
    def test_calibration_independent_data(self):
        c=self.c.updated(vpi_v=4.3,bias_v=2.01,arm_imbalance=.1,residual_chirp=.12,
                        slope_error=.001,chirp_error_hz=2e5,calibration_noise=.001)
        est,report=calibrate(c,21)
        self.assertTrue(report['fit_success'])
        self.assertLess(abs(est.vpi_v-c.vpi_v),.01)
        self.assertLess(abs(est.slope_error-c.slope_error),2e-5)
        self.assertLess(abs(est.chirp_error_hz-c.chirp_error_hz),3000)
    def test_isr_amplitude_scaling(self):
        c=self.c.updated(isr_db=0)
        a=simulate(c,False,99,target_present=False).adc
        b=simulate(c.updated(isr_db=20),False,99,target_present=False).adc
        np.testing.assert_allclose(b,10*a,atol=1e-16)
    def test_white_noise_precision(self):
        c=self.c.updated(noise=True)
        est=Estimator(c,False)
        p=power_budget(c,False); psd=Receiver(c).noise_psd(p['collected_w'])
        amp=2*c.responsivity*np.sqrt(c.lo_w*p['coherent_w'])
        bound=fisher_bound(est,c.range_m,amp,psd)
        estimates=[est.estimate(simulate(c,False,1000+i).processed)[0] for i in range(60)]
        measured=np.std(estimates,ddof=1)
        self.assertTrue(.65 < measured/bound < 1.5,(measured,bound))
    def test_binomial_interval(self):
        lo,hi=interval(0,500)
        self.assertEqual(lo,0); self.assertTrue(.007<hi<.008)
    def test_alias_guard(self):
        with self.assertRaises(ValueError): self.c.updated(isr_db=20,interferer_offset_hz=200e6).validate()
    def test_fixed_foreign_power_across_power_modes(self):
        c=self.c.updated(isr_db=10,power_mode='equal_source',foreign_reference_coherent_w=3.75e-12)
        a=simulate(c,False,99,target_present=False).adc
        b=simulate(c,True,99,target_present=False).adc
        np.testing.assert_allclose(a,b,atol=1e-16)
    def test_complex_mzm_noiseless_ranging(self):
        c=self.c.updated(range_m=49.923,arm_imbalance=.2,residual_chirp=.3)
        tr=simulate(c,True,62)
        r,_=Estimator(c,True).estimate(tr.processed)
        self.assertLess(abs(r-c.range_m),2e-5)

if __name__=='__main__': unittest.main()
