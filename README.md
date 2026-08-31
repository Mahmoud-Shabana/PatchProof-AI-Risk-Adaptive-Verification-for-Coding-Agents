<div align="center">

# 🛡️ PatchProof AI

### Risk-Adaptive Verification for Coding Agents

**Evidence-gated software repair that verifies only when verification is worth the risk and cost.**

[![Author](https://img.shields.io/badge/Author-Mahmoud%20Shabana-0A66C2?style=for-the-badge&logo=github)](https://github.com/Mahmoud-Shabana)
![VRR](https://img.shields.io/badge/Final%20VRR-100%25%20%2822%2F22%29-success?style=for-the-badge)
![Unsafe Patches](https://img.shields.io/badge/Unsafe%20Patch%20Rate-0%25-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-gpt--oss%3A120b--cloud-black?style=for-the-badge)
![License](https://img.shields.io/badge/License-Hackathon%20Terms-orange?style=for-the-badge)

**micro1 Frontier Engineering Challenge 2026 — Agentic Workflows**

</div>

---

## ✨ What is PatchProof AI?

AI coding agents are fast, but a patch that *looks* correct can still be unsafe: it may pass visible tests while failing an unseen edge case, overfit the issue description, or be rejected by a verifier acting on stale evidence.

**PatchProof AI** is a reproducible agentic workflow for software maintainers reviewing AI-generated bug fixes. It evolved through measured experiments from a one-shot coding baseline, to always-on verification, to a **risk-adaptive policy** that verifies only when the expected safety gain justifies the verifier's own cost and failure risk.

```text
Issue + Repository + Public Tests
              │
              ▼
      ┌──────────────────┐
      │ Baseline Candidate│
      └────────┬─────────┘
               │
               ▼
      ┌──────────────────┐
      │ Deterministic    │  ← zero LLM calls
      │ Risk Gate        │
      └──────┬─────┬─────┘
             │     │
      low risk     precision / financial risk
             │     │
             ▼     ▼
        Accept    Diagnose → Verify → Repair → Re-Verify
             \                /
              \              /
               ▼            ▼
                 Final Patch
```

---

## 🏆 Headline Results

The final policy was evaluated across **22 frozen synthetic software-bug cases** using `gpt-oss:120b-cloud` via Ollama.

| Metric | Baseline | Always-on Advanced | **Risk-Adaptive Final** |
|---|---:|---:|---:|
| **Verified Resolution Rate** | 21/22 = **95.5%** | 21/22 = **95.5%** | **22/22 = 100%** |
| **Unsafe Patch Rate** | >0% on original benchmark | Regression observed on safety challenge | **0%** |
| **Relative token cost** | **1.00×** | ~**4×** | **1.39×** |
| Verification policy | None | Every task | **Selective / semantic risk gate** |

### Why the final result matters

- ✅ **22/22 verified resolutions**
- ✅ **0% unsafe patch rate**
- ✅ Solved the original `02_money_rounding` failure that the baseline missed
- ✅ Avoided the `C06_malformed_input` regression introduced by always-on verification
- ✅ Achieved the best observed correctness at only **1.39×** baseline token cost

> **Hot take:** More verification is not automatically more reliable. Verification is itself an agentic action that can fail, so the safest workflow verifies selectively where the expected safety gain exceeds the verifier's own failure risk.

---

## 👤 Intended User

**Software maintainers, reviewers, and engineering teams** who need to assess AI-generated bug fixes before trusting them.

### The bottleneck

A one-shot coding agent can produce a plausible patch that:

- passes public tests but fails held-out behavior,
- addresses the symptom instead of the root cause,
- introduces an edge-case regression,
- or gets rejected by a verifier whose judgment is based on code that has already changed.

PatchProof turns those failure modes into explicit, testable workflow decisions.

---

## 🧪 Evidence-Driven Evolution

PatchProof was not designed by assuming that “more agents = better.” Each iteration was driven by measured evidence.

### 1️⃣ Baseline — one coding agent

A general-purpose agent receives the issue, repository, and public tests, then makes one patch attempt.

**Original frozen benchmark:**

- Baseline: **9/10 = 90% VRR**
- Unsafe patch rate: **10%**

The unsafe failure was a numerical/financial rounding case that passed public tests but failed held-out behavior.

### 2️⃣ Advanced Iteration 0 — always-on verification

```text
Reproducer → Investigator → Patcher → Verifier → Repair
```

**Result:** **6/10 = 60% VRR**, but **0% unsafe patches**.

The verifier found real edge cases, yet the workflow still rejected repaired code because it reused a **stale pre-repair verdict**.

### 3️⃣ Iteration 1 — post-repair re-verification

The repair path was changed so that successfully repaired code receives a **fresh independent verdict**.

| Metric | Iteration 0 | Iteration 1 |
|---|---:|---:|
| Advanced VRR | 60% | **100%** |
| Change | — | **+40 percentage points** |
| Regressions | — | **0** |
| Token overhead vs Iter0 | — | **+16%** |

### 4️⃣ Frozen Safety Challenge Set — negative result that mattered

Twelve new cases were authored and frozen **before any model policy saw them**.

Blind result:

- Baseline: **12/12**
- Always-on Advanced: **11/12**

Always-on verification added cost and introduced a new regression. That negative result directly motivated the final design.

### 5️⃣ Final — Risk-Adaptive Verification

The final architecture first creates a baseline candidate, then applies a **deterministic semantic risk gate**.

The gate:

- makes **zero LLM calls**,
- never uses benchmark IDs,
- never sees hidden tests,
- routes only on clear numerical/financial precision semantics such as monetary calculation, decimal precision, or rounding behavior.

Only high-risk candidates enter the expensive verification/repair loop.

---

## 📏 Evaluation Methodology

### Primary metric — Verified Resolution Rate (VRR)

A case counts as resolved only when:

1. the workflow completes successfully,
2. all public tests pass, and
3. all held-out behavioral tests pass.

### Secondary metrics

- **Unsafe patch rate** — public tests pass but held-out tests fail
- **Model calls**
- **Token usage**
- **Runtime**

### Fairness controls

- Same model for compared policies
- Same seed repository
- Same issue description
- Same public tests
- Hidden tests are copied into a separate evaluator directory **only after the workflow returns**
- Solving agents cannot access hidden-test paths or contents
- Frozen evaluation artifacts are preserved in `artifacts/results/`

---

## 🧰 Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.11+ |
| Testing | pytest |
| Model endpoint | OpenAI-compatible Chat Completions |
| Final model | `gpt-oss:120b-cloud` |
| Runtime bridge | Ollama |
| Tracing | JSONL structured trajectories |
| Evaluation | deterministic public + held-out behavioral tests |

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/Mahmoud-Shabana/PatchProof-AI-Risk-Adaptive-Verification-for-Coding-Agents.git
cd PatchProof-AI-Risk-Adaptive-Verification-for-Coding-Agents
```

### 2. Create an environment

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install

```bash
pip install -e .
```

### 4. Configure Ollama Cloud

```powershell
$env:PATCHPROOF_API_URL="http://localhost:11434/v1/chat/completions"
$env:PATCHPROOF_API_KEY="ollama"
$env:PATCHPROOF_MODEL="gpt-oss:120b-cloud"
```

Linux/macOS:

```bash
export PATCHPROOF_API_URL="http://localhost:11434/v1/chat/completions"
export PATCHPROOF_API_KEY="ollama"
export PATCHPROOF_MODEL="gpt-oss:120b-cloud"
```

### 5. Validate benchmarks

```bash
python evaluation/validate_benchmark.py
python evaluation/validate_challenge_set.py
```

See **[REPRODUCTION.md](REPRODUCTION.md)** for exact benchmark and policy commands.

---

## 📂 Repository Map

```text
PatchProof AI/
├── src/patchproof/                 # workflow, provider, sandbox, tracing
├── prompts/                        # agent instructions
├── tests/                          # workflow regression tests
├── benchmark/
│   ├── cases/                      # original frozen benchmark
│   └── challenge_set/              # blind safety challenge set
├── evaluation/                     # validation, scoring, reports
├── artifacts/
│   ├── results/                    # frozen machine-readable results
│   └── submission_trajectories/    # representative agent trajectories
├── FINAL_RESULTS.md
├── CHANGELOG.md
├── REPRODUCTION.md
├── ARCHITECTURE.md
└── VIDEO_SCRIPT.md
```

---

## 🔎 Representative Agent Trajectories

The submission includes raw JSONL trajectories showing:

1. straightforward baseline success,
2. unsafe baseline money-rounding failure,
3. Iteration 0 stale-verdict failure,
4. Iteration 1 repair + fresh re-verification success,
5. adaptive escalation on a precision-sensitive task,
6. adaptive non-escalation on malformed input.

See **[`artifacts/submission_trajectories/TRAJECTORY_INDEX.md`](artifacts/submission_trajectories/TRAJECTORY_INDEX.md)**.

---

## 📊 Results & Reproducibility

- **[FINAL_RESULTS.md](FINAL_RESULTS.md)** — benchmark tables and final metrics
- **[CHANGELOG.md](CHANGELOG.md)** — evidence → experiment → result → decision
- **[REPRODUCTION.md](REPRODUCTION.md)** — clean-environment commands
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — system design and workflow gates
- **[VIDEO_SCRIPT.md](VIDEO_SCRIPT.md)** — ≤5-minute demo narrative

---

## ⚠️ Limitations

- The final risk gate currently recognizes an evidence-derived **numerical/financial precision** risk class; broader routing requires further evaluation.
- Benchmarks are synthetic and intentionally small enough for deterministic reproduction.
- LLM behavior remains nondeterministic even with temperature minimized.
- The final adaptive evaluation is **post-evidence**, not blind; the 12-case Safety Challenge is the separately frozen blind evaluation.

---

## 👨‍💻 Author & Ownership Notice

<div align="center">

### **Mahmoud Shabana**

**Creator • Engineer • Researcher**

[![GitHub](https://img.shields.io/badge/GitHub-Mahmoud--Shabana-181717?style=for-the-badge&logo=github)](https://github.com/Mahmoud-Shabana)

**Copyright © 2026 Mahmoud Shabana.**

This project was created for the **micro1 Frontier Engineering Challenge 2026**. Copyright, submission ownership, and permitted use are additionally subject to the applicable hackathon participation agreement and third-party component licenses. See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).

</div>

---

## 📜 License

This repository is distributed under the project-specific terms in **[LICENSE](LICENSE)**. The notice preserves authorship and makes clear that challenge-submission rights remain subject to the micro1 participation agreement.

---

<div align="center">

### 🛡️ Patch plausible code. **Prove trustworthy code.**

Built by **Mahmoud Shabana** • 2026

</div>
