from __future__ import annotations
from pathlib import Path
import json
import time

from .sandbox import Sandbox
from .tracing import Trace
from .providers.openai_compatible import OpenAICompatibleProvider
from .models import RunResult
from .deterministic import run_baseline, run_advanced, run_adaptive


def load_case(case_dir):
    return json.loads((case_dir / "case.json").read_text(encoding="utf-8"))


def run_case(case_dir, mode, auto_approve=False):
    case_dir = case_dir.resolve()
    meta = load_case(case_dir)
    sandbox = Sandbox(case_dir)
    trace = Trace(meta["id"], mode)
    provider = OpenAICompatibleProvider()
    start = time.time()
    try:
        if mode == "baseline":
            outcome = run_baseline(provider, sandbox, trace, meta["issue"])
        elif mode in ("advanced", "v1_reproduce", "v2_evidence"):
            outcome = run_advanced(provider, sandbox, trace, meta["issue"], auto_approve)
        elif mode == "adaptive":
            outcome = run_adaptive(provider, sandbox, trace, meta["issue"], auto_approve)
        else:
            raise ValueError("unsupported PatchProof mode")

        patch_diff = sandbox.unified_diff()
        public_ok, public_out = sandbox.run_public_tests()
        hidden_ok, hidden_out = sandbox.run_hidden_tests()
        trace.add(
            "final_evaluation",
            public_passed=public_ok,
            hidden_passed=hidden_ok,
            public_output=public_out,
            hidden_output=hidden_out,
            token_usage=provider.usage_totals,
            patch_diff=patch_diff,
        )
        verified = bool(outcome["finished"] and public_ok and hidden_ok)
        return RunResult(
            case_id=meta["id"], mode=mode, public_passed=public_ok,
            hidden_passed=hidden_ok, verified_resolved=verified,
            steps=int(outcome.get("model_calls", 0)),
            duration_seconds=round(time.time() - start, 3),
            trajectory_path=str(trace.path), patch_path=str(trace.path),
            outcome_summary=outcome.get("summary", ""),
            prompt_tokens=provider.usage_totals["prompt_tokens"],
            completion_tokens=provider.usage_totals["completion_tokens"],
            total_tokens=provider.usage_totals["total_tokens"],
        )
    finally:
        sandbox.close()
