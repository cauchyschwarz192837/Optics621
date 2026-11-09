"""Reproducible analytical budget; not empirical system performance."""
import argparse, csv, json
from pathlib import Path
import numpy as np
from fmcw.config import load, C, Q
from fmcw.modulator import power_budget
from fmcw.receiver import Receiver

def evaluate(c):
    b=power_budget(c,True); u=power_budget(c,False)
    photon=6.62607015e-34*C/c.wavelength_m
    zr=np.pi*.005**2/c.wavelength_m
    psd=Receiver(c).noise_psd(b['collected_w'])
    cnr=4*c.responsivity**2*c.lo_w*b['coherent_w']*c.duration_s/psd
    rows=[]
    def add(k,v,unit,basis): rows.append(dict(quantity=k,value=float(v),unit=unit,basis=basis))
    add('sweep_resolution',c.resolution_m,'m','Optical sweep scale, not isolated-target precision')
    add('target_delay',c.delay(c.range_m),'s','Configured air index and internal delay')
    add('beat_frequency',c.slope*c.delay(c.range_m),'Hz','Stationary target; linear sweep')
    add('collected_power',b['collected_w'],'W','Extended Lambertian target')
    add('coherent_power',b['coherent_w'],'W','Assumed mode and polarization coupling')
    add('coherent_photons_per_ramp',b['coherent_w']*c.duration_s/photon,'photons','Coherent mode equivalent; before detector efficiency')
    add('lo_shot_density',np.sqrt(2*Q*c.responsivity*c.lo_w),'A/sqrt(Hz)','One-sided PSD')
    add('white_noise_cnr',10*np.log10(cnr),'dB','Unmodulated equal-power reference; no interference or phase noise')
    add('white_noise_range_bound',c.resolution_m*np.sqrt(3)/(np.pi*np.sqrt(cnr)),'m','Unknown-phase real sinusoid; not a coded-system guarantee')
    add('coherence_magnitude',np.exp(-np.pi*c.linewidth_hz*c.delay(c.range_m)),'1','Lorentzian linewidth')
    add('gaussian_rayleigh_length',zr,'m','Assumed 5 mm vacuum waist, M squared = 1')
    add('gaussian_radius_at_target',.005*np.sqrt(1+(c.range_m/zr)**2),'m','Ideal free-space Gaussian; no turbulence')
    add('mzm_incident_power',b['source_w'],'W','Branch power, not total laser output')
    add('total_source_budget',(b['source_w']+c.lo_w+.0001)/.95,'W','Illustrative 0.1 mW calibration tap and 95% allocation efficiency')
    add('uncoded_total_source_budget',(u['source_w']+c.lo_w+.0001)/.95,'W','Same allocation assumptions, MZM bypass')
    add('slope_fraction_for_1cm',.01/c.range_m,'1','Single-error allowance; not combined budget')
    add('delay_error_for_1cm',2*c.air_index*.01/C,'s','Single-error allowance')
    add('air_index_fraction_for_1cm',.01/c.range_m,'1','Relative index error; single-error allowance')
    add('sideband_main_lobe_upper_edge',c.slope*c.delay(c.search_max_m)+c.carrier_hz+c.chip_hz,'Hz','Allocation only; code and harmonic tails remain')
    add('one_ramp_rate_upper_bound',1/c.duration_s,'Hz','Excludes retrace and processing overhead')
    add('up_down_pair_rate_upper_bound',1/(2*c.duration_s),'Hz','Pair not implemented; excludes overhead')
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default='config/baseline.json');p.add_argument('--out',default='results/requirements_review')
    a=p.parse_args();c=load(a.config);out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    rows=evaluate(c)
    with (out/'budget.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'budget.json').write_text(json.dumps(rows,indent=2)+'\n');c.save(out/'config.json')
    print('\n'.join(f"{r['quantity']}: {r['value']:.7g} {r['unit']}" for r in rows))
if __name__=='__main__':main()
