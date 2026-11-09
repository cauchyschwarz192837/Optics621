"""Generate selected experiment configs or execute a declared campaign.

Default creates a reviewable plan only. --execute runs local Monte Carlo simulations.
The full plan is intentionally staged. No component cloud solves are launched.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from fmcw.config import load
from fmcw.modulator import power_budget


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',choices=['primary','power','bias_drive','robustness'],default='primary')
    p.add_argument('--config',default='config/baseline.json')
    p.add_argument('--root',default='results/campaign')
    p.add_argument('--trials',type=int,default=500)
    p.add_argument('--null-trials',type=int,default=2000)
    p.add_argument('--execute',action='store_true')
    a=p.parse_args();root=Path(a.root)/a.stage;root.mkdir(parents=True,exist_ok=True)
    cfg=load(a.config).updated(oversample=8)
    cases=[]
    if a.stage=='primary':
        for scenario in ['overlap','crossing','out_of_band']:
            cases.append((scenario,cfg,scenario,'none,-20,-10,0,10,20,30'))
    elif a.stage=='power':
        for mode in ['equal_launch','equal_source']:
            cases.append((mode,cfg.updated(power_mode=mode),'overlap','none,0,10,20'))
            reference=power_budget(cfg.updated(power_mode='equal_launch'),False)['coherent_w']
            cases.append((mode+'_fixed_foreign',cfg.updated(power_mode=mode,foreign_reference_coherent_w=reference),'overlap','none,0,10,20'))
    elif a.stage=='bias_drive':
        for bias in [.4,.5,.6]:
            for drive in [.1,.3,.6]:
                cases.append((f'b{bias}_d{drive}',cfg.updated(bias_v=bias*cfg.vpi_v,drive_v=drive*cfg.vpi_v),'overlap','none,10,20'))
    else:
        for lw in [3e3,50e3,300e3]:
            cases.append((f'linewidth_{lw:g}',cfg.updated(linewidth_hz=lw,interferer_linewidth_hz=lw),'overlap','none,10'))
        for coupling in [.01,.3]:
            cases.append((f'coupling_{coupling}',cfg.updated(coupling=coupling),'overlap','none,10'))
        for r in [10.,100.]:
            cases.append((f'range_{r:g}',cfg.updated(range_m=r,search_min_m=5.,search_max_m=105.),'overlap','none,10'))
        for err in [-.001,.001]:
            cases.append((f'mzi_delay_error_{err}',cfg.updated(mzi_delay_fraction_error=err,chirp_error_hz=2e5,slope_error=.001),'overlap','none,10'))
        cases.append(('speckle',cfg.updated(scatterer_count=8,depth_std_m=.005),'overlap','none,10'))
        cases.append(('clipping',cfg.updated(clipping_a=2e-7),'overlap','none,20'))
    plan=[]
    for name,c,scenario,isr in cases:
        path=root/f'{name}.json';c.save(path)
        cmd=[sys.executable,'-m','fmcw.cli','mc','--config',str(path),'--out',str(root/name),
             '--scenario',scenario,'--isr',isr,'--trials',str(a.trials),'--null-trials',str(a.null_trials)]
        plan.append(dict(name=name,command=cmd))
    (root/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(f'{len(plan)} cases saved to {root}/plan.json; each case includes 4 estimators.',flush=True)
    if a.execute:
        for item in plan:
            print('Running',item['name'],flush=True)
            subprocess.run(item['command'],check=True)
    else: print('Inspect the plan; rerun with --execute to compute it.')

if __name__=='__main__':main()
