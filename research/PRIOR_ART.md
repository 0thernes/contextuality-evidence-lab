# Prior art and claim boundary

Search date: 10 November 2026. Scope: a bounded primary-source review supporting an executable methods paper. This is not an exhaustive literature review, a historical-priority proof, or a statistical meta-analysis.

## Question investigated

Can a small contextuality experiment carry an exact certificate for its sequential statistical interpretation, including an explicit setting-bias attack and a bound that remains valid under adaptive classical memory?

The research target was deliberately narrowed after checking prior work. Optimizing contextuality inequalities, using products of nonnegative test factors, and controlling repeated examination with supermartingales are established methods. The contribution of this repository is their concrete, auditable integration with a finite formal model and actual software execution.

## Search record

Queries included:

- `contextuality inequalities optimal noise robust weighted Peres Mermin square context sampling statistical tests martingale`
- `optimal quantum contextuality inequalities linear programming experimental imperfections`
- `contextuality sequential statistical hypothesis testing memory loophole martingale`
- `prediction based ratio test quantum contextuality hypothesis testing noncontextuality`
- `contextuality statistical significance optimal measurement allocation Peres Mermin memory loophole`
- `Lean formally verified e-process martingale Bell inequalities contextuality`
- `Lean formalization prediction based ratio hypothesis testing quantum contextuality`
- `contextuality measurement dependence nonuniform context probabilities Peres Mermin`

General web search supplied candidate records. The paper's scholarly references were checked against the primary article or author-hosted record. Search results, scraped dates, and repository descriptions were not treated as proof of mathematical correctness.

## Primary sources inspected

| Source | Material inspected | Relevance and effect on claims |
|---|---|---|
| N. D. Mermin, *Simple unified form for the major no-hidden-variables theorems*, Physical Review Letters 65, 3373–3376 (1990), [DOI](https://doi.org/10.1103/PhysRevLett.65.3373) | Publisher metadata and abstract; the local argument is independently derived and checked | The square is established quantum-foundations mathematics, not a new construction. |
| Y. Zhang, S. Glancy, E. Knill, *Asymptotically optimal data analysis for rejecting local realism*, Physical Review A 84, 062118 (2011), [primary full text](https://arxiv.org/html/1108.2468v2) | Sections II.3 and III.3, with setting-distribution assumptions | Prediction-based ratios and adaptation to past data are prior art. Our simple Bernoulli factors are a specialization, not an invention of sequential evidence. |
| M. Kleinmann, C. Budroni, J.-Å. Larsson, O. Gühne, A. Cabello, *Optimal inequalities for state-independent contextuality*, Physical Review Letters 109, 250402 (2012), [primary full text](https://arxiv.org/html/1204.3741v2) | Linear-program formulation and experimental discussion | A new claim that linear optimization of contextuality witnesses is unprecedented would be false. |
| A. Krishna, R. W. Spekkens, E. Wolfe, *Deriving robust noncontextuality inequalities from algebraic proofs of the Kochen–Specker theorem: the Peres–Mermin square*, New Journal of Physics 19, 123031 (2017), [primary full text](https://arxiv.org/html/1704.01153v2) | Introduction, operational formulation, conclusions, Appendix D | A deterministic value-assignment test is not automatically a test of all generalized-noncontextual models with noisy measurements. This limitation is explicit throughout the paper. |
| S. R. Howard, A. Ramdas, J. McAuliffe, J. Sekhon, *Time-uniform Chernoff bounds via nonnegative supermartingales*, Probability Surveys 17, 257–317 (2020), [DOI](https://doi.org/10.1214/18-PS321), [author manuscript](https://arxiv.org/html/1808.03204v6) | Section 2.3, Lemma 1 and its role in threshold crossing | Ville's inequality is established. The inspected manuscript version displays the title *Exponential line-crossing inequalities*; the reference uses the journal title. |
| K. Ying, R. Degenne, *A Formalization of Doob's Martingale Convergence Theorems in mathlib* (2022), [primary record](https://arxiv.org/abs/2212.05578) | Author abstract and scope | Formal probability and martingale theory in Lean predate this repository. The finite-tree proof is a small specialized certificate, not the first formalization of martingales. |

An additional source-code search located [formal-martingales' Ville documentation](https://github.com/Robby955/formal-martingales/blob/main/docs/ville.md) and [FormalSLT's e-process module](https://github.com/Robby955/FormalSLT/blob/main/FormalSLT/AnytimeValid/EProcess.lean). These external projects were not built or audited here. Their existence is another reason not to assert a first-ever Lean e-process result.

## Local prior work inspected

The existing Contextuality Tensor Lab README, formal boundary, manuscript and frontier review were read. They concern exact contextuality degrees for disjoint-copy families and their readout-noise thresholds. The Hoggar Bound Lab summary was also read. It concerns spectral bounds, saturation cases, and completion spectra. This project does not extend their degree records or independently revalidate every claim in those studies. It adds an experiment-analysis layer with a different theorem boundary.

## Negative results and choices

1. **No novelty claim for the broad method.** The search found established antecedents for every broad mathematical ingredient.
2. **No claim of solving an open foundational problem.** The classical floor bound and the finite-tree argument are elementary consequences of their assumptions.
3. **No certificate of physical randomness.** A deterministic software mixer can exercise the execution pipeline but cannot establish a conditional setting-probability floor against an observer knowing its state.
4. **No generalized-noncontextuality claim from readout-noise injection.** The tested null is specified deterministic context-independent value assignments, with mixtures and adaptive inter-trial memory. Context-dependent disturbance is outside that null.
5. **No statistical meta-analysis.** No eligible set of independent empirical studies was pooled; there is no estimated pooled effect, heterogeneity statistic, or publication-bias analysis.

## Defensible contribution statement

This repository supplies a reproducible contextuality evidence benchmark: exact finite-game bounds, a formal finite-horizon threshold-crossing argument, a constructive biased-setting counterexample, exact replay of finite traces, and a disclosed four-component software experiment. It is a new project artifact and a concrete formalization/application. A claim of historical mathematical priority would require a substantially broader specialist review.
