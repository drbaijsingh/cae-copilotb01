# cae-copilotb01
Free browser tool for structural CAE. Generates runnable ABAQUS, ANSYS, LS-DYNA and MATLAB scripts, diagnoses solver errors, and analyses functionally graded, laminated and sandwich plates. Validated against Leissa to 0.03%.
CAE Copilot
A validated, browser-based toolkit for structural CAE and plate vibroacoustics. Free. No installation, no login, no data leaves your machine.

Built by Dr. Baij Nath Singh — PhD in Mechanical Engineering (Vibroacoustics), IIT (ISM) Dhanbad.


What it does
Script Builder
Describe a plate problem once — geometry, material, boundary conditions, mesh — and get a commented, runnable script for the solver you use.

Solver
Language
Analyses
ABAQUS
Python (abaqus cae noGUI=)
static, modal, buckling, explicit impact
ANSYS
APDL macro
static, modal, buckling, harmonic
LS-DYNA
keyword deck
explicit impact
MATLAB
script
modal, harmonic, vibroacoustic radiation

Error Doctor
Paste a message from a .msg, .dat, .log or d3hsp file. Get the actual cause and a ranked list of fixes in the order an experienced analyst would try them. Nineteen curated solver errors across ABAQUS, ANSYS and LS-DYNA.

It returns nothing when it does not recognise an error, rather than inventing a plausible cause.
Setup Advisor
Six analysis classes — strength, vibration, impact, buckling, fatigue, acoustics — each with the analysis type, element choice, mesh rule, solver settings, and the specific mistakes that quietly invalidate that class of work.
Materials module
Functionally graded plates — power, sigmoid and exponential gradation under Voigt, Mori–Tanaka or Reuss homogenisation, referenced to the physical neutral surface so the bending–stretching coupling vanishes identically. Any of 18 phases in either position, so ceramic–ceramic systems work as well as the conventional ceramic–metal.
Composite laminates — full ABD matrix from standard notation ([0/±45/90]2s parses), with symmetry, balance and bend–twist diagnostics that tell you when the closed-form frequency no longer applies.
Sandwich panels — shear-corrected throughout, because classical thin-plate theory overpredicts sandwich stiffness badly. Face yielding, core shear and face wrinkling margins.
Parametric study — sweep any of eleven design variables, chart the response, export as CSV or a booktabs LaTeX table.


Why a deterministic tool
Every script comes from a fixed template. Every frequency comes from a published closed-form solution. Where a method does not apply, the tool says so and stops.

A general-purpose language model will answer any plate question fluently, and some of the answers will be wrong in ways you cannot detect without doing the calculation yourself — which is what you asked it to do. This tool is built the other way round.

The pairing is the point. For any plate you can generate both the FE deck and the analytical solution. Run both. Agreement is evidence. Disagreement is information, usually about your boundary conditions or your units. Every generated script prints the analytical value in its header comment, so the FE run has something to check itself against the moment it finishes.


Validation
Frequency parameter λ = ωa²√(ρh/D) for a square isotropic plate, ν = 0.3, against Leissa (1969):

Case
Computed
Reference
Error
Method
SSSS
19.7394
19.7392
+0.001%
Lévy, exact
SCSS
23.6462
23.6463
−0.000%
Lévy, exact
SCSC
28.9508
28.9509
−0.000%
Lévy, exact
SSSF
11.6842
11.6845
−0.003%
Lévy, exact
SCSF
12.6870
12.6874
−0.003%
Lévy, exact
SFSF
9.6313
9.6314
−0.002%
Lévy, exact
CCCC
35.9912
35.9852
+0.017%
Rayleigh–Ritz 5×5
CCCF
24.0227
24.0200
+0.011%
Rayleigh–Ritz 5×5
CFFF
3.4917
3.4917
−0.000%
Rayleigh–Ritz 5×5
CCFF
6.9440
6.9421
+0.028%
Rayleigh–Ritz 5×5


Worst error 0.028%. Exact wherever a simply supported pair admits the Lévy solution; Rayleigh–Ritz otherwise, which is a minimum principle and therefore always an upper bound.

Further checks: the laminate routine reproduces A₁₁ = Eh/(1−ν²) and D₁₁ = Eh³/12(1−ν²) exactly for a single isotropic ply, gives B = 0 and D₁₆ = D₂₆ = 0 for symmetric cross-ply, and returns λ = 19.7392 for an isotropic square plate. The FGM routine returns the exact homogeneous rigidity at n = 0 with the neutral surface at mid-plane to machine precision. Mori–Tanaka is bounded by Voigt above and Reuss below at every volume fraction.

The validation/ folder contains every script that produces these numbers, plus VALIDATION.md with the full results and a record of four genuine physics errors that this process caught during development. Run them yourself.


Using it
Open the live site — or clone this repository and double-click index.html. It runs offline, indefinitely, with no dependencies.

index.html      landing page

copilot.html    Script Builder · Error Doctor · Setup Advisor

materials.html  FGM · laminate · sandwich · parametric study

validation/     the scripts that verify every number above


Scope and limits
State these honestly if you use the tool in published work.

Flat rectangular plates only. No curved shells, stiffened panels or cutouts.
Thin-plate (Kirchhoff) theory in the analytical solutions. Above roughly h/L = 0.05, shear deformation matters and these overpredict frequencies — use FSDT or the generated FE model instead.
Rayleigh–Ritz values are upper bounds, converged to ~0.03% at 5×5 for the cases tested, but not exact.
The laminate frequency formula assumes B = 0 and D₁₆ = D₂₆ = 0. The tool warns when a layup violates that; take the warning seriously.
Sandwich failure checks are a simply supported strip under uniform pressure — a first sizing pass, not a certification analysis.
LS-DYNA output covers the control, material, section and boundary cards. Bring your own mesh.


Citing this
Cite the methods — Mori–Tanaka homogenisation, the physical neutral surface formulation, classical lamination theory, Lévy's solution, Rayleigh–Ritz with characteristic beam functions, Warburton (1954), Leissa (1969), Elliott & Johnson (1993) for the elemental radiator model. Implementations are checked, not cited.

If you want to cite the software itself, use the archived release DOI.


Contributing
The physics lives in plainly named functions near the top of each file's <script> block — moriTanaka, fgmStiffness, computeABD, levyFreqs, ritzFreqs, sandwich. Script generators sit below them, so you can add a solver without touching the physics, or add physics without touching the generators. Adding a material is one entry in the arrays at the top.

Roadmap, in order of value:

Lévy for specially orthotropic laminates — replace the scalar D with D₁₁, D₁₂+2D₆₆, D₂₂ in the ODE. The machinery already exists.
First-order shear deformation theory for thick FGM plates.
Fluid loading and added mass for the vibroacoustic module.
A unit-system toggle (SI-m / SI-mm).

Issues and pull requests welcome. If you find a number that disagrees with a published reference, that is the most valuable thing you can report.


Licence
MIT — see LICENSE. Use it, modify it, teach with it, build on it.

