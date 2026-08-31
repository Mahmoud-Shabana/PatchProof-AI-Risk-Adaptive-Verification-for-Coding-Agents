from pathlib import Path
from dataclasses import asdict
import argparse
import json
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from patchproof.runner import run_case

ALL_MODES = ["baseline", "v1_reproduce", "v2_evidence", "advanced", "adaptive"]


def summarize(results, mode):
    rows = [r for r in results if r["mode"] == mode]
    if not rows:
        return None
    solved = sum(bool(r["verified_resolved"]) for r in rows)
    public_pass = [r for r in rows if r["public_passed"]]
    unsafe = sum(not r["hidden_passed"] for r in public_pass)
    return {
        "mode": mode,
        "cases": len(rows),
        "verified": solved,
        "vrr": solved / len(rows),
        "unsafe_patch_rate": (unsafe / len(public_pass)) if public_pass else 0.0,
        "median_steps": statistics.median(r["steps"] for r in rows),
        "median_runtime_seconds": statistics.median(r["duration_seconds"] for r in rows),
        "total_tokens": sum(r.get("total_tokens", 0) for r in rows),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=ALL_MODES + ["both", "matrix"], default="both")
    p.add_argument("--auto-approve", action="store_true")
    p.add_argument("--case", default=None)
    p.add_argument("--tag", default="")
    p.add_argument("--challenge-set", action="store_true")
    p.add_argument("--all-cases", action="store_true")
    args = p.parse_args()

    if args.mode == "both":
        modes = ["baseline", "advanced"]
    elif args.mode == "matrix":
        modes = ["baseline", "advanced", "adaptive"]
    else:
        modes = [args.mode]

    if args.all_cases:
        roots = [ROOT / "benchmark" / "cases", ROOT / "benchmark" / "challenge_set" / "cases"]
    else:
        roots = [ROOT / "benchmark" / "challenge_set" / "cases" if args.challenge_set else ROOT / "benchmark" / "cases"]

    results = []
    for current_root in roots:
        for case_dir in sorted(current_root.iterdir()):
            if not case_dir.is_dir():
                continue
            if args.case and case_dir.name != args.case:
                continue
            for mode in modes:
                print(f"Running {case_dir.name} [{mode}] ...", flush=True)
                result = run_case(case_dir, mode, auto_approve=args.auto_approve)
                results.append(asdict(result))
                print(f"  verified={result.verified_resolved} public={result.public_passed} hidden={result.hidden_passed} steps={result.steps} tokens={result.total_tokens}")

    outdir = ROOT / "artifacts" / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    tag = f"-{args.tag}" if args.tag else ""
    results_path = outdir / f"benchmark-results{tag}.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    summaries = [s for s in (summarize(results, m) for m in modes) if s]
    summary_path = outdir / f"benchmark-summary{tag}.json"
    summary_path.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    for s in summaries:
        print(f"{s['mode']}: VRR={s['verified']}/{s['cases']}={s['vrr']:.1%}; unsafe={s['unsafe_patch_rate']:.1%}; median_steps={s['median_steps']}; tokens={s['total_tokens']}")
    print(f"Saved {results_path}")
    print(f"Saved {summary_path}")


if __name__ == "__main__":
    main()
