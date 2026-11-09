"""Paired finite-linewidth control. Run from project root: python -m hybrid.ranging."""
import csv,json
from pathlib import Path
from fmcw.config import Config
from fmcw.simulation import simulate
from fmcw.calibration import calibrate
from fmcw.estimation import Estimator

def main():
    out=Path('hybrid/output')
    src=json.loads((out/'source.json').read_text())
    c=Config(sweep_hz=src['MHz_per_V']*1e6*5,search_min_m=47.,search_max_m=53.,search_step_m=.025)
    c=c.updated(isr_db=10.,interferer_offset_hz=c.slope*(c.interferer_delay_s-c.delay(50.45)))
    c.validate();c.save(out/'ranging_config.json')
    template,_=calibrate(c,341700)
    with (out/'paired.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['method','seed','ISR_dB','range_m'])
        for label,coded,band,wrong in [('uncoded',False,'full',False),('matched',True,'sideband',False),('wrong code',True,'sideband',True)]:
            est=Estimator(template.updated(code_seed_a=941) if wrong else template,coded,False,band)
            for level in [None,10.]:
                for seed in range(841000,841040):
                    y=simulate(c.updated(isr_db=level),coded,seed,band=band).processed
                    r,_=est.estimate(y);w.writerow([label,seed,level,r])
if __name__=='__main__': main()
