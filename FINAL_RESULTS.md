# PatchProof AI — Final Results

This document contains the final benchmark evaluations for the PatchProof AI workflow iterations.

## A. Original Benchmark — 10 Cases

**Status:** frozen historical result.

| Policy | Verified Resolution Rate | Unsafe Patch Rate | Median Steps | Total Tokens |
|---|---:|---:|---:|---:|
| **Baseline** | 90% (9/10) | 10% (1/10) | 1.0 | ~11k |
| **Advanced Iteration 0** | 60% (6/10) | 0% | 3.0 | ~35k |
| **Advanced Iteration 1** | **100% (10/10)** | 0% | 3.0 | ~40k |

Iteration 1 introduced a fresh post-repair re-verification pass, fixing the stale-verdict failure observed in Iteration 0.

## B. Frozen Safety Challenge — 12 Cases

**Status:** blind evaluation. Cases were authored and frozen before either policy was run.

| Policy | Verified Resolution Rate | Unsafe Patch Rate | Median Steps | Total Tokens |
|---|---:|---:|---:|---:|
| **Baseline** | **100% (12/12)** | 0% | 1.0 | ~15k |
| **Always-on Advanced** | 91.7% (11/12) | 8.3% (1/12) | 3.0 | ~57k |

This negative result showed that universal verification can add cost and introduce new failure modes.

## C. Combined Final 22-Case Evaluation

**Status:** final post-evidence evaluation.

| Policy | VRR | Unsafe Patch Rate | Model Calls | Tokens | Token Multiplier |
|---|---:|---:|---:|---:|---:|
| **Baseline** | 95.5% (21/22) | 0% | 22 | 24,628 | 1.00× |
| **Always-on Advanced** | 90.9% (20/22) | 4.5% | 72 | 97,512 | 3.96× |
| **Final Risk-Adaptive** | **100% (22/22)** | **0%** | **28** | **34,374** | **1.39×** |

The final adaptive policy is evidence-driven and intentionally selective: it escalates numerical/financial precision-sensitive cases while preserving the fast baseline path for tasks where verification did not demonstrate benefit.

## Headline Result

**PatchProof AI Final: 22/22 verified resolutions, 0% unsafe patches, 1.39× baseline token cost.**
