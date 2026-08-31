# PatchProof AI Architecture

## Final selected policy

```text
Baseline candidate → deterministic semantic risk gate → optional Advanced verification/repair
```

The baseline produces a candidate patch from the issue, seed repository, and public tests. A deterministic risk gate then decides whether the candidate should be escalated. The gate makes zero LLM calls, uses no benchmark identifiers, and has no access to held-out tests.

## Advanced path

When escalation is warranted, PatchProof uses an evidence-gated workflow:

1. **Investigator** — diagnoses root cause from visible repository/test evidence.
2. **Patcher** — makes the smallest production-code change justified by the evidence.
3. **Independent Verifier** — tries to falsify the patch with a focused adversarial test.
4. **Repair** — one bounded repair attempt if the verifier exposes a real flaw.
5. **Post-repair Re-Verification** — a fresh verdict on repaired code, preventing stale-verdict decisions.
6. **Human checkpoint** — approval before accepting a consequential patch outside the sandbox.

## Sandbox and hidden-test isolation

Each case copies only `seed/` into an isolated temporary workspace. Held-out tests live in a sibling evaluator directory and execute only after the solving workflow returns. All model-visible file operations are path-bounded to the workspace.

## Trajectories

Structured JSONL events record model calls, tool observations, decisions, repair/re-verification paths, risk-gate reasoning, and final evaluator status. Representative trajectories are included with the submission.

## Design principle

The project deliberately rejects the assumption that more agents are automatically better. Every extra stage has to justify its cost and its own failure probability with measured evidence.
