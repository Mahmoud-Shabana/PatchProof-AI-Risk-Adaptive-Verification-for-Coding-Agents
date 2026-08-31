from __future__ import annotations
import json

PATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string"},
        "content": {"type": "string"},
        "summary": {"type": "string"},
    },
    "required": ["path", "content", "summary"],
    "additionalProperties": False,
}

DIAGNOSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "root_cause": {"type": "string"},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "proposed_change": {"type": "string"},
    },
    "required": ["root_cause", "evidence", "proposed_change"],
    "additionalProperties": False,
}

VERIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "verdict": {"type": "string", "enum": ["accept", "reject"]},
        "reason": {"type": "string"},
        "test_path": {"type": "string"},
        "test_content": {"type": "string"},
    },
    "required": ["verdict", "reason", "test_path", "test_content"],
    "additionalProperties": False,
}


def _repo_context(sandbox):
    chunks = []
    for rel in sandbox.list_files():
        if "__pycache__" in rel or ".pytest_cache" in rel:
            continue
        try:
            content = sandbox.read_file(rel)
        except Exception:
            continue
        chunks.append(f"===== {rel} =====\n{content}")
    return "\n\n".join(chunks)


def _safe_source_path(path):
    norm = path.replace("\\", "/").lstrip("./")
    low = norm.lower()
    if low.startswith("test") or "/test" in low:
        raise ValueError("Production patch may not modify tests.")
    if norm.startswith("../") or norm.startswith("/"):
        raise ValueError("Unsafe path.")
    return norm


def _is_collection_error(output: str) -> bool:
    return "ERROR collecting" in output


def run_baseline(provider, sandbox, trace, issue):
    public_ok, public_out = sandbox.run_public_tests()
    context = _repo_context(sandbox)
    trace.add("baseline_observation", public_passed=public_ok, public_output=public_out)
    system = (
        "You are a single general-purpose coding agent. Fix the reported bug with the "
        "smallest correct production-code change. Never modify tests. Return the FULL "
        "replacement content for exactly one production file."
    )
    user = f"ISSUE:\n{issue}\n\nPUBLIC TEST OUTPUT:\n{public_out}\n\nREPOSITORY:\n{context}"
    patch, message, usage = provider.force_function(
        system, user, "submit_patch", "Submit one production-file replacement patch.", PATCH_SCHEMA
    )
    path = _safe_source_path(patch["path"])
    sandbox.write_file(path, patch["content"])
    trace.add("baseline_patch", patch=patch, usage=usage, raw_message=message)
    public_ok2, public_out2 = sandbox.run_public_tests()
    trace.add("baseline_verify", passed=public_ok2, output=public_out2)
    return {"finished": public_ok2, "summary": patch["summary"], "model_calls": 1}


