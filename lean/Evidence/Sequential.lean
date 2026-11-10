module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Tactic

@[expose] public section

/-!+# Exact finite adaptive betting certificates

Every internal node may choose its own conditional success chance and its own
two factors. Thus the finite tree represents arbitrary dependence on the full
binary history, including adaptive factor selection and early stopping.

The result is finite-horizon, for every finite tree. It does not use an IID
assumption and does not assert an infinite-horizon measure-theoretic theorem.
-/

noncomputable section

namespace Evidence

/-- A nonnegative monotone factor with mean at most one at the null boundary
also has mean at most one at every smaller success probability. -/
theorem local_factor_bound (s b A B : ℝ)
    (hsb : s ≤ b) (hBA : B ≤ A)
    (hcal : b * A + (1 - b) * B ≤ 1) :
    s * A + (1 - s) * B ≤ 1 := by
  have h := mul_nonneg (sub_nonneg.mpr hsb) (sub_nonneg.mpr hBA)
  nlinarith

inductive BetTree where
  | stop : BetTree
  | node (q A B : ℝ) (win lose : BetTree) : BetTree


/-- q is the actual conditional success chance. The two child trees may be
different, so no stationarity or independence between rounds is assumed. -/
def BetTree.Valid : BetTree → Prop
  | .stop => True
  | .node q A B win lose =>
      0 ≤ q ∧ q ≤ 1 ∧ 0 ≤ A ∧ 0 ≤ B ∧
      q * A + (1 - q) * B ≤ 1 ∧ win.Valid ∧ lose.Valid

def BetTree.expectedWealth : BetTree → ℝ → ℝ
  | .stop, z => z
  | .node q A B win lose, z =>
      q * win.expectedWealth (z * A) + (1 - q) * lose.expectedWealth (z * B)

def BetTree.hitProbability : BetTree → ℝ → ℝ → ℝ
  | .stop, z, T => if T ≤ z then 1 else 0
  | .node q A B win lose, z, T =>
      if T ≤ z then 1 else
        q * win.hitProbability (z * A) T +
        (1 - q) * lose.hitProbability (z * B) T

theorem BetTree.expected_wealth_nonnegative (tree : BetTree) (h : tree.Valid)
    (z : ℝ) (hz : 0 ≤ z) : 0 ≤ tree.expectedWealth z := by
  induction tree generalizing z with
  | stop => exact hz
  | node q A B win lose ihw ihl =>
    rcases h with ⟨hq0, hq1, hA, hB, _, hw, hl⟩
    exact add_nonneg (mul_nonneg hq0 (ihw hw (z*A) (mul_nonneg hz hA)))
      (mul_nonneg (sub_nonneg.mpr hq1) (ihl hl (z*B) (mul_nonneg hz hB)))

theorem BetTree.expected_wealth_bound (tree : BetTree) (h : tree.Valid)
    (z : ℝ) (hz : 0 ≤ z) : tree.expectedWealth z ≤ z := by
  induction tree generalizing z with
  | stop => exact le_refl z
  | node q A B win lose ihw ihl =>
    rcases h with ⟨hq0, hq1, hA, hB, hmean, hw, hl⟩
    have hw' := mul_le_mul_of_nonneg_left
      (ihw hw (z*A) (mul_nonneg hz hA)) hq0
    have hl' := mul_le_mul_of_nonneg_left
      (ihl hl (z*B) (mul_nonneg hz hB)) (sub_nonneg.mpr hq1)
    have hm := mul_le_mul_of_nonneg_left hmean hz
    simp only [BetTree.expectedWealth]
    nlinarith

theorem BetTree.hit_probability_nonnegative (tree : BetTree) (h : tree.Valid)
    (z T : ℝ) : 0 ≤ tree.hitProbability z T := by
  induction tree generalizing z with
  | stop => simp only [BetTree.hitProbability]; split_ifs <;> norm_num
  | node q A B win lose ihw ihl =>
    rcases h with ⟨hq0, hq1, _, _, _, hw, hl⟩
    simp only [BetTree.hitProbability]
    split_ifs
    · norm_num
    · exact add_nonneg (mul_nonneg hq0 (ihw hw (z*A)))
        (mul_nonneg (sub_nonneg.mpr hq1) (ihl hl (z*B)))

theorem BetTree.hit_probability_le_one (tree : BetTree) (h : tree.Valid)
    (z T : ℝ) : tree.hitProbability z T ≤ 1 := by
  induction tree generalizing z with
  | stop => simp only [BetTree.hitProbability]; split_ifs <;> norm_num
  | node q A B win lose ihw ihl =>
    rcases h with ⟨hq0, hq1, _, _, _, hw, hl⟩
    simp only [BetTree.hitProbability]
    split_ifs
    · exact le_refl 1
    · have hw' := mul_le_mul_of_nonneg_left (ihw hw (z*A)) hq0
      have hl' := mul_le_mul_of_nonneg_left (ihl hl (z*B)) (sub_nonneg.mpr hq1)
      nlinarith

