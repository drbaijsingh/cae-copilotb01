import numpy as np

def Qmat(E1,E2,G12,nu12):
    nu21=nu12*E2/E1; d=1-nu12*nu21
    return np.array([[E1/d, nu12*E2/d, 0],[nu12*E2/d, E2/d, 0],[0,0,G12]])

def Qbar(Q,th):
    c=np.cos(np.radians(th)); s=np.sin(np.radians(th))
    Q11,Q12,Q22,Q66=Q[0,0],Q[0,1],Q[1,1],Q[2,2]
    return np.array([
      [Q11*c**4+2*(Q12+2*Q66)*s*s*c*c+Q22*s**4,
       (Q11+Q22-4*Q66)*s*s*c*c+Q12*(c**4+s**4),
       (Q11-Q12-2*Q66)*c**3*s-(Q22-Q12-2*Q66)*c*s**3],
      [0,
       Q11*s**4+2*(Q12+2*Q66)*s*s*c*c+Q22*c**4,
       (Q11-Q12-2*Q66)*c*s**3-(Q22-Q12-2*Q66)*c**3*s],
      [0,0,(Q11+Q22-2*Q12-2*Q66)*s*s*c*c+Q66*(c**4+s**4)]])

def ABD(plies):
    tot=sum(p[1] for p in plies)
    z=[-tot/2]
    for p in plies: z.append(z[-1]+p[1])
    z=np.array(z)
    A=np.zeros((3,3)); B=np.zeros((3,3)); D=np.zeros((3,3))
    for k,(Q,t,th) in enumerate([(Qbar(p[0],p[2]),p[1],p[2]) for p in plies]):
        Qb=Q; Qb[1,0]=Qb[0,1]; Qb[2,0]=Qb[0,2]; Qb[2,1]=Qb[1,2]
        A+=Qb*(z[k+1]-z[k]); B+=Qb*(z[k+1]**2-z[k]**2)/2; D+=Qb*(z[k+1]**3-z[k]**3)/3
    return A,B,D,tot

print('=== Check 1: single isotropic ply must reproduce plate constants ===')
E,nu,h=210e9,0.3,0.005
Q=Qmat(E,E,E/(2*(1+nu)),nu)
A,B,D,tot=ABD([(Q,h,0.0)])
print(f'  A11 = {A[0,0]:.6e}  ref Eh/(1-v^2) = {E*h/(1-nu**2):.6e}')
print(f'  D11 = {D[0,0]:.6e}  ref Eh^3/12(1-v^2) = {E*h**3/(12*(1-nu**2)):.6e}')
print(f'  |B|max = {np.abs(B).max():.3e} (must be 0)')

print()
print('=== Check 2: symmetric cross-ply [0/90]s -> B=0, D16=D26=0 ===')
E1,E2,G12,nu12=138e9,8.96e9,7.1e9,0.30
Qc=Qmat(E1,E2,G12,nu12); tp=0.000125
lam=[(Qc,tp,a) for a in [0,90,90,0]]
A,B,D,tot=ABD(lam)
print(f'  |B|max = {np.abs(B).max():.3e}   D16 = {D[0,2]:.3e}   D26 = {D[1,2]:.3e}')

print()
print('=== Check 3: antisymmetric [0/90] -> B nonzero (coupling) ===')
A2,B2,D2,_=ABD([(Qc,tp,0),(Qc,tp,90)])
print(f'  |B|max = {np.abs(B2).max():.4e} (must be nonzero)')

print()
print('=== Check 4: isotropic plate frequency via laminate route ===')
a=b=1.0; rho=7850
A,B,D,tot=ABD([(Qmat(E,E,E/(2*(1+nu)),nu),0.005,0.0)])
m=n=1
w=np.pi**2*np.sqrt((D[0,0]*(m/a)**4+2*(D[0,1]+2*D[2,2])*(m/a)**2*(n/b)**2+D[1,1]*(n/b)**4)/(rho*0.005))
lam_=w*a**2*np.sqrt(rho*0.005/(E*0.005**3/(12*(1-nu**2))))
print(f'  f1 = {w/(2*np.pi):.4f} Hz     lambda = {lam_:.4f}  (ref 19.739)')

print()
print('=== Check 5: sandwich shear correction ===')
Ef,nuf,tf,rhof = 70e9,0.33,0.0005,2700
Ec_,nuc_,tc,rhoc_,Gc = 0.2e9,0.3,0.02,60,0.05e9
h_=tc+2*tf; d=tc+tf
Dsw=Ef*(h_**3-tc**3)/(12*(1-nuf**2))+Ec_*tc**3/(12*(1-nuc_**2))
S=Gc*d**2/tc
rhoA=2*rhof*tf+rhoc_*tc
k2=np.pi**2*((1/a)**2+(1/b)**2)
w_b=np.sqrt(Dsw*k2**2/rhoA)
w_s=np.sqrt(Dsw*k2**2/(rhoA*(1+Dsw*k2/S)))
print(f'  D = {Dsw:.4e} N.m   S = {S:.4e} N/m   mass/area = {rhoA:.3f} kg/m2')
print(f'  bending-only f = {w_b/(2*np.pi):9.3f} Hz')
print(f'  shear-corrected f = {w_s/(2*np.pi):7.3f} Hz   ({100*(1-w_s/w_b):.1f}% lower)')
print('  Shear MUST reduce the frequency. Ignoring it is the classic sandwich error.')

sig_wr=0.5*(Ef*Ec_*Gc)**(1/3)
print(f'  face wrinkling stress = {sig_wr/1e6:.1f} MPa')
