"""Local optical mode solve with a declared UNIFORM electrostatic-field approximation.

Usage from repository root:
  python component/solve_component.py --design component/design_a.json --out results/design_a

No web.run(), no FDTD propagation over metres, no RF plugin, no paid cloud submission.
The geometry is a simplified rectangular ridge, NOT a reproduction of a published chip.
All optical dimensions passed to Tidy3D are micrometres; EO perturbations use SI units.
"""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def make_solver(d, voltage, mesh, extra=0):
    import tidy3d as td
    from tidy3d.plugins.mode import ModeSolver
    # Laboratory y: propagation; x: crystal Z (optic axis); z: crystal X (film normal).
    # E_RF along crystal Z. Only r13 and r33 enter the diagonal impermeability here.
    # d(1/n_i^2) = r_i3 E3; E_RF = V/gap. V is per-arm applied voltage in this solve.
    e=voltage/(d['gap_um']*1e-6)
    eps_e=1/(1/d['n_e']**2+d['r33_pm_v']*1e-12*e)
    eps_o=1/(1/d['n_o']**2+d['r13_pm_v']*1e-12*e)
    ln=td.AnisotropicMedium(xx=td.Medium(permittivity=eps_e),
                           yy=td.Medium(permittivity=eps_o),zz=td.Medium(permittivity=eps_o))
    # Same silica below/above. Metal loss and nonuniform RF fields are NOT modeled.
    structures=[
      td.Structure(geometry=td.Box(center=(0,0,d['slab_um']/2),size=(td.inf,td.inf,d['slab_um'])),medium=ln),
      td.Structure(geometry=td.Box(center=(0,0,(d['film_um']+d['slab_um'])/2),
                   size=(d['width_um'],td.inf,d['film_um']-d['slab_um'])),medium=ln)]
    size=(d['domain_x_um']+extra,1.,d['domain_z_um']+extra)
    center=(0,0,d['film_um']/2)
    sim=td.Simulation(center=center,size=size,medium=td.Medium(permittivity=d['n_clad']**2),
        structures=structures,grid_spec=td.GridSpec.uniform(dl=mesh),
        boundary_spec=td.BoundarySpec.all_sides(boundary=td.Periodic()),run_time=1e-12)
    return ModeSolver(simulation=sim,plane=td.Box(center=center,size=(size[0],0,size[2])),
        mode_spec=td.ModeSpec(num_modes=4,target_neff=1.9,num_pml=(12,12)),freqs=[td.C_0/d['wavelength_um']])


def field_vector(data,index):
    arrays=[np.asarray(getattr(data,k).isel(f=0,mode_index=index)).ravel() for k in ['Ex','Ey','Ez']]
    return np.concatenate(arrays)


def choose_mode(data,reference=None):
    neff=np.asarray(data.n_eff.isel(f=0)).real.ravel()
    vectors=[field_vector(data,j) for j in range(len(neff))]
    if reference is not None:
        overlap=[abs(np.vdot(reference,v))/(np.linalg.norm(reference)*np.linalg.norm(v)) for v in vectors]
        j=int(np.argmax(overlap))
        if overlap[j]<.9: raise RuntimeError('Mode identity changed across voltage: inspect fields')
        return j,float(overlap[j])
    # Fundamental x-polarized candidate: select highest neff among x-dominant modes.
    fractions=[]
    for j,v in enumerate(vectors):
        ex=np.asarray(data.Ex.isel(f=0,mode_index=j))
        fractions.append(float(np.sum(abs(ex)**2)/np.sum(abs(v)**2)))
    choices=[j for j in range(len(neff)) if fractions[j]>.5]
    if not choices: raise RuntimeError('No x-dominant TE-like mode; inspect cross-section and mode count')
    j=max(choices,key=lambda j:neff[j])
    return j,fractions[j]


