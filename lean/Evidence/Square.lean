module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Data.Matrix.Basic
public import Mathlib.Tactic

@[expose] public section

/-!+# The bias-aware Peres--Mermin bound

The deterministic null assigns one Bool to each observable, independently of
the chosen context. `true` is the outcome -1. The six triples are rows followed
by columns; only the last column has negative quantum product.

These are assumptions about the null model. The theorem does not establish
measurement compatibility or context-choice independence for a physical device.
-/

open Finset

noncomputable section

namespace Evidence

abbrev Assignment := Fin 9 → Bool

def contextTriple : Fin 6 → Fin 3 → Fin 9 :=
  ![![0, 1, 2], ![3, 4, 5], ![6, 7, 8],
    ![0, 3, 6], ![1, 4, 7], ![2, 5, 8]]

def contextParity (a : Assignment) (c : Fin 6) : Bool :=
  (a (contextTriple c 0) != a (contextTriple c 1)) != a (contextTriple c 2)

def loses (a : Assignment) (c : Fin 6) : Bool :=
  contextParity a c != (c == 5)

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem square_no_all_win : ∀ a : Assignment, ∃ c : Fin 6, loses a c = true := by
  decide +kernel

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem square_singleton_witness : ∀ c : Fin 6, ∃ a : Assignment,
    ∀ d : Fin 6, loses a d = (d == c) := by
  decide +kernel

def failureProbability (p : Fin 6 → ℝ) (a : Assignment) : ℝ :=
  ∑ c, if loses a c then p c else 0

def successProbability (p : Fin 6 → ℝ) (a : Assignment) : ℝ :=
  ∑ c, if loses a c then 0 else p c

