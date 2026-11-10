module

public import Evidence.Square
public import Evidence.Sequential

@[expose] public section

noncomputable section

namespace Evidence

/-- End-to-end local bridge: the actual winning probability of an arbitrary
global square assignment under a normalized context distribution produces a
valid betting-tree node when calibrated to its context-probability floor. -/
theorem classical_square_node_valid (p : Fin 6 → ℝ) (a : Assignment)
    (β A B : ℝ) (win lose : BetTree)
    (hβ : 0 ≤ β) (hp : ∀ c, β ≤ p c) (hsum : ∑ c, p c = 1)
    (hB : 0 ≤ B) (hBA : B ≤ A)
    (hcal : (1-β)*A + β*B ≤ 1) (hw : win.Valid) (hl : lose.Valid) :
    (BetTree.node (successProbability p a) A B win lose).Valid := by
  have hq0 := success_nonnegative p a (fun c => hβ.trans (hp c))
  have hqb := success_upper_bound p a β hβ hp hsum
  apply BetTree.valid_node_of_null_bound (successProbability p a) (1-β) A B win lose
    hq0 (by linarith) hqb hB hBA
  · convert hcal using 1; ring
  · exact hw
  · exact hl

/-- There is an actual deterministic square table whose biased-context winning
probability makes the specified naive stopped test falsely cross threshold 100
with probability greater than 4.3%. -/
theorem concrete_classical_false_positive : ∃ a : Assignment,
    (43 : ℝ)/1000 <
      (winPrefixTree 36 (successProbability biasedContextProbability a)
        (57/50) (3/10)).hitProbability 1 100 := by
  obtain ⟨a, ha⟩ := biased_square_bound_sharp
  have hs := success_add_failure biasedContextProbability a
  rw [biased_context_distribution.1] at hs
  have hq : successProbability biasedContextProbability a = (11 : ℝ)/12 := by linarith
  refine ⟨a, ?_⟩
  rw [hq]
  exact concrete_naive_false_positive

/-- Exact artifact binding: the deterministic table is +1 at all nine
observables, so only the negatively signed final column loses. -/
theorem concrete_all_positive_false_positive :
    (43 : ℝ)/1000 <
      (winPrefixTree 36
        (successProbability biasedContextProbability (fun _ => false))
        (57/50) (3/10)).hitProbability 1 100 := by
  rw [biased_all_positive_success]
  exact concrete_naive_false_positive

theorem protected_prefix_tree_valid (n : ℕ) (q : ℝ)
    (hq0 : 0 ≤ q) (hqb : q ≤ (11 : ℝ)/12) :
    (winPrefixTree n q (57/55) (3/5)).Valid := by
  induction n with
  | zero => trivial
  | succ n ih =>
    apply BetTree.valid_node_of_null_bound q (11/12) (57/55) (3/5)
      (winPrefixTree n q (57/55) (3/5)) .stop hq0 (by linarith) hqb
    · norm_num
    · norm_num
    · norm_num
    · exact ih
    · trivial

theorem protected_prefix_threshold_bound (n : ℕ) (q T : ℝ)
    (hq0 : 0 ≤ q) (hqb : q ≤ (11 : ℝ)/12) (hT : 0 < T) :
    (winPrefixTree n q (57/55) (3/5)).hitProbability 1 T ≤ 1/T := by
  exact biased_unit_start_threshold _ (protected_prefix_tree_valid n q hq0 hqb) T hT

end Evidence
