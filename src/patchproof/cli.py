import argparse
import json
from pathlib import Path
from dataclasses import asdict
from .runner import run_case


def main():
    p = argparse.ArgumentParser(description="Run one PatchProof benchmark case.")
    p.add_argument("--case", required=True)
    p.add_argument("--mode", choices=["baseline", "v1_reproduce", "v2_evidence", "advanced", "adaptive"], required=True)
    p.add_argument("--auto-approve", action="store_true")
    args = p.parse_args()
    result = run_case(Path(args.case), args.mode, auto_approve=args.auto_approve)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
