# QGTL provenance and scope

Upstream: [tsotchke/quantum_geometric_tensor](https://github.com/tsotchke/quantum_geometric_tensor).
Pinned commit: [`770994aa8ddd858e6bb16eebb25250a7b9f67c96`](https://github.com/tsotchke/quantum_geometric_tensor/tree/770994aa8ddd858e6bb16eebb25250a7b9f67c96)
(upstream commit description: v0.777 beta release).

Verified against the upstream GitHub tree on 2026-11-09:

| Local/upstream path | Git blob SHA-1 |
|---|---|
| `src/quantum_geometric/distributed/differential_geometry.c` | `f2f92a68a92f7d4866eea24e6e9a810c21b94e6a` |
| `include/quantum_geometric/distributed/differential_geometry.h` | `0222e4dbeb60fd2e003f025466d7ffa1ec424c60` |
| `LICENSE` | `e42af9827970b426259e4e453b321b2ebcd6321c` |

These files match upstream after Git's CRLF-to-LF normalization. The MIT
license is retained. The one local compatibility file is `stub/cblas.h`, an
empty header explicitly labeled as local. The compiled translation unit has
no calls to BLAS, so no BLAS implementation is replaced or emulated.

The lab tests two actual C functions: `diffgeo_compute_fubini_study` and
`diffgeo_compute_berry_curvature`, with **normalized pure states and supplied
parameter derivatives**. The latter returns `F_ij = -2 Im Q_ij`; this
convention is used explicitly in the experiments. These kernels do not
normalize their state input, so callers must provide a unit vector.

`scripts/stack_audit.py` builds a shared library from this source and compares
its outputs against independent NumPy inner products, phase-gauge shifts,
and random normalized states. Only those kernels and conditions are audited.
The broader QGTL library, generic-coordinate QGT entry point, distributed
algorithms, GPU paths, and other geometry routines are not validated here.