def solve_triplet(d,mesh,extra,out,label):
    step=d['voltage_step_v']
    data0=make_solver(d,0,mesh,extra).solve()
    j,pol=choose_mode(data0)
    ref=field_vector(data0,j)
    neff=[float(np.asarray(data0.n_eff.isel(f=0,mode_index=j)).real)]
    overlaps=[]
    for voltage in [-step,step]:
        data=make_solver(d,voltage,mesh,extra).solve()
        k,overlap=choose_mode(data,ref); overlaps.append(overlap)
        neff.append(float(np.asarray(data.n_eff.isel(f=0,mode_index=k)).real))
    derivative=(neff[2]-neff[1])/(2*step)
    # Differential drive convention: arm voltages +V/2, -V/2. Consequently
    # d(phi1-phi2)/dV = (2*pi*L/lambda)*(dn_eff/dV_arm), not twice this value.
    wavelength=d['wavelength_um']*1e-6
    vpi=wavelength/(2*d['length_m']*abs(derivative))
    row=dict(mesh_um=mesh,domain_expansion_um=extra,neff=neff[0],
        dneff_dv=derivative,vpi_v=vpi,vpi_l_v_m=vpi*d['length_m'],
        x_field_fraction=pol,voltage_mode_overlap=min(overlaps),mode_index=j)
    data0.to_file(str(out/f'{label}_zero_voltage.hdf5'))
    # Plot one dominant field component; units follow solver normalization.
    ex=data0.Ex.isel(f=0,mode_index=j).squeeze(drop=True)
    fig,ax=plt.subplots(figsize=(6,4),layout='constrained')
    (abs(ex)**2).transpose('z','x').plot(ax=ax)
    ax.set(title=f'{label}: |Ex|², neff={neff[0]:.6f}',xlabel='x (µm)',ylabel='z (µm)')
    fig.savefig(out/f'{label}_mode.png',dpi=170); plt.close(fig)
    return row


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--design',required=True); p.add_argument('--out',required=True)
    args=p.parse_args(); d=json.loads(Path(args.design).read_text())
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    try: import tidy3d as td
    except ImportError as exc: raise SystemExit('Install optional dependencies: python -m pip install -e ".[component]"') from exc
    rows=[]
    for i,mesh in enumerate(d['meshes_um']):
        rows.append(solve_triplet(d,mesh,0,out,f'mesh_{i}'))
    rows.append(solve_triplet(d,d['meshes_um'][-1],d['domain_expansion_um'],out,'expanded'))
    # Halve voltage step to check that extracted derivative is local and stable.
    half=dict(d,voltage_step_v=d['voltage_step_v']/2)
    rows.append(solve_triplet(half,d['meshes_um'][-1],d['domain_expansion_um'],out,'half_voltage'))
    with (out/'convergence.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    v=[r['vpi_v'] for r in rows]
    changes=[abs(v[-3]/v[-4]-1),abs(v[-2]/v[-3]-1),abs(v[-1]/v[-2]-1)]
    converged=all(x<d['relative_vpi_tolerance'] for x in changes)
    result=dict(name=d['name'],wavelength_m=d['wavelength_um']*1e-6,vpi_v=v[-1],
        vpi_l_v_m=v[-1]*d['length_m'],dneff_dv=rows[-1]['dneff_dv'],
        converged=converged,relative_changes=changes,tidy3d_version=td.__version__,geometry=d,
        voltage_convention='Differential voltage: arm 1 +V/2, arm 2 -V/2',
        assumptions=['Uniform RF field V_arm/gap, not electrostatic electrode solution',
          'Crystal Z along lab x; propagation lab y; crystal X normal to film lab z',
          'Rectangular LN ridge/slab in silica; no metal or fabrication loss',
          'n_o, n_e, r13, r33 are assumed constants; no dispersion or group-index extraction',
          'Insertion loss remains an independent system assumption',
          'Local mode solver; convergence of numerical Vpi is not validation of RF approximation'])
    (out/'component.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    if not converged: raise SystemExit('Convergence failed: refine meshes/domain; export marked unusable')

if __name__=='__main__': main()
