"""Complete filtered-field cross ambiguity against asynchronous transmitter B."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .source import target_phase
from .modulator import normalized_field
from .estimation import Estimator
from .experiments import metadata,save_csv


def run(cfg,out):
    out=metadata(out,cfg,'cross-ambiguity')
    offsets=np.linspace(0,cfg.code_length/cfg.chip_hz,41,endpoint=False)
    frequencies=np.linspace(-2e6,2e6,41)
    rows=[];fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for band,ax in zip(['full','sideband'],axes):
        # No bank construction needed for one fixed desired range.
        est=Estimator.__new__(Estimator); est.cfg=cfg;est.coded=True;est.small=False
        from .receiver import Receiver
        est.rx=Receiver(cfg,band);a=est.basis(cfg.range_m);t=est.rx.t;tau=cfg.delay(cfg.range_m)
        values=np.empty((len(frequencies),len(offsets)))
        for j,offset in enumerate(offsets):
            u=normalized_field(t-tau-offset,cfg,True,cfg.code_seed_b)
            phase=target_phase(t,tau,cfg)
            for i,f in enumerate(frequencies):
                z=u*np.exp(1j*(phase+2*np.pi*f*t))
                h=est.rx.process(np.stack([z.real,-z.imag])).T
                q,_=np.linalg.qr(h,mode='reduced')
                overlap=float(np.linalg.svd(a@q,compute_uv=False)[0])
                values[i,j]=overlap
                rows.append(dict(band=band,offset_us=offset*1e6,beat_offset_mhz=f/1e6,overlap=overlap))
        im=ax.pcolormesh(offsets*1e6,frequencies/1e6,values,shading='auto',vmin=0,vmax=1)
        ax.set(title=band,xlabel='B code offset (µs)',ylabel='B beat offset (MHz)');fig.colorbar(im,ax=ax,label='Worst-phase normalized overlap')
    save_csv(out/'cross_ambiguity.csv',rows);fig.savefig(out/'cross_ambiguity.png',dpi=180);plt.close(fig)

if __name__=='__main__':
    import argparse
    from .config import load
    from threadpoolctl import threadpool_limits
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default='config/baseline.json');p.add_argument('--out',default='results/ambiguity')
    a=p.parse_args()
    with threadpool_limits(limits=1):run(load(a.config),a.out)
