"""Staged reproducible experiments; all figures are regenerated from recorded outputs."""
from dataclasses import asdict
from pathlib import Path
import csv
import json
import platform
import importlib.metadata
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import periodogram
from .config import C,Q
from .modulator import power_budget, chips, voltage, transfer
from .receiver import Receiver
from .simulation import simulate
from .calibration import calibrate
from .estimation import Estimator, fft_range, fisher_bound
from .metrics import summarize, interval

METHODS = {
    'uncoded': (False,False,'full'),
    'small_signal': (True,True,'full'),
    'full_field': (True,False,'full'),
    'sideband': (True,False,'sideband'),
}


def write_json(path,data):
    Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')


def save_csv(path,rows):
    if not rows: return
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)


def metadata(out,cfg,command):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    cfg.save(out/'config.json')
    versions={}
    for name in ['numpy','scipy','matplotlib','threadpoolctl','tidy3d']:
        try: versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: pass
    write_json(out/'provenance.json',dict(command=command,python=platform.python_version(),packages=versions,
        code_a=chips(cfg.code_seed_a,cfg.code_length).astype(int).tolist(),
        code_b=chips(cfg.code_seed_b,cfg.code_length).astype(int).tolist(),
        notes=['Simulation, not experimental validation','Periodic codes with asynchronous foreign timing',
               'Coherent receiver; one real balanced output','Stationary PSD whitening approximation']))
    return out


def analytic(cfg):
    p=power_budget(cfg,False); rx=Receiver(cfg)
    psd=rx.noise_psd(p['collected_w'])
    a=2*cfg.responsivity*np.sqrt(cfg.lo_w*p['coherent_w'])
    cnr=a*a*cfg.duration_s/psd
    return dict(uncoded_budget=p,coded_budget=power_budget(cfg,True),
        round_trip_ns=cfg.delay(cfg.range_m)*1e9,beat_mhz=cfg.slope*cfg.delay(cfg.range_m)/1e6,
        resolution_m=cfg.resolution_m,samples=rx.n,receiver_enbw_hz=rx.enbw(),
        shot_density_a_rt_hz=np.sqrt(2*Q*cfg.responsivity*cfg.lo_w),
        white_noise_cnr_db=10*np.log10(cnr),
        white_noise_range_bound_m=cfg.resolution_m*np.sqrt(3)/(np.pi*np.sqrt(cnr)),
        coherence=np.exp(-np.pi*cfg.linewidth_hz*cfg.delay(cfg.range_m)),
        source_tuning_voltage_pp_v=cfg.sweep_hz/28e6)


def demo(cfg,out):
    out=metadata(out,cfg,'demo')
    template,cal=calibrate(cfg,cfg.seed+17); write_json(out/'calibration.json',cal)
    write_json(out/'analytical_baselines.json',analytic(cfg))
    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    t=np.arange(0,5e-6,1/cfg.sim_hz)
    v=voltage(t,cfg,cfg.code_seed_a)
    axes[0,0].plot(t*1e6,v,lw=1); axes[0,0].set(xlabel='Time (µs)',ylabel='Differential drive (V)')
    axes[0,1].plot(t*1e6,abs(transfer(v,cfg))**2,lw=1)
    axes[0,1].set(xlabel='Time (µs)',ylabel='MZM power transmission')
    rows=[]
    for name,(coded,small,band) in METHODS.items():
        print('Demo:',name,flush=True)
        trial=simulate(cfg,coded,cfg.seed,band=band)
        est=Estimator(template,coded,small,band)
        r,score=est.estimate(trial.processed)
        a=2*cfg.responsivity*np.sqrt(cfg.lo_w*trial.budget['coherent_w'])
        rows.append(dict(method=name,range_m=r,error_m=r-cfg.range_m,
                         fft_initializer_m=fft_range(trial.adc,template) if not coded else '',
                         score=score,approximate_local_bound_m=fisher_bound(est,cfg.range_m,a,trial.noise_psd),
                         **trial.budget))
        f,p=periodogram(trial.adc,fs=cfg.adc_hz)
        if name in ('uncoded','full_field'):
            axes[1,0].plot(f/1e6,10*np.log10(np.maximum(p,1e-35)),label=name,lw=.8)
            ambiguity=np.array([est.overlap(cfg.range_m,r) for r in np.linspace(cfg.range_m-1,cfg.range_m+1,101)])
            axes[1,1].plot(np.linspace(-1,1,101),ambiguity,label=name)
        np.savez_compressed(out/f'{name}_waveform.npz',adc=trial.adc,processed=trial.processed)
    axes[1,0].set(xlabel='Electrical frequency (MHz)',ylabel='PSD (dB A²/Hz)',xlim=(0,20)); axes[1,0].legend()
    axes[1,1].set(xlabel='Range offset (m)',ylabel='Maximum quadrature overlap',ylim=(0,1.02)); axes[1,1].legend()
    fig.savefig(out/'demo.png',dpi=180); plt.close(fig)
    save_csv(out/'estimates.csv',rows)
    return rows


