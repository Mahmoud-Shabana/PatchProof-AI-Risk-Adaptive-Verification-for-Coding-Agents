# Final Improvement Changelog

| Stage | Hypothesis / Change | Evidence | Result | Decision |
|---|---|---|---|---|
| **Baseline** | A single general-purpose coding agent may be sufficient for many bugs. | Original frozen 10-case benchmark. | 9/10 VRR; one unsafe financial-rounding patch. | Keep as the fast default and comparison point. |
| **Advanced Iteration 0** | Always-on investigation + verification + repair should improve safety. | Same frozen benchmark. | 6/10 VRR; 0% unsafe patches. | Reject as-is and inspect trajectories. |
| **Stale-verdict discovery** | Repairs were being judged by an old pre-repair verifier decision. | Cases 01, 03, 06 showed successful repair with final rejection. | Identified a state-machine defect. | Add fresh post-repair verification. |
| **Iteration 1** | Re-verifying repaired code should remove stale decisions. | Advanced-only rerun on same 10 cases. | 60% → 100% VRR; 0 regressions; +16% tokens vs Iter0 Advanced. | Accept as improved Advanced workflow. |
| **Safety Challenge** | A harder frozen set is needed because baseline already scored 90%. | 12 new cases authored before model execution. | Blind result: Baseline 12/12; Advanced 11/12. | Always-on verification is not generally beneficial. |
| **Rejected: always-on verification** | More verification should always mean more reliability. | Blind challenge contradicted the hypothesis. | Added ~4× cost and caused a regression. | Reject universal escalation. |
| **Final Risk-Adaptive Policy** | Verify only where measured safety gain exceeds verifier failure risk. | Deterministic zero-LLM numerical/financial risk gate; combined 22-case evaluation. | **22/22 VRR, 0% unsafe, 1.39× baseline tokens.** | **Final selected solution.** |

## Main lesson

Verification is not free evidence. It is another agentic action with its own failure modes, so its value has to be measured rather than assumed.
