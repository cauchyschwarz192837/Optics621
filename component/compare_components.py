"""Compare real component exports at identical bias/drive VOLTS, and save configs.

python component/compare_components.py results/design_a/component.json results/design_b/component.json
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import argparse
import json
from fmcw.config import load
from fmcw.experiments import save_csv
from fmcw.modulator import power_budget

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('components',nargs='+');p.add_argument('--config',default='config/baseline.json')
p.add_argument('--out',default='results/component_comparison')
a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);c=load(a.config)
rows=[]
for i,path in enumerate(a.components):
    d=json.loads(Path(path).read_text())
    if not d['converged']: raise SystemExit(f'Unconverged component: {path}')
    if abs(d['wavelength_m']/c.wavelength_m-1)>.001: raise SystemExit('Wavelength mismatch')
    cfg=c.updated(vpi_v=d['vpi_v'])
    cfg.save(out/f'design_{i}.json')
    rows.append(dict(name=d['name'],vpi_v=d['vpi_v'],bias_v=cfg.bias_v,drive_v=cfg.drive_v,
                     bias_over_vpi=cfg.bias_v/cfg.vpi_v,drive_over_vpi=cfg.drive_v/cfg.vpi_v,
                     **power_budget(cfg,True)))
save_csv(out/'comparison.csv',rows)
print('Saved component-specific system configs. Run fmcw mc with each config at the same ISR values.')
