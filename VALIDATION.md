# Validation record

All values produced by the scripts in this folder, run August 2026.
Reproduce with `python3 <script>.py`.

---

## 1. FGM homogenization and neutral surface

Al₂O₃ / Aluminium, h = 10 mm, Mori–Tanaka.

**Limiting cases** — the graded plate must collapse onto the homogeneous one:

| Case | D computed | D reference | Error | z_ns |
|---|---|---|---|---|
| n = 0 (all ceramic) | 3.4799e+04 | 3.4799e+04 | +0.000% | −2.2e−19 |
| n → ∞ (all metal) | 6.4315e+03 | 6.4103e+03 | +0.332% | +5.5e−06 |

The n = 0 case is exact and the neutral surface returns to the mid-plane to
machine precision, which is the check that the neutral-surface integration is
right.

**Neutral surface shift** — peaks at intermediate gradation, returns to zero at
both homogeneous limits, as it must:

| n | z_ns / h |
|---|---|
| 0.2 | +0.07087 |
| 0.5 | +0.11069 |
| 1 | +0.13498 |
| 2 | +0.14109 |
| 5 | +0.11286 |
| 10 | +0.07767 |

**Homogenization bounding** at V_c = 0.5:

| Scheme | E (GPa) |
|---|---|
| Voigt (upper bound) | 225.00 |
| Mori–Tanaka | 144.02 |
| Reuss (lower bound) | 118.22 |

Mori–Tanaka lies strictly between the bounds, as required.

---

## 2. Classical lamination theory

| Check | Result |
|---|---|
| Single isotropic ply, A₁₁ | 1.153846e+09 = Eh/(1−ν²) exactly |
| Single isotropic ply, D₁₁ | 2.403846e+03 = Eh³/12(1−ν²) exactly |
| Single isotropic ply, \|B\| | 0.000e+00 |
| Symmetric [0/90]s, \|B\| | 8.5e−14 (numerical zero) |
| Symmetric [0/90]s, D₁₆, D₂₆ | 6.3e−19, 9.7e−18 (numerical zero) |
| Antisymmetric [0/90], \|B\| | 1.0141e+03 (correctly non-zero) |
| Isotropic plate via laminate route, λ | **19.7392** vs classical 19.739 |

---

## 3. Sandwich shear correction

Aluminium faces 0.5 mm, PVC foam core 20 mm, 1.0 × 0.6 m panel.

| Quantity | Value |
|---|---|
| D | 8.4013e+03 N·m |
| S | 1.0506e+06 N/m |
| Bending-only f₁ | 275.421 Hz |
| Shear-corrected f₁ | 241.732 Hz |
| Error if shear ignored | **+13.9%** |
| Face wrinkling stress | 444.0 MPa |

Shear must reduce the frequency. A sandwich result that ignores it is wrong in
a predictable direction — always too stiff, always too high.

---

## 4. Boundary conditions vs Leissa (1969)

Square isotropic plate, ν = 0.3. Frequency parameter λ = ωa²√(ρh/D).

### Lévy exact solution (one simply supported pair)

| Case | Computed | Leissa | Error |
|---|---|---|---|
| SSSS | 19.7392 | 19.7392 | +0.000% |
| SCSS | 23.6463 | 23.6463 | +0.000% |
| SCSC | 28.9509 | 28.9509 | −0.000% |
| SSSF | 11.6845 | 11.6845 | +0.000% |
| SCSF | 12.6874 | 12.6874 | −0.000% |
| SFSF | 9.6314 | 9.6314 | −0.000% |

### Rayleigh–Ritz, 5×5 beam functions (no simply supported pair)

| Case | Computed | Reference | Error |
|---|---|---|---|
| CCCC | 35.9915 | 35.9852 | +0.017% |
| CCCF | 24.0231 | 24.0200 | +0.013% |
| CFFF | 3.4919 | 3.4917 | +0.005% |
| CCFF | 6.9439 | 6.9421 | +0.026% |

Ritz is a minimum principle: every value is an upper bound, never below truth.
Errors are consistently positive, which is itself a correctness signal.

### End-to-end browser check

The same ten cases driven through the published app and converted back to λ:
**worst error +0.027%**, zero JavaScript errors. See `bcverify.js`.

---

## Bugs caught by this process

Two real physics errors were found by validation, not by review. Both would
have produced confident, plausible, wrong numbers.

**1. Cantilever plate edge mapping — 113% error.**
The first Warburton implementation mapped a CFFF plate's free edges onto
*clamped–free* beam functions. Validated against the known square-plate
parameter λ = 3.492, it returned 7.446. A free plate edge maps to a
**free–free** beam, whose first two indices are rigid-body modes. After the
fix: 3.518, +0.73%.

**2. Pinned–free rigid rotation omitted — 137% error.**
The Rayleigh–Ritz pinned–free basis initially contained only elastic modes.
SSSF came out at 27.758 against Leissa's 11.6845. A pinned–free beam has a
**rigid-body rotation about the pinned edge** that carries no strain energy
but is essential to the basis. After adding it: 11.7437, +0.51%, and 11.6845
exactly once Lévy took precedence for that case.

**3. Radiated power factor of two.**
The elemental-radiator power was written as W = (Aₑ²/2)·vᴴRv. Checked against
the small baffled piston limit, W = |v|²ω²ρ₀Aₑ²/(4πc₀), the factor of ½ is
wrong — the correct form is W = Aₑ²·vᴴRv. Confirmed by σ → 1 for a rigid
piston at high ka.

**4. Elemental radiator grid validity.**
A rigid piston returned σ = 22.99 at 8 kHz instead of 1, because the radiator
elements had become larger than the acoustic wavelength. The generated script
now checks this and refines automatically.

The general lesson, and the reason the tools are built from templates and
closed-form solutions rather than a language model: every one of these produced
output that looked entirely reasonable. Only a reference value caught them.
