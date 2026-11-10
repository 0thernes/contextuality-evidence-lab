module

public import Evidence.Square
public import Mathlib.LinearAlgebra.Matrix.Kronecker

@[expose] public section

/-!+# The standard ideal two-qubit realization

These definitions use the standard real X and Z Pauli matrices, and construct
the real two-qubit matrix Y tensor Y as -(XZ) tensor (XZ). All identities are
checked by the kernel over integers. They establish ideal operator identities,
not physical apparatus compatibility, isolation, or absence of disturbance.
-/

open Matrix
open scoped Kronecker

namespace Evidence

abbrev OneQubitMatrix := Matrix (Fin 2) (Fin 2) ℤ
abbrev TwoQubitMatrix := Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℤ

def pauliX : OneQubitMatrix := !![0, 1; 1, 0]
def pauliZ : OneQubitMatrix := !![1, 0; 0, -1]

/-- Observable order XI, IX, XX, IZ, ZI, ZZ, XZ, ZX, YY. -/
def squareObservable : Fin 9 → TwoQubitMatrix :=
  ![pauliX ⊗ₖ 1, 1 ⊗ₖ pauliX, pauliX ⊗ₖ pauliX,
    1 ⊗ₖ pauliZ, pauliZ ⊗ₖ 1, pauliZ ⊗ₖ pauliZ,
    pauliX ⊗ₖ pauliZ, pauliZ ⊗ₖ pauliX,
    -((pauliX * pauliZ) ⊗ₖ (pauliX * pauliZ))]

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem ideal_observables : ∀ i : Fin 9,
    squareObservable i * squareObservable i = 1 ∧
    (squareObservable i).transpose = squareObservable i := by
  decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem ideal_context_commutation : ∀ (c : Fin 6) (i j : Fin 3),
    squareObservable (contextTriple c i) * squareObservable (contextTriple c j) =
    squareObservable (contextTriple c j) * squareObservable (contextTriple c i) := by
  decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem ideal_context_product : ∀ c : Fin 6,
    squareObservable (contextTriple c 0) * squareObservable (contextTriple c 1) *
      squareObservable (contextTriple c 2) =
    if c == 5 then -(1 : TwoQubitMatrix) else 1 := by
  decide +kernel

end Evidence
