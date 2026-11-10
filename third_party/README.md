# Pinned Tsotchke dependencies

The minimal dependencies were copied byte-for-byte from the existing
Contextuality Tensor Lab checkout on 10 November 2026. The original provenance
records are retained; references within those records to Hoggar Bound Lab and
its scripts refer to that historical project. Current execution evidence for
this repository is `../results/stack_report.json`, produced by
`../scripts/run_stack.py`. Original MIT licenses remain in each directory.

| Component | Pinned upstream commit | Current use |
| --- | --- | --- |
| Moonlab | `cd3b2347e3739327548708073d7e4ac710cc6a6c` | Native CPU/WASM gates, state preparation, Born sampling and projective collapse |
| quantum_geometric_tensor | `770994aa8ddd858e6bb16eebb25250a7b9f67c96` | Native C pure-state metric and curvature kernels |
| quantum_rng | `1a77e77f803c63883349b658361c06401cd8ceb7` | Seeded legacy software mixer for settings, readout and measurement draws |

`SHA256SUMS.json` fixes the imported files. The prebuilt Moonlab WASM is not
independently rebuilt here; its wrapper relies on the pinned WASM32 state
layout. The local empty `qgtl/stub/cblas.h` is a compatibility shim; no tested
function in this translation unit calls BLAS. Quantum_rng has floating-point
dependencies, so only same-build seeded replay is promised. Eshkol is an
external runtime; the report records its version and executable fingerprint.
No hardware quantum device, hardware entropy, GPU backend or speedup is claimed.