theorem success_add_failure (p : Fin 6 → ℝ) (a : Assignment) :
    successProbability p a + failureProbability p a = ∑ c, p c := by
  unfold successProbability failureProbability
  rw [← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro c _
  split_ifs <;> ring

theorem success_nonnegative (p : Fin 6 → ℝ) (a : Assignment)
    (hp : ∀ c, 0 ≤ p c) : 0 ≤ successProbability p a := by
  apply Finset.sum_nonneg
  intro c _
  split_ifs
  · exact le_refl 0
  · exact hp c

/-- A pointwise floor on the context distribution is the sharp null failure
bound. The probabilities may depend on the entire past and hidden state, provided
this floor holds after that conditioning and the value table is context independent. -/
theorem failure_lower_bound (p : Fin 6 → ℝ) (a : Assignment) (β : ℝ)
    (hβ : 0 ≤ β) (hp : ∀ c, β ≤ p c) : β ≤ failureProbability p a := by
  obtain ⟨c, hc⟩ := square_no_all_win a
  calc
    β ≤ p c := hp c
    _ = (if loses a c then p c else 0) := by simp [hc]
    _ ≤ ∑ d : Fin 6, if loses a d then p d else 0 := by
      apply Finset.single_le_sum (s := Finset.univ)
        (f := fun d : Fin 6 => if loses a d then p d else 0)
      · intro d _
        split_ifs
        · exact hβ.trans (hp d)
        · exact le_refl 0
      · exact Finset.mem_univ c

theorem success_upper_bound (p : Fin 6 → ℝ) (a : Assignment) (β : ℝ)
    (hβ : 0 ≤ β) (hp : ∀ c, β ≤ p c) (hsum : ∑ c, p c = 1) :
    successProbability p a ≤ 1 - β := by
  have hf := failure_lower_bound p a β hβ hp
  have hsf := success_add_failure p a
  rw [hsum] at hsf
  linarith

theorem singleton_failure_probability (p : Fin 6 → ℝ) (c : Fin 6)
    (a : Assignment) (ha : ∀ d, loses a d = (d == c)) :
    failureProbability p a = p c := by
  simp [failureProbability, ha]

/-- Attainment at every chosen coordinate. In particular the best deterministic
classical strategy loses exactly at a context of minimum selection probability. -/
theorem failure_bound_attained (p : Fin 6 → ℝ) (c : Fin 6) :
    ∃ a : Assignment, failureProbability p a = p c := by
  obtain ⟨a, ha⟩ := square_singleton_witness c
  exact ⟨a, singleton_failure_probability p c a ha⟩

theorem sharp_minimum (p : Fin 6 → ℝ) (c : Fin 6)
    (hp : ∀ d, 0 ≤ p d) (hc : ∀ d, p c ≤ p d) :
    (∃ a : Assignment, failureProbability p a = p c) ∧
    (∀ a : Assignment, p c ≤ failureProbability p a) := by
  exact ⟨failure_bound_attained p c, fun a => failure_lower_bound p a (p c) (hp c) hc⟩

/-- Convex mixtures of context-independent deterministic tables preserve the bound. -/
theorem mixture_failure_lower_bound {ι : Type*} [Fintype ι]
    (weights failures : ι → ℝ) (β : ℝ)
    (hw : ∀ i, 0 ≤ weights i) (hsum : ∑ i, weights i = 1)
    (hf : ∀ i, β ≤ failures i) :
    β ≤ ∑ i, weights i * failures i := by
  calc
    β = ∑ i, weights i * β := by rw [← Finset.sum_mul, hsum, one_mul]
    _ ≤ ∑ i, weights i * failures i :=
      Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left (hf i) (hw i)

/-- Explicit defect model: at most δ of the conditional mixture is arbitrary.
`goodSuccess ≤ 1-β` applies only to its remaining context-independent component. -/
theorem defect_success_bound (β δ goodSuccess badSuccess : ℝ)
    (hδ0 : 0 ≤ δ) (hδ1 : δ ≤ 1)
    (hgood : goodSuccess ≤ 1 - β) (hbad : badSuccess ≤ 1) :
    (1 - δ) * goodSuccess + δ * badSuccess ≤ 1 - (1 - δ) * β := by
  have hg := mul_le_mul_of_nonneg_left hgood (sub_nonneg.mpr hδ1)
  have hb := mul_le_mul_of_nonneg_left hbad hδ0
  nlinarith

def biasedContextProbability : Fin 6 → ℝ :=
  ![11/60, 11/60, 11/60, 11/60, 11/60, 1/12]

theorem all_positive_singleton_loss :
    ∀ c : Fin 6, loses (fun _ => false) c = (c == 5) := by decide

theorem biased_context_distribution :
    (∑ c, biasedContextProbability c = 1) ∧
    (∀ c, (1 : ℝ)/12 ≤ biasedContextProbability c) := by
  constructor
  · norm_num [biasedContextProbability, Fin.sum_univ_succ]
  · intro c
    fin_cases c <;> norm_num [biasedContextProbability]

theorem biased_square_success_bound (a : Assignment) :
    1 - failureProbability biasedContextProbability a ≤ (11 : ℝ)/12 := by
  have h := failure_lower_bound biasedContextProbability a (1/12)
    (by norm_num) biased_context_distribution.2
  linarith

theorem biased_square_bound_sharp :
    ∃ a : Assignment, 1 - failureProbability biasedContextProbability a = (11 : ℝ)/12 := by
  obtain ⟨a, ha⟩ := failure_bound_attained biasedContextProbability 5
  refine ⟨a, ?_⟩
  have hzero : biasedContextProbability 5 = (1 : ℝ)/12 := by
    norm_num [biasedContextProbability]
  rw [hzero] at ha
  linarith

theorem biased_all_positive_success :
    successProbability biasedContextProbability (fun _ => false) = (11 : ℝ)/12 := by
  have hf := singleton_failure_probability biasedContextProbability 5
    (fun _ => false) all_positive_singleton_loss
  have hlast : biasedContextProbability 5 = (1 : ℝ)/12 := by
    norm_num [biasedContextProbability]
  rw [hlast] at hf
  have hs := success_add_failure biasedContextProbability (fun _ => false)
  rw [biased_context_distribution.1] at hs
  linarith

end Evidence
