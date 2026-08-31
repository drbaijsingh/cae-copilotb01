import numpy as np
from numpy.polynomial.legendre import leggauss

# Characteristic beam functions as admissible Ritz functions.
ROOT_CC = [4.730040745, 7.853204624, 10.995607838, 14.137165491, 17.278759657]
ROOT_CF = [1.875104069, 4.694091133,  7.854757438, 10.995540734, 14.137168391]

def beam(bc, m, L, x):
    """Return X, X', X'' for admissible function m (1-based) of `bc` beam."""
    if bc == 'S':
        k = m*np.pi/L
        return np.sin(k*x), k*np.cos(k*x), -k*k*np.sin(k*x)
    if bc == 'C':
        kL = ROOT_CC[m-1]; k = kL/L
        s = (np.cosh(kL)-np.cos(kL))/(np.sinh(kL)-np.sin(kL))
        X   = np.cosh(k*x)-np.cos(k*x) - s*(np.sinh(k*x)-np.sin(k*x))
        X1  = k*(np.sinh(k*x)+np.sin(k*x) - s*(np.cosh(k*x)-np.cos(k*x)))
        X2  = k*k*(np.cosh(k*x)+np.cos(k*x) - s*(np.sinh(k*x)+np.sin(k*x)))
        return X, X1, X2
    if bc == 'CF':
        kL = ROOT_CF[m-1]; k = kL/L
        s = (np.cosh(kL)+np.cos(kL))/(np.sinh(kL)+np.sin(kL))
        X   = np.cosh(k*x)-np.cos(k*x) - s*(np.sinh(k*x)-np.sin(k*x))
        X1  = k*(np.sinh(k*x)+np.sin(k*x) - s*(np.cosh(k*x)-np.cos(k*x)))
        X2  = k*k*(np.cosh(k*x)+np.cos(k*x) - s*(np.sinh(k*x)+np.sin(k*x)))
        return X, X1, X2
    if bc == 'FF':
        if m == 1: return np.ones_like(x), np.zeros_like(x), np.zeros_like(x)
        if m == 2: return (1-2*x/L)*np.sqrt(3.0), np.full_like(x,-2*np.sqrt(3.0)/L), np.zeros_like(x)
        kL = ROOT_CC[m-3]; k = kL/L
        s = (np.cosh(kL)-np.cos(kL))/(np.sinh(kL)-np.sin(kL))
        X   = np.cosh(k*x)+np.cos(k*x) - s*(np.sinh(k*x)+np.sin(k*x))
        X1  = k*(np.sinh(k*x)-np.sin(k*x) - s*(np.cosh(k*x)+np.cos(k*x)))
        X2  = k*k*(np.cosh(k*x)-np.cos(k*x) - s*(np.sinh(k*x)-np.sin(k*x)))
        return X, X1, X2
    raise ValueError(bc)

def edge_pair_to_beam(e0, e1):
    """Map the two opposite edge conditions onto a beam family."""
    p = e0+e1
    if p == 'SS': return 'S'
    if p == 'CC': return 'C'
    if p in ('CF','FC'): return 'CF'
    if p == 'FF': return 'FF'
    if p in ('SC','CS'): return 'SC'
    if p in ('SF','FS'): return 'SF'
    raise ValueError(p)

ROOT_SC = [3.926602312, 7.068582746, 10.210176122, 13.351768777, 16.493361431]
ROOT_SF = [3.926602312, 7.068582746, 10.210176122, 13.351768777, 16.493361431]

