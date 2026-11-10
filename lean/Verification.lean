module

import Evidence

/-! Audit every theorem declared in this project's namespace. Imported mathlib
theorems are audited transitively when they are dependencies of these theorems. -/

#check Evidence.square_no_all_win
#check Evidence.square_singleton_witness
#check Evidence.sharp_minimum
#check Evidence.success_upper_bound
#check Evidence.defect_success_bound
#check Evidence.ideal_observables
#check Evidence.ideal_context_commutation
#check Evidence.ideal_context_product
#check Evidence.local_factor_bound
#check Evidence.BetTree.finite_hitting_bound
#check Evidence.naive_attack_prefix_crosses
#check Evidence.naive_attack_prefix_probability
#check Evidence.concrete_classical_false_positive
#check Evidence.classical_square_node_valid

open Lean Elab Command in
run_cmd do
  let environment ← getEnv
  let declarations := environment.constants.toList.filter fun entry =>
    (`Evidence).isPrefixOf entry.1
  -- Modern Lean module interfaces expose theorem types without classifying
  -- their public ConstantInfo as `.thmInfo`. Test whether the type is a
  -- proposition instead of using `ConstantInfo.isTheorem`, which misses them.
  let propositions ← liftTermElabM do
    let mut names : Array Name := #[]
    for (name, information) in declarations do
      if ← Meta.isProp information.type then names := names.push name
    pure names
  let ordered := propositions.qsort fun x y => x.toString < y.toString
  let permitted := #[`propext, `Classical.choice, `Quot.sound]
  if ordered.isEmpty then throwError "No project theorems found"
  for required in #[`Evidence.square_no_all_win, `Evidence.square_singleton_witness,
      `Evidence.BetTree.finite_hitting_bound, `Evidence.concrete_all_positive_false_positive,
      `Evidence.classical_square_node_valid, `Evidence.ideal_context_product] do
    unless ordered.contains required do
      throwError "Axiom audit failed to discover required theorem {required}"
  for declaration in ordered do
    let dependencies ← Lean.collectAxioms declaration
    for dependency in dependencies do
      unless permitted.contains dependency do
        throwError "Forbidden axiom {dependency} in {declaration}"
    let json := Json.mkObj [
      ("theorem", toJson declaration.toString),
      ("axioms", toJson (dependencies.map Name.toString))]
    logInfo m!"AXIOM_AUDIT {json.compress}"
  logInfo m!"AXIOM_AUDIT_COUNT {ordered.size}"
