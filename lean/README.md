# Formal verification

This is a standalone Lean 4.35.0 / mathlib v4.35.0 project. The manifest pins
mathlib and its transitive dependencies. The statements use real probabilities;
benchmark constants and comparisons are exact rational expressions inside the
reals. Computation over the finite assignment and matrix models is checked by
Lean's kernel. There are no admitted proofs, project axioms, or `native_decide`
proofs.

From this directory:

```sh
lake exe cache get
lake build
lake env lean Verification.lean
```

On the authoring Windows machine, Lake is at
`C:\Users\Alexa\.elan\bin\lake.exe`. An ignored `.lake/packages` junction reuses
an already installed v4.35.0 dependency cache. That cache is an installation
convenience and is not needed to reproduce the public project from its manifest.

## What is proved

`Evidence/Square.lean` defines the nine global outcome bits and the six rows and
columns of the Peres--Mermin square, with only the final column negative. It proves:

- Every deterministic global assignment loses at least one context.
- For each context there is an assignment losing only that context.
- For a nonnegative normalized context distribution, the sharp classical success
  bound is `1 - min p`. A pointwise probability floor `beta` implies success at
  most `1 - beta`.
- Finite convex mixtures of the allowed deterministic tables preserve the bound.
- An explicitly modeled arbitrary defect fraction `delta` changes the success
  bound to `1 - (1 - delta) * beta`.
- The concrete biased distribution `(11,11,11,11,11,5)/60` has sharp success bound
  `11/12`, whereas uniform context selection has the familiar `5/6` bound.

The pointwise floor must hold **conditional on the past and the hidden variables**
of the null model. A marginal histogram of contexts does not establish that
assumption. The assigned value table must not change with the chosen context.

`Evidence/Physical.lean` constructs the standard two-qubit ideal observables from
the integer Pauli X and Z matrices, using `YY = -(XZ tensor XZ)`. It proves
symmetry, involution, within-context commutation, and the six signed products.
These ideal identities do not establish compatibility or the absence of
disturbance in a physical apparatus.

`Evidence/Sequential.lean` proves a general finite-tree theorem. Every internal
node has its own conditional success probability and nonnegative win/loss
factors. If the conditional expected factor is at most one at every node, then:

- expected terminal wealth is at most starting wealth;
- the probability of hitting positive threshold `T` anywhere in the finite tree
  is at most starting wealth divided by `T`.

Different children and different node parameters permit adaptation to the full
binary history. Arbitrary stopping is represented by leaf nodes at any depth.
The theorem is for **every finite tree**; an infinite-horizon measure-theoretic
statement is not included. It assumes the stated conditional-probability model
and does not formalize a hardware data-collection process or the Python runtime.

The calibration lemma proves that factors `A >= B >= 0` satisfying
`b*A + (1-b)*B <= 1` are valid for every actual success probability at most `b`.
The benchmark uses alternative success `19/20`:

| Calibration | Null bound | Win factor | Loss factor |
|---|---:|---:|---:|
| Bias-aware | 11/12 | 57/55 | 3/5 |
| Naively uniform | 5/6 | 57/50 | 3/10 |

Applied at the biased classical boundary, the naive expected factor is
`107/100`, so it is invalid. Exact comparisons prove that its first 36 successes
cross threshold 100, while that event has probability greater than `43/1000` in
the independent biased-classical construction. The protected factors do not
cross on that prefix. These comparisons establish a concrete finite-sample
counterexample to the miscalibrated test; the valid-tree theorem supplies the
protected test's bound.

`Evidence/Bridge.lean` connects the actual square success probability directly to
the valid-node certificate. It also proves that the concrete all-`+1` assignment
under the displayed biased distribution makes an explicit 36-round stopped
naive test cross threshold 100 with probability greater than 4.3%. This is an
exact counterexample in the formal tree model, not just two unrelated numeric
inequalities.

## Axiom audit

`Verification.lean` enumerates every theorem in namespace `Evidence`, computes
its transitive axiom dependencies, and fails on any dependency other than the
standard Lean/mathlib foundations `propext`, `Classical.choice`, and `Quot.sound`.
It emits one `AXIOM_AUDIT` JSON record per theorem and a final count. These are
standard foundations, not extra assumptions about this experiment.

## Relation to prior work

The Peres--Mermin square and finite nonnegative-supermartingale maximal bounds
are established mathematics. This project formalizes their composition and a
specific biased-choice counterexample; it does not claim these underlying
theorems as newly discovered. Earlier Contextuality Tensor Lab source was
inspected for environment compatibility and mathematical conventions. The files
here are newly authored; no earlier lab is a build dependency.
