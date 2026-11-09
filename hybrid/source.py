"""Local straight-section source model. Lengths in um except where marked."""
import argparse, json
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve

def bias(x,z,gap,eps_ln=(28.,43.)):
    """Unit differential bias, insulated outer walls, finite-volume flux continuity."""
    X,Z=np.meshgrid(x,z); film=(Z>=1.1)&(Z<1.4)
    pad=(Z>=1.4)&(Z<1.6)&(abs(X)>=gap/2)&(abs(X)<gap/2+1.)
    base=np.where(Z< -4,11.7,np.where(Z<1.1,3.9,1.))
    base[(abs(X)<.75)&(Z>=0)&(Z<.95)]=7.5
    ids=np.arange(X.size).reshape(X.shape); rows=[];cols=[];vals=[]
    for axis,k in [(1,eps_ln[0]),(0,eps_ln[1])]:
        eps=np.where(film,k,base)
        a,b=(ids[:,:-1],ids[:,1:]) if axis else (ids[:-1],ids[1:])
        a,b=a.ravel(),b.ravel(); e=eps.ravel()
        g=2*e[a]*e[b]/(e[a]+e[b])
        rows.extend([a,b,a,b]);cols.extend([a,b,b,a]);vals.extend([g,g,-g,-g])
    K=coo_matrix((np.concatenate(vals),(np.concatenate(rows),np.concatenate(cols))),shape=(X.size,X.size)).tocsr()
    fixed=pad.ravel(); V=np.zeros(X.size);V[fixed]=.5*np.sign(X.ravel()[fixed])
    V[~fixed]=spsolve(K[~fixed][:,~fixed],-K[~fixed][:,fixed]@V[fixed])
    V=V.reshape(X.shape); ez,ex=np.gradient(-V,z,x)
    return V,ex,ez

def run(h=.05,gap=4.,coverage=.5,out=Path('hybrid/output')):
    import tidy3d as td
    from tidy3d.plugins.mode import ModeSolver
    out.mkdir(exist_ok=True,parents=True)
    def box(c,s,n):
        return td.Structure(geometry=td.Box(center=c,size=s),medium=td.Medium(permittivity=n*n) if isinstance(n,float) else n)
    ne,no=2.138,2.211
    ln=td.AnisotropicMedium(**{k:td.Medium(permittivity=n*n) for k,n in zip(('xx','yy','zz'),(ne,no,no))})
    st=[box((0,0,-5.5),(td.inf,td.inf,3),3.48),box((0,0,-1.45),(td.inf,td.inf,5.1),1.444),box((0,0,.475),(1.5,td.inf,.95),2.),box((0,0,1.25),(td.inf,td.inf,.3),ln)]
    sim=td.Simulation(center=(0,0,-1.6),size=(10,1,9.2),structures=st,grid_spec=td.GridSpec.uniform(dl=h),run_time=1e-12)
    f0=td.C_0/1.55; freqs=f0*np.array([.999,1,1.001])
    data=ModeSolver(simulation=sim,plane=td.Box(center=sim.center,size=(10,0,9.2)),mode_spec=td.ModeSpec(num_modes=4,target_neff=1.87,num_pml=(10,10)),freqs=freqs.tolist()).solve()
    x=np.arange(-5+h/2,5,h);z=np.arange(-6.2+h/2,3,h); X,Z=np.meshgrid(x,z)
    core=(abs(X)<.75)&(Z>=0)&(Z<.95); film=(Z>=1.1)&(Z<1.4)
    def field(k,i,j):
        a=getattr(data,k).isel(f=i,mode_index=j).squeeze().interp(x=x,z=z,kwargs={'fill_value':0.}).transpose('z','x').values
        return abs(np.nan_to_num(a))**2
    js=[];ns=[]
    for i in range(3):
        scores=[]
        for j in range(4):
            I=field('Ex',i,j);scores.append(I[core].sum()/max(sum(field(k,i,j).sum() for k in ('Ex','Ey','Ez')),1e-30))
        js.append(int(np.argmax(scores)));ns.append(float(data.n_eff.isel(f=i,mode_index=js[-1])))
    ng=ns[1]+(ns[2]-ns[0])/.002
    I,J,K=[field(k,1,js[1]) for k in ('Ex','Ey','Ez')]
    bg=np.where(core,4.,np.where(Z< -4,3.48**2,np.where(Z<1.1,1.444**2,1.)))
    W=np.where(film,ne**2,bg)*I+np.where(film,no**2,bg)*(J+K)
    V,ex,ez=bias(x,z,gap)
    # Nondispersive cavity perturbation; dominant extraordinary diagonal term only.
    # r33=31 pm/V design input. 1 V/um = 1e6 V/m.
    slope=abs(.5*f0*ne**4*31e-12*1e6*np.sum((ex*I)[film])/W.sum())*coverage
    meta=dict(step_um=h,gap_um=gap,active_fraction=coverage,n_eff=ns[1],group_index=ng,mode_indices=js,ln_electric_energy_fraction=W[film].sum()/W.sum(),MHz_per_V=slope/1e6,Vpp_for_500MHz=500e6/slope,assumed_radius_um=td.C_0/(2*np.pi*ng*102e9))
    np.savez_compressed(out/'fields.npz',x=x,z=z,intensity=I,ex=ex,ez=ez,potential=V)
    (out/'source.json').write_text(json.dumps(meta,indent=2));return meta
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--step',type=float,default=.05);p.add_argument('--gap',type=float,default=4);p.add_argument('--coverage',type=float,default=.5);p.add_argument('--out',type=Path,default=Path('hybrid/output'))
    a=p.parse_args();print(run(a.step,a.gap,a.coverage,a.out))
