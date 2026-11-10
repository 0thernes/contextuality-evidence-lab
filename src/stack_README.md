# Native Tsotchke experiment

Run `python scripts/run_stack.py` with GCC, Node, NumPy and Eshkol installed.
Set `ESHKOL_RUN` or pass `--eshkol-run` for a nonstandard installation. All four
components are required. Missing dependencies or failed checks return nonzero;
`results/stack_report.json` records failure instead of retaining a stale pass.

The two-qubit square is `XI IX XX / IZ ZI ZZ / XZ ZX YY`. Contexts are its three
rows followed by three columns, numbered 0 through 5. Only the last column has
negative product. Independent exact Pauli multiplication checks commutation and
all six signed identity products; deliberately flipped signs are rejected.

Moonlab executes every preparation gate, Pauli-basis rotation, native measurement
and collapse. The tests cover zero, plus, Bell, complex and all computational
basis states, randomized compatible measurement order, repeated measurements,
and independent direct expectations. A separate experiment records 6,000 fresh
trials by default. Each trial has a uniformly selected setting under the ideal
uniform-word sampler model, three sequential Pauli measurements and independent
1% readout flips under the software noise model. Integer draws use rejection
sampling to avoid modulo mapping bias. Outcomes and flips are retained in
`results/stack_shots.json`; `results/stack_trials.json` is the compact array
`[{"context": 0, "success": true}, ...]` consumed by the evidence analysis.

QGTL computes the Fubini--Study metric and Berry curvature on a two-qubit family
prepared by Moonlab using local Ry and Rz gates followed by a fixed CNOT. Central
differences supply the four parameter derivatives. Direct inner products,
analytic product-sphere geometry, phase-gauge changes and a deliberately wrong
curvature sign are checked. Curvature convention is `F = -2 Im Q`.

Eshkol enumerates all 512 value assignments. Its violation histogram is
`[0,96,0,320,0,96,0]`; there is an explicit single-violation assignment for each
context. Six biased distributions put weight `5/60=1/12` on a selected context
and `11/60` on each other context. Exhaustive maximum success is `55/60=11/12`
for each. Python independently checks these results. The general statement for
all distributions satisfying a conditional floor is a separate mathematical
claim, not inferred from these six examples.

All execution is classical. Moonlab is a simulator and quantum_rng is a seeded
software mixer. Sampling here does not establish experimental measurement
independence, entropy quality, or hardware contextuality. Rejection sampling
removes a mapping bias conditional on uniform source words; it does not make a
deterministic stream into certified random input. Finite state probes test the
implementation; the algebraic context products are the source of ideal state
independence. Geometry checks are numerical, not a formalization of QGTL in Lean.
