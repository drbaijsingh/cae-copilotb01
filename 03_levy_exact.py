import numpy as np

# Levy solution: two opposite edges (x=0,a) simply supported.
# w(x,y) = W(y) sin(alpha x),  alpha = m*pi/a
# D(W'''' - 2a^2 W'' + a^4 W) = I0 w^2 W
#   => W'''' - 2a^2 W'' + (a^4 - lam) W = 0,  lam = I0 w^2 / D

def basis(y, a2, s, nu, alpha):
    """Return [W, W', W'', W'''] for each of the 4 basis functions at y."""
    b1 = np.sqrt(a2 + s)
    out = []
    # cosh(b1 y), sinh(b1 y)  -- scaled later
    out.append([np.cosh(b1*y), b1*np.sinh(b1*y), b1**2*np.cosh(b1*y), b1**3*np.sinh(b1*y)])
    out.append([np.sinh(b1*y), b1*np.cosh(b1*y), b1**2*np.sinh(b1*y), b1**3*np.cosh(b1*y)])
    if s > a2:            # trigonometric branch
        b2 = np.sqrt(s - a2)
        out.append([ np.cos(b2*y), -b2*np.sin(b2*y), -b2**2*np.cos(b2*y),  b2**3*np.sin(b2*y)])
        out.append([ np.sin(b2*y),  b2*np.cos(b2*y), -b2**2*np.sin(b2*y), -b2**3*np.cos(b2*y)])
    else:                 # hyperbolic branch
        b2 = np.sqrt(a2 - s)
        out.append([np.cosh(b2*y), b2*np.sinh(b2*y), b2**2*np.cosh(b2*y), b2**3*np.sinh(b2*y)])
        out.append([np.sinh(b2*y), b2*np.cosh(b2*y), b2**2*np.sinh(b2*y), b2**3*np.cosh(b2*y)])
    return np.array(out).T   # rows: W,W',W'',W'''   cols: basis

def rows_for(bc, d, nu, alpha):
    """Two BC rows given derivative table d[0..3] (each length 4)."""
    a2 = alpha**2
    if bc == 'S':   return [d[0], d[2] - nu*a2*d[0]]
    if bc == 'C':   return [d[0], d[1]]
    if bc == 'F':   return [d[2] - nu*a2*d[0], d[3] - (2-nu)*a2*d[1]]
    raise ValueError(bc)

def det_levy(w, D, I0, a, b, nu, m, bc0, bcb):
    alpha = m*np.pi/a
    lam = I0*w*w/D
    s = np.sqrt(lam)
    a2 = alpha**2
    d0 = basis(0.0, a2, s, nu, alpha)
    db = basis(b,   a2, s, nu, alpha)
    M = np.array(rows_for(bc0, d0, nu, alpha) + rows_for(bcb, db, nu, alpha), dtype=float)
    # normalise each row so the determinant stays in range
    for i in range(4):
        n = np.max(np.abs(M[i]))
        if n > 0: M[i] /= n
    return np.linalg.det(M)

def levy_freqs(D, I0, a, b, nu, m, bc0, bcb, wmax, nscan=24000, want=6):
    ws = np.linspace(1.0, wmax, nscan)
    prev = det_levy(ws[0], D, I0, a, b, nu, m, bc0, bcb)
    roots = []
    for i in range(1, nscan):
        cur = det_levy(ws[i], D, I0, a, b, nu, m, bc0, bcb)
        if np.isfinite(prev) and np.isfinite(cur) and prev*cur < 0:
            lo, hi = ws[i-1], ws[i]
            for _ in range(80):
                mid = 0.5*(lo+hi)
                fm = det_levy(mid, D, I0, a, b, nu, m, bc0, bcb)
                if prev*fm < 0: hi = mid
                else: lo = mid; prev = fm
            roots.append(0.5*(lo+hi))
            if len(roots) >= want: break
        prev = cur
    return roots

# ---- validation: isotropic square plate, nu = 0.3 -------------------
E, nu, h, rho, a, b = 210e9, 0.3, 0.005, 7850.0, 1.0, 1.0
D  = E*h**3/(12*(1-nu**2)); I0 = rho*h
scale = a*a*np.sqrt(I0/D)

LEISSA = {  # Leissa (1969), square plate, nu = 0.3 ; first mode of each family
  ('S','S'): 19.7392,   # SSSS
  ('C','S'): 23.6463,   # SCSS
  ('C','C'): 28.9509,   # SCSC
  ('F','S'): 11.6845,   # SSSF
  ('F','C'): 12.6874,   # SCSF
  ('F','F'):  9.6314,   # SFSF
}
print("Levy-type FGM/isotropic plate solver -- square plate, nu = 0.3")
print(f"{'case':8} {'computed':>10} {'Leissa':>9} {'err %':>8}")
wmax = 60.0/scale
for (b0, bb), ref in LEISSA.items():
    r = levy_freqs(D, I0, a, b, nu, 1, b0, bb, wmax, want=3)
    if not r:
        print(f"  S{b0}S{bb}  no root found"); continue
    lam = r[0]*scale
    print(f"  S{b0}S{bb}  {lam:10.4f} {ref:9.4f} {100*(lam-ref)/ref:+8.3f}")