def monte_carlo(cfg,out,isrs,trials=500,null_trials=1000,methods=None,scenario='overlap'):
    if trials<1 or null_trials<100: raise ValueError('Use trials>=1 and null_trials>=100; >=1000 preferred')
    out=metadata(out,cfg,f'monte-carlo scenario={scenario}')
    template,cal=calibrate(cfg,cfg.seed+17); write_json(out/'calibration.json',cal)
    methods=methods or list(METHODS)
    summaries=[]; raw=[]
    for name in methods:
        coded,small,band=METHODS[name]
        print('Building template bank:',name,flush=True)
        est=Estimator(template,coded,small,band)
        for level in isrs:
            case=cfg.updated(isr_db=level)
            # Frequency placements are explicit, not labels inferred from outcomes.
            if scenario=='overlap':
                case=case.updated(interferer_slope_ratio=1.,
                      interferer_offset_hz=cfg.slope*(cfg.interferer_delay_s-cfg.delay(cfg.range_m+.45)))
            elif scenario=='crossing':
                case=case.updated(interferer_slope_ratio=1.04,interferer_offset_hz=-10e6)
            elif scenario=='out_of_band':
                case=case.updated(interferer_slope_ratio=1.,interferer_offset_hz=55e6)
            else: raise ValueError(scenario)
            case.validate()
            print(f'{name} ISR={level}; H0 calibration/validation {null_trials} each, H1 {trials}',flush=True)
            null_scores=[]; validation=[]
            # Same seeds across methods and ISR values enable paired comparisons.
            for i in range(2*null_trials):
                tr=simulate(case,coded,cfg.seed+100000+i,target_present=False,band=band)
                _,score=est.estimate(tr.processed)
                (null_scores if i<null_trials else validation).append(score/(tr.noise_psd*cfg.adc_hz/2))
            threshold=float(np.quantile(null_scores,.99,method='higher'))
            estimates=[]; scores=[]; clips=[]
            for i in range(trials):
                tr=simulate(case,coded,cfg.seed+1000000+i,band=band)
                r,score=est.estimate(tr.processed)
                normalized=score/(tr.noise_psd*cfg.adc_hz/2)
                estimates.append(r); scores.append(normalized); clips.append(tr.clipped_fraction)
                raw.append(dict(method=name,isr_db=level,trial=i,seed=cfg.seed+1000000+i,
                    estimated_range_m=r,score=normalized,threshold=threshold,clipped_fraction=tr.clipped_fraction))
            row=dict(method=name,isr_db=level,scenario=scenario,**summarize(estimates,cfg.range_m,cfg.resolution_m,scores,threshold))
            false=int(np.sum(np.array(validation)>threshold))
            row.update(false_alarm_validation=false/null_trials,false_alarm_ci95=interval(false,null_trials),
                       null_trials=null_trials,mean_clipped_fraction=float(np.mean(clips)),**power_budget(case,coded))
            reference=row['coherent_w'] if case.foreign_reference_coherent_w is None else case.foreign_reference_coherent_w
            row['actual_isr_db']=None if level is None else float(level+10*np.log10(reference/row['coherent_w']))
            row['foreign_coherent_w']=0. if level is None else reference*10**(level/10)
            row['isr_axis']='actual received ISR' if case.foreign_reference_coherent_w is None else 'ISR relative to fixed reference power'
            summaries.append(row)
            tag='none' if level is None else str(level)
            write_json(out/f'h0_{name}_{tag}.json',dict(calibration_scores=null_scores,validation_scores=validation,threshold=threshold))
            write_json(out/'summary.json',summaries); save_csv(out/'trials.csv',raw)
            save_csv(out/'summary.csv',summaries)
    plot_summary(out,summaries)
    # Largest tested ISR passing explicit point-estimate criteria, with intervals retained.
    tolerances={}
    for name in methods:
        rows=[r for r in summaries if r['method']==name and r['isr_db'] is not None]
        passed=[r['isr_db'] for r in rows if r['rmse_m']<=.01 and r['gross_error_probability']<=.01 and r['detection_probability']>=.95]
        tolerances[name]=max(passed) if passed else None
    write_json(out/'tolerable_isr.json',dict(criteria='RMSE<=1 cm; gross error<=1%; Pd>=95%; point estimates only',largest_tested_isr_db=tolerances))
    return summaries