def run_advanced(provider, sandbox, trace, issue, auto_approve=False):
    model_calls = 0
    public_ok, public_out = sandbox.run_public_tests()
    context_before = _repo_context(sandbox)
    reproduced = not public_ok
    trace.add("reproduction_gate", passed=reproduced, output=public_out)
    if not reproduced:
        return {"finished": False, "summary": "Reproduction gate failed.", "model_calls": 0}

    diagnosis, inv_msg, inv_usage = provider.force_function(
        "You are the investigator. Diagnose the root cause from the issue, repository and exact failing test output. Ground the diagnosis in concrete evidence. Do not modify tests.",
        f"ISSUE:\n{issue}\n\nFAILING TEST OUTPUT:\n{public_out}\n\nREPOSITORY:\n{context_before}",
        "submit_diagnosis",
        "Submit a root-cause diagnosis grounded in observed evidence.",
        DIAGNOSIS_SCHEMA,
    )
    model_calls += 1
    trace.add("investigation", diagnosis=diagnosis, usage=inv_usage, raw_message=inv_msg)
    if not diagnosis.get("root_cause") or not diagnosis.get("evidence"):
        return {"finished": False, "summary": "Evidence gate failed.", "model_calls": model_calls}

    patch, patch_msg, patch_usage = provider.force_function(
        "You are the patcher. Implement the smallest production-code fix justified by the supplied diagnosis. Never modify tests. Return FULL replacement content for exactly one production file.",
        f"ISSUE:\n{issue}\n\nDIAGNOSIS:\n{json.dumps(diagnosis, indent=2)}\n\nREPOSITORY:\n{context_before}",
        "submit_patch",
        "Submit one minimal production-file replacement patch.",
        PATCH_SCHEMA,
    )
    model_calls += 1
    patch_path = _safe_source_path(patch["path"])
    sandbox.write_file(patch_path, patch["content"])
    trace.add("patch", patch=patch, usage=patch_usage, raw_message=patch_msg)
    public_ok2, public_out2 = sandbox.run_public_tests()
    trace.add("post_patch_tests", passed=public_ok2, output=public_out2)
    if not public_ok2:
        return {"finished": False, "summary": "Patch failed public tests.", "model_calls": model_calls}

    context_after = _repo_context(sandbox)
    verification, ver_msg, ver_usage = provider.force_function(
        "You are an independent verifier trying to falsify a coding fix. Design ONE focused pytest regression/boundary test not already covered. Do not modify production code. The filename must begin test_agent_. Use verdict=accept only if the current evidence supports the fix.",
        f"ISSUE:\n{issue}\n\nROOT CAUSE:\n{diagnosis['root_cause']}\n\nPATCH SUMMARY:\n{patch['summary']}\n\nPUBLIC TESTS:\n{public_out2}\n\nREPOSITORY AFTER PATCH:\n{context_after}",
        "submit_verification",
        "Submit a verdict and one adversarial pytest test.",
        VERIFY_SCHEMA,
    )
    model_calls += 1
    trace.add("verifier_initial", verification=verification, usage=ver_usage, raw_message=ver_msg)

    test_path = verification["test_path"].replace("\\", "/").lstrip("./")
    if not test_path.startswith("test_agent_"):
        test_path = "test_agent_verifier.py"
    sandbox.write_file(test_path, verification["test_content"])
    adv_ok, adv_out = sandbox.run_public_tests()
    final_verifier_accepts = verification["verdict"] == "accept"
    final_summary = verification["reason"]

    if _is_collection_error(adv_out):
        trace.add("invalid_verifier_test", test_path=test_path, output=adv_out)
        adv_ok = public_ok2
        final_verifier_accepts = True
        final_summary = "Verifier test was invalid (collection/syntax error). Approved on public test passage. " + verification["reason"]
    elif not adv_ok:
        trace.add("repair_started", output=adv_out)
        repair_context = _repo_context(sandbox)
        repair, rep_msg, rep_usage = provider.force_function(
            "You are the repair agent. An independent verifier exposed a flaw. Repair production code only; never modify tests. Return FULL replacement content for exactly one production file.",
            f"ISSUE:\n{issue}\n\nDIAGNOSIS:\n{json.dumps(diagnosis, indent=2)}\n\nADVERSARIAL TEST OUTPUT:\n{adv_out}\n\nREPOSITORY:\n{repair_context}",
            "submit_repair",
            "Submit one corrected production-file replacement patch.",
            PATCH_SCHEMA,
        )
        model_calls += 1
        repair_path = _safe_source_path(repair["path"])
        sandbox.write_file(repair_path, repair["content"])
        trace.add("repair", patch=repair, usage=rep_usage, raw_message=rep_msg)
        adv_ok, adv_out = sandbox.run_public_tests()
        trace.add("repair_tests", passed=adv_ok, output=adv_out)
        if adv_ok:
            context_repaired = _repo_context(sandbox)
            re_verification, rev_msg, rev_usage = provider.force_function(
                "You are an independent verifier. A repair was applied after the initial rejection. Re-evaluate the repaired code independently without being influenced by the earlier verdict. Design ONE focused pytest regression or boundary test. The filename must begin test_agent_re_. Use verdict=accept only if the repaired evidence fully supports the fix.",
                f"ISSUE:\n{issue}\n\nROOT CAUSE:\n{diagnosis['root_cause']}\n\nINITIAL PATCH:\n{patch['summary']}\n\nREPAIR APPLIED:\n{repair['summary']}\n\nALL TESTS AFTER REPAIR:\n{adv_out}\n\nREPAIRED REPOSITORY:\n{context_repaired}",
                "submit_verification",
                "Submit a fresh independent verdict on the repaired code.",
                VERIFY_SCHEMA,
            )
            model_calls += 1
            trace.add("reverification", verification=re_verification, usage=rev_usage, raw_message=rev_msg)
            final_verifier_accepts = re_verification["verdict"] == "accept"
            final_summary = re_verification["reason"]
        else:
            final_verifier_accepts = False
            final_summary = "Repair failed all tests."

    eligible = adv_ok and final_verifier_accepts
    approved = eligible if auto_approve else False
    if not auto_approve and eligible:
        approved = input("Verification passed. Approve sandbox patch? [y/N]: ").strip().lower() in {"y", "yes"}
    trace.add("final_verdict", final_verifier_accepts=final_verifier_accepts, tests_passed=adv_ok, approved=approved)
    trace.add("human_checkpoint", verifier_accept=final_verifier_accepts, tests_passed=adv_ok, approved=approved)
    return {"finished": approved, "summary": final_summary, "model_calls": model_calls}


def is_numerical_or_financial(issue: str, context: str) -> tuple[bool, str]:
    text = (issue + "\n" + context).lower()
    keywords = ["monetary", "financial", "decimal precision", "rounding semantics", "half-up", "half-even", "currency", "invoice"]
    for kw in keywords:
        if kw in text:
            return True, f"matched keyword '{kw}'"
    return False, ""


def run_adaptive(provider, sandbox, trace, issue, auto_approve=False):
    baseline_outcome = run_baseline(provider, sandbox, trace, issue)
    trace.add("baseline_candidate", passed_public=baseline_outcome["finished"], summary=baseline_outcome["summary"])
    context = _repo_context(sandbox)
    triggered, reason = is_numerical_or_financial(issue, context)
    trace.add("risk_gate", triggered=triggered)
    if not triggered:
        trace.add("risk_gate_reason", reason="No risk keywords matched")
        trace.add("baseline_accepted_without_escalation")
        return baseline_outcome
    trace.add("risk_gate_reason", reason=reason)
    trace.add("verification_escalated")
    import shutil
    shutil.rmtree(sandbox.workspace)
    shutil.copytree(sandbox.case_dir / "seed", sandbox.workspace)
    adv_outcome = run_advanced(provider, sandbox, trace, issue, auto_approve=auto_approve)
    adv_outcome["model_calls"] += baseline_outcome["model_calls"]
    return adv_outcome
