import numpy as np

# ---------------- FGM ----------------
def mori_tanaka(Ec,nuc,Em,num,Vc):
    Kc=Ec/(3*(1-2*nuc)); Gc=Ec/(2*(1+nuc))
    Km=Em/(3*(1-2*num)); Gm=Em/(2*(1+num))
    fm=Gm*(9*Km+8*Gm)/(6*(Km+2*Gm))
    K=Km+(Kc-Km)*Vc/(1+(1-Vc)*(Kc-Km)/(Km+4/3*Gm))
    G=Gm+(Gc-Gm)*Vc/(1+(1-Vc)*(Gc-Gm)/(Gm+fm))
    E=9*K*G/(3*K+G); nu=(3*K-2*G)/(2*(3*K+G))
    return E,nu

def voigt(Ec,nuc,Em,num,Vc):
    return Ec*Vc+Em*(1-Vc), nuc*Vc+num*(1-Vc)

def reuss(Ec,nuc,Em,num,Vc):
    E=1.0/(Vc/Ec+(1-Vc)/Em)
    return E, nuc*Vc+num*(1-Vc)

def fgm_props(h,n,Ec,nuc,rhoc,Em,num,rhom,scheme='mt',law='power',N=400):
    z=np.linspace(-h/2,h/2,N)
    t=(z+h/2)/h
    if law=='power': Vc=t**n
    elif law=='exp':  Vc=None
    elif law=='sigmoid':
        Vc=np.where(t<=0.5, 0.5*(2*t)**n, 1-0.5*(2*(1-t))**n)
    if law=='exp':
        E=Em*np.exp(np.log(Ec/Em)*t); nu=np.full_like(z,num); rho=rhom*np.exp(np.log(rhoc/rhom)*t)
    else:
        f={'mt':mori_tanaka,'voigt':voigt,'reuss':reuss}[scheme]
        E,nu=f(Ec,nuc,Em,num,Vc)
        rho=rhoc*Vc+rhom*(1-Vc)
    return z,E,nu,rho

def fgm_stiffness(h,n,Ec,nuc,rhoc,Em,num,rhom,scheme='mt',law='power',N=2001):
    z,E,nu,rho=fgm_props(h,n,Ec,nuc,rhoc,Em,num,rhom,scheme,law,N)
    Eb=E/(1-nu**2)
    A=np.trapezoid(Eb,z)
    zns=np.trapezoid(Eb*z,z)/A
    D=np.trapezoid(Eb*(z-zns)**2,z)
    I0=np.trapezoid(rho,z)
    return A,D,zns,I0

Al=(70e9,0.30,2702.0); Alu=(380e9,0.30,3800.0)
h=0.01
print('=== FGM limiting cases (Al / Al2O3, h=10mm) ===')
for n,lbl in [(0.0,'n=0 (all ceramic)'),(1e6,'n->inf (all metal)')]:
    A,D,zns,I0=fgm_stiffness(h,n,Alu[0],Alu[1],Alu[2],Al[0],Al[1],Al[2])
    Eref,nuref,rhoref=(Alu if n==0 else Al)
    Dref=Eref*h**3/(12*(1-nuref**2)); I0ref=rhoref*h
    print(f'  {lbl:20} D={D:12.4e} ref={Dref:12.4e} err={100*(D-Dref)/Dref:+7.3f}%  zns={zns:+.3e}  I0 err={100*(I0-I0ref)/I0ref:+.3f}%')

print()
print('=== Neutral surface shift vs power index (Mori-Tanaka) ===')
for n in [0.2,0.5,1,2,5,10]:
    A,D,zns,I0=fgm_stiffness(h,n,Alu[0],Alu[1],Alu[2],Al[0],Al[1],Al[2])
    print(f'  n={n:<5} zns/h = {zns/h:+.5f}')

print()
print('=== Homogenization scheme spread, n=1, Vc=0.5 point value ===')
for s in ['voigt','mt','reuss']:
    E,nu=({'voigt':voigt,'mt':mori_tanaka,'reuss':reuss}[s])(380e9,0.3,70e9,0.3,0.5)
    print(f'  {s:6} E(Vc=0.5) = {E/1e9:7.2f} GPa')
print('  (Voigt is the upper bound, Reuss the lower; Mori-Tanaka must sit between.)')