def plot_summary(out,rows):
    fig,axes=plt.subplots(1,3,figsize=(13,3.8),layout='constrained')
    if all(r['isr_db'] is None for r in rows):
        names=[r['method'] for r in rows]
        for ax,key,label in zip(axes,['rmse_m','gross_error_probability','detection_probability'],
                                ['Range RMSE (m)','Gross-error probability','Detection probability']):
            ax.bar(names,[r[key] for r in rows])
            ax.set(ylabel=label,title='No interference')
            ax.tick_params(axis='x',rotation=20)
        axes[1].set_ylim(0,1.02); axes[2].set_ylim(0,1.02)
        fig.savefig(Path(out)/'performance.png',dpi=180); plt.close(fig)
        return
    for name in dict.fromkeys(r['method'] for r in rows):
        subset=[r for r in rows if r['method']==name and r['isr_db'] is not None]
        if not subset: continue
        x=[r['isr_db'] for r in subset]
        axes[0].semilogy(x,[max(r['rmse_m'],1e-7) for r in subset],'o-',label=name)
        axes[1].plot(x,[r['gross_error_probability'] for r in subset],'o-',label=name)
        axes[2].plot(x,[r['detection_probability'] for r in subset],'o-',label=name)
    for ax,y in zip(axes,['Range RMSE (m)','Gross-error probability','Detection probability']):
        axis_label='Received ISR (dB)' if all(r.get('isr_axis','actual received ISR')=='actual received ISR' for r in rows) else 'ISR vs fixed reference (dB)'
        ax.set(xlabel=axis_label,ylabel=y); ax.grid(alpha=.25)
    axes[0].legend(fontsize=8); axes[1].set_ylim(-.02,1.02); axes[2].set_ylim(-.02,1.02)
    fig.savefig(Path(out)/'performance.png',dpi=180); plt.close(fig)


def convergence(cfg,out):
    out=metadata(out,cfg,'convergence')
    rows=[]
    # Compare noiseless sampled waveforms; random optical phase is fixed independently.
    from .source import target_phase
    from .modulator import normalized_field
    baseline=None
    for os in [16,8,4]:
        c=cfg.updated(oversample=os,noise=False,linewidth_hz=0,interferer_linewidth_hz=0)
        rx=Receiver(c); tau=c.delay(c.range_m)
        z=normalized_field(rx.t-tau,c)*np.exp(1j*target_phase(rx.t,tau,c))
        y=rx.sample(z.real)
        if baseline is None: baseline=y
        rows.append(dict(oversample=os,relative_waveform_error_to_16x=float(np.linalg.norm(y-baseline)/np.linalg.norm(baseline)),enbw_hz=rx.enbw()))
    save_csv(out/'convergence.csv',rows)
    return rows


def tradeoff(cfg,out):
    out=metadata(out,cfg,'bias-drive')
    rows=[]
    for bias in [.4,.5,.6]:
        for drive in [.1,.3,.6]:
            c=cfg.updated(bias_v=bias*cfg.vpi_v,drive_v=drive*cfg.vpi_v)
            p=power_budget(c,True)
            rx=Receiver(c,'sideband'); full=Receiver(c)
            from .modulator import normalized_field
            from .source import target_phase
            z=normalized_field(rx.t-c.delay(c.range_m),c)*np.exp(1j*target_phase(rx.t,c.delay(c.range_m),c))
            # Quadrature-averaged band energy; no unknown target-phase preference.
            q=np.stack([z.real,z.imag]); total=np.sum(full.process(q)**2); kept=np.sum(rx.process(q)**2)
            rows.append(dict(bias_over_vpi=bias,drive_over_vpi=drive,sideband_fraction_of_processed_energy=float(kept/total),**p))
    save_csv(out/'bias_drive.csv',rows)
    fig,ax=plt.subplots(figsize=(6,4),layout='constrained')
    for b in [.4,.5,.6]:
        subset=[r for r in rows if r['bias_over_vpi']==b]
        ax.plot([r['drive_over_vpi'] for r in subset],[r['sideband_fraction_of_processed_energy'] for r in subset],'o-',label=f'Bias {b} Vπ')
    ax.set(xlabel='RF drive / Vπ',ylabel='Retained sideband energy fraction'); ax.legend()
    fig.savefig(out/'bias_drive.png',dpi=180); plt.close(fig)
    return rows
