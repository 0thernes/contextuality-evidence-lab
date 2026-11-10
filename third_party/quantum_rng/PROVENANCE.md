# quantum_rng provenance and scope

Upstream: [tsotchke/quantum_rng](https://github.com/tsotchke/quantum_rng).
Pinned commit: [`1a77e77f803c63883349b658361c06401cd8ceb7`](https://github.com/tsotchke/quantum_rng/tree/1a77e77f803c63883349b658361c06401cd8ceb7).

Verified against the upstream GitHub tree on 2026-11-09:

| Local/upstream path | Git blob SHA-1 |
|---|---|
| `src/quantum_rng/quantum_rng.c` | `6146323cc4a0c412a9c2936e38329d592d1fca59` |
| `src/quantum_rng/quantum_rng.h` | `62535c702eca5190026c8cd738ec886d6ecd69aa` |
| `src/common/secure_memory.h` | `ade22b336f45615d1b167d3f62b8617dabe58458` |
| `LICENSE` | `e42af9827970b426259e4e453b321b2ebcd6321c` |

These files match upstream after Git's CRLF-to-LF normalization. No local
changes were made to the vendored implementation, including the upstream
Windows-compatible secure-memory fallback. The MIT license is retained.

The experiment uses the legacy `qrng_init` / `qrng_bytes` software API with an
explicit seed. This is a **classical quantum-inspired software mixer**, not a
physical quantum random-number source. It does not use this repository's
separate v3 API or hardware-entropy integrations. Quantum-themed identifiers
and constants in the code do not establish quantum behavior.

The stream depends on floating-point/libm behavior. Repeating an explicit
seed on the same tested build produced identical bytes, but cross-platform
byte identity is not promised. `scripts/stack_audit.py` records compiler and
binary/stream SHA-256 fingerprints. Binary fingerprints can change because
of platform linker timestamps; the source commit and stream fingerprint are
the stable scientific references for that toolchain. Search witnesses are
checked independently of the random stream. No statistical entropy,
cryptographic unpredictability, or hardware certification is claimed.
