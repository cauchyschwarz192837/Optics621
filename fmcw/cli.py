"""All commands operate locally; no Tidy3D cloud jobs are submitted."""
import argparse
import json
from pathlib import Path
from threadpoolctl import threadpool_limits
from .config import load
from .experiments import demo,monte_carlo,convergence,tradeoff,analytic


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['baseline','demo','mc','convergence','tradeoff'])
    p.add_argument('--config',default=None)
    p.add_argument('--out',default='results/run')
    p.add_argument('--component',help='Exported component JSON; changes Vpi, retains drive VOLTS')
    p.add_argument('--trials',type=int,default=500)
    p.add_argument('--null-trials',type=int,default=1000)
    p.add_argument('--isr',default='none,-20,-10,0,10,20,30')
    p.add_argument('--scenario',choices=['overlap','crossing','out_of_band'],default='overlap')
    p.add_argument('--methods',default='uncoded,small_signal,full_field,sideband')
    args=p.parse_args(); cfg=load(args.config)
    if args.component:
        d=json.loads(Path(args.component).read_text())
        if abs(d['wavelength_m']/cfg.wavelength_m-1)>.001: p.error('Component wavelength mismatch')
        if not d.get('converged',False): p.error('Component export is not converged; inspect convergence.csv')
        cfg=cfg.updated(vpi_v=d['vpi_v']).validate()
    with threadpool_limits(limits=1):
        if args.command=='baseline': print(json.dumps(analytic(cfg),indent=2))
        elif args.command=='demo': demo(cfg,args.out)
        elif args.command=='convergence': convergence(cfg,args.out)
        elif args.command=='tradeoff': tradeoff(cfg,args.out)
        else:
            isrs=[None if x.strip().lower()=='none' else float(x) for x in args.isr.split(',')]
            monte_carlo(cfg,args.out,isrs,args.trials,args.null_trials,args.methods.split(','),args.scenario)

if __name__=='__main__': main()
