"""Regenerate publication figures and summary data from stored numerical fields and trials."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from .source import bias
p=Path('hybrid/output')
def main():
    d=np.load(p/'fields.npz'); x,z,I,ex=[d[k] for k in ['x','z','intensity','ex']]
    s=json.loads((p/'source.json').read_text())
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titlelocation':'left'})
    fig,ax=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
    for a,U,cmap in zip(ax[:2],[I/I.max(),abs(ex)],['magma','viridis']):
        im=a.pcolormesh(x,z,U,cmap=cmap,shading='auto',rasterized=True,vmin=0,vmax=1 if a==ax[0] else .35)
        a.set(xlim=(-3.3,3.3),ylim=(-.45,2.2),aspect='equal',xlabel='Lateral position (µm)',ylabel='Height (µm)')
        a.add_patch(Rectangle((-.75,0),1.5,.95,fill=False,ec='white',lw=1))
        for zz in (1.1,1.4):a.axhline(zz,c='white',lw=.7)
        for xx in (-3,2):a.add_patch(Rectangle((xx,1.4),1,.2,color='#a6a8aa'))
        fig.colorbar(im,ax=a,orientation='horizontal',shrink=.84,label='Normalised |Eₓ|²' if a==ax[0] else 'Lateral bias field magnitude (V/µm per V), gap region')
    ax[0].set_title('a   Guided optical mode');ax[1].set_title('b   Electrode bias field')
    X,Z=np.meshgrid(x,z);film=(Z>=1.1)&(Z<1.4)
    gaps=[3,4,5,6];slopes=[]
    for gap in gaps:
        _,eg,_=bias(x,z,gap)
        slopes.append(s['MHz_per_V']*np.sum((eg*I)[film])/np.sum((ex*I)[film]))
    with (p/'geometry.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['gap_um','MHz_per_V_half_active']);w.writerows(zip(gaps,slopes))
    a=ax[2];a.plot(gaps,slopes,'o-',c='#136b74',label='Model, half active');a.axhline(28,ls=':',c='#a44b28',label='Published laser benchmark')
    a.set(xlabel='Assumed electrode gap (µm)',ylabel='Tuning magnitude (MHz/V)',ylim=(0,max(slopes)*1.14));a.set_title('c   Geometry sensitivity');a.legend(frameon=False,fontsize=8)
    for ext in ['png','pdf']:fig.savefig(p/f'source_fields.{ext}',dpi=200)
    plt.close(fig)
    rows=list(csv.DictReader((p/'paired.csv').open()));fig,axs=plt.subplots(1,2,figsize=(8.4,3.1),layout='constrained',sharey=True);summary=[]
    for a,level,title in zip(axs,['','10.0'],['a   No foreign transmitter','b   Foreign return +10 dB']):
        for m,col in zip(['uncoded','matched','wrong code'],['#464e70','#087b72','#bd612d']):
            vals=sorted(abs(float(r['range_m'])-50)*1000 for r in rows if r['method']==m and r['ISR_dB']==level)
            a.step(vals,np.arange(1,len(vals)+1)/len(vals),where='post',label=m,c=col,lw=2)
            summary.append(dict(method=m,ISR=level or 'absent',n=len(vals),rmse_mm=np.sqrt(np.mean(np.square(vals))),median_abs_mm=np.median(vals),within_half_cell=sum(np.array(vals)<299792458/(2*s['MHz_per_V']*5e6)*500)))
        a.set(xscale='log',xlabel='Absolute range error (mm)',title=title);a.grid(alpha=.18);a.legend(frameon=False,fontsize=8)
    axs[0].set_ylabel('Fraction of trials');plt.savefig(p/'range_control.png',dpi=210);plt.savefig(p/'range_control.pdf')
    with (p/'summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
if __name__=='__main__': main()
