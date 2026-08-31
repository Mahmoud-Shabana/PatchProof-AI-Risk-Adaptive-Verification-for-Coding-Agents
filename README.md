# PatchProof AI

**One-line description:**
An evidence-gated coding-agent workflow that verifies selectively when the expected safety gain justifies the verifier's own cost and failure risk.

## The User
Software maintainers reviewing AI-generated bug fixes who need rigorous, autonomous validation without wasting time or money on over-verified simple fixes.

## The Bottleneck
A one-shot coding agent can produce a plausible patch that passes visible tests but fails an unseen edge case.

## Baseline
One general-purpose coding agent given:
* The same model
* Issue description
* Repository context
* Public tests
* One patch attempt

## Advanced Iteration 0
The initial advanced workflow pipeline:
`Reproducer → Investigator → Patcher → Verifier → Repair`

**Frozen Results (Original 10-Case Benchmark):**
* **Baseline**: 9/10 = 90%
* **Advanced Iter0**: 6/10 = 60%
* **Baseline unsafe patch rate**: 10%
* **Advanced unsafe patch rate**: 0%

**The Stale-Verdict Failure**: Advanced Iter0 suffered from a logical flaw where the final verification decision used the verifier's *initial* rejection (pre-repair). If a repair succeeded, the system still failed the patch because it relied on a stale verdict about code that no longer existed.

## Iteration 1
Introduced **post-repair re-verification**:
If a repair is attempted and passes all tests, a fresh, independent verifier evaluates the repaired code.

**Results:**
* **Advanced Iter0**: 60%
* **Advanced Iter1**: 100% (+40 percentage points, 0 regressions)
* Cost: +16% tokens versus Iter0 Advanced

## Safety Challenge Set
To stress-test the system, 12 new cases designed to provoke silent correctness failures were authored and frozen *before* either model policy was run.

**Blind Evaluation Results (12 Cases):**
* **Baseline**: 12/12 (100%)
* **Always-on Advanced**: 11/12 (91.7%)

**Takeaway**: Always-on verification added massive cost without measurable benefit on this set and actually *caused* one regression by hallucinating an overly strict, invalid test.

## Final Adaptive Solution
**Architecture:**
`Baseline candidate → deterministic risk gate → optional advanced verification/repair`

**How it works:**
* The risk gate makes **zero LLM calls**.
* It uses **no benchmark IDs** and **no hidden tests**.
* It routes based purely on **semantic numerical/financial precision signals** (e.g., "monetary", "financial calculations", "decimal precision", "rounding semantics") in the issue and context.

**Final 22-Case Evaluation (Original + Challenge):**
* **Adaptive VRR**: 22/22 = 100%
* **Baseline overall**: 21/22
* Adaptive solved original `02_money_rounding`
* Adaptive avoided the `C06_malformed_input` regression
* **Adaptive cost**: 1.39× Baseline
* **Always-on Advanced cost**: ~3.96× Baseline (approximately 4×)

## Primary Metric
**Verified Resolution Rate (VRR)**: The percentage of cases where the workflow proposes a patch that passes all public tests *and* all hidden tests.

## Secondary Metrics
* **Unsafe patch rate**: Patches that pass public tests but fail hidden tests.
* **Tokens**: Total LLM token usage.
* **Model calls**: Number of LLM invocations.
* **Runtime**: Total execution time in seconds.

## Reproduction
Exact commands from a clean environment:
```bash
git clone <repo_url> patchproof-ai
cd patchproof-ai
pip install -r requirements.txt
export PATCHPROOF_API_URL="http://localhost:11434/v1/chat/completions"
export PATCHPROOF_API_KEY="ollama"
export PATCHPROOF_MODEL="gpt-oss:120b-cloud"

# Run final evaluation across all 22 cases
python evaluation/run_benchmark.py --mode matrix --all-cases --auto-approve
```
See `REPRODUCTION.md` for full details.

## Main Failure Mode
Verifiers themselves can introduce failures or stale judgments.

## Hot Take
**More verification is not automatically more reliable.** Verification is itself an agentic action that can fail, so the safest workflow verifies selectively where the expected safety gain exceeds the verifier's own failure risk.
