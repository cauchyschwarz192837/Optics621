"""Run from any directory. Uses ONLY supplied raw trial CSVs; no new optical runs."""
from pathlib import Path
from collections import defaultdict
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'review'/'figures'
OUT.mkdir(exist_ok=True, parents=True)
methods = ['uncoded','full_field','sideband']
labels = ['Uncoded','Coded, full band','Coded, sideband']
colors = ['#526679','#247b88','#c26124']
rows=[]
fig, ax = plt.subplots(1,2,figsize=(10.2,4.3),layout='constrained')
for panel, folder, level, title in [(0,'no_interference_validation',None,'Receiver noise only | 60 trials'),
                                    (1,'smoke_mc',10,'Foreign return | +10 dB ISR | 20 trials')]:
    d=ROOT/'results'/folder
    import json
    cfg=json.loads((d/'config.json').read_text())
    R=cfg['range_m']; tol=299792458/(4*cfg['sweep_hz'])
    data=defaultdict(list)
    with (d/'trials.csv').open() as f:
        for row in csv.DictReader(f):
            val=float(row['isr_db']) if row['isr_db'] else None
            if val==level:data[row['method']].append(row)
    for k,m in enumerate(methods):
        trials=data[m]
        err=1000*np.array([float(r['estimated_range_m'])-R for r in trials])
        detected=np.array([float(r['score'])>float(r['threshold']) for r in trials])
        local=np.abs(err)<=1000*tol; n=len(err)
        # Jitter is for visibility only; vertically paired positions have no physical meaning.
        x=k+np.random.default_rng(k+14).uniform(-.16,.16,n)
        ax[panel].scatter(x[detected],err[detected],s=15,color=colors[k],alpha=.8)
        ax[panel].scatter(x[~detected],err[~detected],s=24,marker='x',color=colors[k])
        rows.append(dict(study=folder,method=m,n=n,rmse_mm=np.sqrt(np.mean(err**2)),
                         gross_errors=sum(~local),threshold_crossings=sum(detected),
                         correct_detections=sum(local & detected),correct_detection_rate=np.mean(local & detected)))
    ax[panel].axhline(0,color='#526679',lw=.9)
    ax[panel].set(xticks=range(3),xticklabels=labels,ylabel='Estimated range minus true range (mm)',title=title)
    ax[panel].tick_params(axis='x',labelrotation=12)
    ax[panel].grid(axis='y',alpha=.2)
ax[1].axhline(450,color='#8b4a41',ls='--',lw=1,label='Foreign beat: +450 mm')
ax[1].axhline(1000*tol,color='grey',ls=':',lw=1,label='Upper gross-error boundary')
ax[1].legend(fontsize=8,loc='center right')
fig.suptitle('Correct target or foreign beat?  •  Filled: detected; ×: below threshold',fontsize=13)
for ext in ['png','pdf']: fig.savefig(OUT/f'range_evidence.{ext}',dpi=210)
with (OUT/'verified_metrics.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print(OUT)