/-- For any finite adaptive tree, the probability of ever hitting threshold T
is at most starting wealth / T. Threshold checking includes the starting node
and every later node. Early stopped leaves are allowed at arbitrary depths. -/
theorem BetTree.finite_hitting_bound (tree : BetTree) (h : tree.Valid)
    (z T : ℝ) (hz : 0 ≤ z) (hT : 0 < T) :
    tree.hitProbability z T ≤ z / T := by
  induction tree generalizing z with
  | stop =>
    simp only [BetTree.hitProbability]
    split_ifs with hhit
    · exact (le_div_iff₀ hT).mpr (by simpa using hhit)
    · exact div_nonneg hz (le_of_lt hT)
  | node q A B win lose ihw ihl =>
    rcases h with ⟨hq0, hq1, hA, hB, hmean, hw, hl⟩
    simp only [BetTree.hitProbability]
    split_ifs with hhit
    · exact (le_div_iff₀ hT).mpr (by simpa using hhit)
    · have hw' := mul_le_mul_of_nonneg_left
        (ihw hw (z*A) (mul_nonneg hz hA)) hq0
      have hl' := mul_le_mul_of_nonneg_left
        (ihl hl (z*B) (mul_nonneg hz hB)) (sub_nonneg.mpr hq1)
      calc
        _ ≤ q * ((z * A) / T) + (1-q) * ((z * B) / T) := add_le_add hw' hl'
        _ = (z / T) * (q*A + (1-q)*B) := by ring
        _ ≤ (z / T) * 1 := mul_le_mul_of_nonneg_left hmean (div_nonneg hz (le_of_lt hT))
        _ = z / T := mul_one _

/-- The nodewise certificate can be discharged against an upper bound b on q,
rather than knowing q exactly. -/
theorem BetTree.valid_node_of_null_bound (q b A B : ℝ) (win lose : BetTree)
    (hq0 : 0 ≤ q) (hq1 : q ≤ 1) (hqb : q ≤ b)
    (hB : 0 ≤ B) (hBA : B ≤ A)
    (hcal : b*A + (1-b)*B ≤ 1) (hw : win.Valid) (hl : lose.Valid) :
    (BetTree.node q A B win lose).Valid := by
  exact ⟨hq0, hq1, hB.trans hBA, hB, local_factor_bound q b A B hqb hBA hcal, hw, hl⟩

theorem calibrated_biased_factors :
    (0 : ℝ) ≤ 3/5 ∧ 3/5 ≤ (57 : ℝ)/55 ∧
    (11/12 : ℝ) * (57/55) + (1-11/12) * (3/5) = 1 := by
  norm_num

theorem calibrated_uniform_factors :
    (0 : ℝ) ≤ 3/10 ∧ 3/10 ≤ (57 : ℝ)/50 ∧
    (5/6 : ℝ) * (57/50) + (1-5/6) * (3/10) = 1 := by
  norm_num

/-- Using the uniform calibration on the biased classical boundary gives an
expected factor strictly above one: it is not a valid null certificate. -/
theorem naive_biased_factor_invalid :
    (11/12 : ℝ) * (57/50) + (1-11/12) * (3/10) = (107 : ℝ)/100 := by
  norm_num

/-- The all-success 36-round prefix already crosses the nominal 1% threshold
for the naively uniform-calibrated test. -/
theorem naive_attack_prefix_crosses : (100 : ℝ) < (57/50 : ℝ)^36 := by
  norm_num

/-- Under the biased classical boundary that prefix has probability > 4.3%,
already larger than the claimed 1% type-I probability. IID here is an explicit
construction for a counterexample, not an assumption of the valid-tree theorem. -/
theorem naive_attack_prefix_probability : (43 : ℝ)/1000 < (11/12 : ℝ)^36 := by
  norm_num

theorem protected_attack_prefix_does_not_cross : (57/55 : ℝ)^36 < 100 := by
  norm_num

/-- A finite test that stops at the first loss or after n wins. This is an
explicit sequential counterexample tree, without any validity assumption. -/
def winPrefixTree : ℕ → ℝ → ℝ → ℝ → BetTree
  | 0, _, _, _ => .stop
  | n+1, q, A, B => .node q A B (winPrefixTree n q A B) .stop

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem concrete_naive_false_positive :
    (43 : ℝ)/1000 <
      (winPrefixTree 36 (11/12) (57/50) (3/10)).hitProbability 1 100 := by
  norm_num [winPrefixTree, BetTree.hitProbability]

theorem biased_unit_start_threshold (tree : BetTree) (h : tree.Valid)
    (T : ℝ) (hT : 0 < T) : tree.hitProbability 1 T ≤ 1/T :=
  tree.finite_hitting_bound h 1 T (by norm_num) hT

end Evidence