def beam2(fam, m, L, x):
    if fam in ('S','C','CF','FF'): return beam(fam, m, L, x)
    if fam == 'SC':   # pinned at x=0, clamped at x=L
        kL = ROOT_SC[m-1]; k = kL/L
        s = np.sin(kL)/np.sinh(kL)
        X  = np.sin(k*x) - s*np.sinh(k*x)
        X1 = k*(np.cos(k*x) - s*np.cosh(k*x))
        X2 = k*k*(-np.sin(k*x) - s*np.sinh(k*x))
        return X, X1, X2
    if fam == 'SF':   # pinned at x=0, free at x=L
        # m = 1 is the rigid-body ROTATION about the pinned edge. Omitting it
        # is why a naive pinned-free basis overpredicts SSSF by >100%.
        if m == 1:
            return np.sqrt(3.0)*x/L, np.full_like(x, np.sqrt(3.0)/L), np.zeros_like(x)
        kL = ROOT_SF[m-2]; k = kL/L
        s = np.sin(kL)/np.sinh(kL)
        X  = np.sin(k*x) + s*np.sinh(k*x)
        X1 = k*(np.cos(k*x) + s*np.cosh(k*x))
        X2 = k*k*(-np.sin(k*x) + s*np.sinh(k*x))
        return X, X1, X2

def ritz(D, I0, a, b, nu, ex0, ex1, ey0, ey1, NT=5, NQ=140):
    famx = edge_pair_to_beam(ex0, ex1)
    famy = edge_pair_to_beam(ey0, ey1)
    gx, wx = leggauss(NQ); x = 0.5*a*(gx+1); wxs = 0.5*a*wx
    gy, wy = leggauss(NQ); y = 0.5*b*(gy+1); wys = 0.5*b*wy
    X=[];X1=[];X2=[]
    for m in range(1, NT+1):
        f = beam2(famx, m, a, x); X.append(f[0]); X1.append(f[1]); X2.append(f[2])
    Y=[];Y1=[];Y2=[]
    for n in range(1, NT+1):
        f = beam2(famy, n, b, y); Y.append(f[0]); Y1.append(f[1]); Y2.append(f[2])
    def IX(p,q,i,j):
        A=[X,X1,X2][p][i]; B=[X,X1,X2][q][j]; return np.sum(wxs*A*B)
    def IY(p,q,i,j):
        A=[Y,Y1,Y2][p][i]; B=[Y,Y1,Y2][q][j]; return np.sum(wys*A*B)
    N=NT*NT; K=np.zeros((N,N)); M=np.zeros((N,N))
    idx=[(i,j) for i in range(NT) for j in range(NT)]
    for r,(i,j) in enumerate(idx):
        for c,(k,l) in enumerate(idx):
            K[r,c]=D*( IX(2,2,i,k)*IY(0,0,j,l) + IX(0,0,i,k)*IY(2,2,j,l)
                     + nu*(IX(2,0,i,k)*IY(0,2,j,l) + IX(0,2,i,k)*IY(2,0,j,l))
                     + 2*(1-nu)*IX(1,1,i,k)*IY(1,1,j,l) )
            M[r,c]=I0*IX(0,0,i,k)*IY(0,0,j,l)
    K=0.5*(K+K.T); M=0.5*(M+M.T)
    ev=np.linalg.eigvals(np.linalg.solve(M,K))
    ev=np.sort(np.real(ev[np.abs(np.imag(ev))<1e-6*np.abs(np.real(ev))+1e-12]))
    ev=ev[ev>1e-6]
    return np.sqrt(ev)

E,nu,h,rho,a,b = 210e9,0.3,0.005,7850.0,1.0,1.0
D=E*h**3/(12*(1-nu**2)); I0=rho*h; sc=a*a*np.sqrt(I0/D)

REF={ 'SSSS':19.7392,'CCCC':35.9852,'SCSC':28.9509,'SSSC':23.6463,
      'SFSF':9.6314,'SCSF':12.6874,'SSSF':11.6845,'CCCF':24.020,'CFFF':3.4917,'CCFF':6.9421 }
def edges(code): return code[0],code[2],code[1],code[3]
print(f"{'case':7}{'Ritz 5x5':>11}{'reference':>11}{'err %':>9}")
for code,ref in REF.items():
    ex0,ex1,ey0,ey1 = code[0],code[2],code[1],code[3]
    try:
        w=ritz(D,I0,a,b,nu,ex0,ex1,ey0,ey1,NT=5)
        lam=w[0]*sc
        print(f"  {code:5}{lam:11.4f}{ref:11.4f}{100*(lam-ref)/ref:+9.3f}")
    except Exception as ex:
        print(f"  {code:5}  error: {ex}")
