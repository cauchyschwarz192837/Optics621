"""Compact final-evidence plan; execution is explicit and may take substantial time."""
import argparse,json,subprocess,sys
from pathlib import Path
from fmcw.config import load
from fmcw.modulator import power_budget

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute',action='store_true')
    p.add_argument('--root',default='results/submission');a=p.parse_args()
    root=Path(a.root);root.mkdir(parents=True,exist_ok=True)
    c=load('config/baseline.json').updated(oversample=8)
    ref=power_budget(c,False)['coherent_w']
    cases=[('primary',c,'overlap','none,0,10,20'),
      ('crossing',c,'crossing','10'),('out_of_band',c,'out_of_band','10'),
      ('source_fixed_foreign',c.updated(power_mode='equal_source',foreign_reference_coherent_w=ref),'overlap','none,10'),
      ('launch_fixed_foreign',c.updated(foreign_reference_coherent_w=ref),'overlap','none,10'),
      ('rate16',c.updated(oversample=16),'overlap','none,10'),
      ('calibration',c.updated(mzi_delay_fraction_error=.001,chirp_error_hz=2e5,slope_error=.001),'overlap','none,10'),
      ('linewidth',c.updated(linewidth_hz=300e3,interferer_linewidth_hz=300e3),'overlap','none,10')]
    for bias,drive in [(.4,.1),(.6,.6)]:
        cases.append((f'bias{bias}_drive{drive}',c.updated(bias_v=bias*c.vpi_v,drive_v=drive*c.vpi_v),'overlap','none,10'))
    plan=[]
    for name,cfg,scenario,isr in cases:
        cfg.validate();path=root/f'{name}.json';cfg.save(path)
        cmd=[sys.executable,'-m','fmcw.cli','mc','--config',str(path),'--out',str(root/name),'--scenario',scenario,'--isr',isr,'--trials','500','--null-trials','2000','--methods','uncoded,small_signal,full_field,sideband']
        plan.append(dict(name=name,command=cmd,status='planned'))
    (root/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    print(f'Wrote {len(plan)} cases; no results implied by plan.')
    if a.execute:
        for item in plan: subprocess.run(item['command'],check=True)
if __name__=='__main__': main()
