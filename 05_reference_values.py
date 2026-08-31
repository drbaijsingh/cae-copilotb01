import numpy as np, json
def mt(Ec,nuc,Em,num,Vc):
    Kc=Ec/(3*(1-2*nuc)); Gc=Ec/(2*(1+nuc))
    Km=Em/(3*(1-2*num)); Gm=Em/(2*(1+num))
    fm=Gm*(9*Km+8*Gm)/(6*(Km+2*Gm))
    K=Km+(Kc-Km)*Vc/(1+(1-Vc)*(Kc-Km)/(Km+4/3*Gm))
    G=Gm+(Gc-Gm)*Vc/(1+(1-Vc)*(Gc-Gm)/(Gm+fm))
    return 9*K*G/(3*K+G),(3*K-2*G)/(2*(3*K+G))
# FGM default: Al2O3 top / Al bottom, power n=1, MT, h=10mm, a=b=1
N=801; h=0.01
t=np.linspace(0,1,N); z=(t-0.5)*h
Vc=t**1.0
E,nu=mt(380e9,0.30,70e9,0.30,Vc)
rho=3800*Vc+2702*(1-Vc)
Eb=E/(1-nu**2)
A=np.trapezoid(Eb,z); zns=np.trapezoid(Eb*z,z)/A
D=np.trapezoid(Eb*(z-zns)**2,z); I0=np.trapezoid(rho,z)
k=np.pi**2*(1+1); f=k*np.sqrt(D/I0)/(2*np.pi)
print(json.dumps({"zns_h":zns/h,"D":D,"I0":I0,"f11":f},indent=None))

# Laminate default: [0/45/-45/90]s AS4, tply 0.125mm
def Q(E1,E2,G,nu12):
    nu21=nu12*E2/E1; d=1-nu12*nu21
    return np.array([[E1/d,nu12*E2/d,0],[nu12*E2/d,E2/d,0],[0,0,G]])
def Qb(q,th):
    c=np.cos(np.radians(th)); s=np.sin(np.radians(th))
    Q11,Q12,Q22,Q66=q[0,0],q[0,1],q[1,1],q[2,2]
    M=np.zeros((3,3))
    M[0,0]=Q11*c**4+2*(Q12+2*Q66)*s*s*c*c+Q22*s**4
    M[0,1]=M[1,0]=(Q11+Q22-4*Q66)*s*s*c*c+Q12*(c**4+s**4)
    M[1,1]=Q11*s**4+2*(Q12+2*Q66)*s*s*c*c+Q22*c**4
    M[0,2]=M[2,0]=(Q11-Q12-2*Q66)*c**3*s-(Q22-Q12-2*Q66)*c*s**3
    M[1,2]=M[2,1]=(Q11-Q12-2*Q66)*c*s**3-(Q22-Q12-2*Q66)*c**3*s
    M[2,2]=(Q11+Q22-2*Q12-2*Q66)*s*s*c*c+Q66*(c**4+s**4)
    return M
ang=[0,45,-45,90]; ang=ang+ang[::-1]
tp=0.000125; q=Q(138e9,8.96e9,7.1e9,0.30)
tot=len(ang)*tp; zk=-tot/2
A2=np.zeros((3,3)); B2=np.zeros((3,3)); D2=np.zeros((3,3))
for a_ in ang:
    z0=zk; z1=zk+tp; zk=z1; M=Qb(q,a_)
    A2+=M*(z1-z0); B2+=M*(z1**2-z0**2)/2; D2+=M*(z1**3-z0**3)/3
rhoA=1600*tot
f11=np.pi**2*np.sqrt((D2[0,0]+2*(D2[0,1]+2*D2[2,2])+D2[1,1])/rhoA)/(2*np.pi)
print(json.dumps({"h_mm":tot*1000,"D11":D2[0,0],"D12":D2[0,1],"D66":D2[2,2],
                  "maxB":float(np.abs(B2).max()),"D16":D2[0,2],"f11":f11}))

# Sandwich default
Ef=70e9;nuf=0.33;tf=0.0005;rhof=2700; Ec=200e6;Gc=50e6;tc=0.020;rhoc=60
h2=tc+2*tf; d=tc+tf
D3=Ef*(h2**3-tc**3)/(12*(1-nuf**2))+Ec*tc**3/(12*(1-0.09))
S=Gc*d*d/tc; rA=2*rhof*tf+rhoc*tc
k2=np.pi**2*(1/1**2+1/0.6**2)
fb=np.sqrt(D3*k2**2/rA)/(2*np.pi); fs=np.sqrt(D3*k2**2/(rA*(1+D3*k2/S)))/(2*np.pi)
print(json.dumps({"D":D3,"S":S,"fb":fb,"fs":fs,"ratio":D3*k2/S}))
