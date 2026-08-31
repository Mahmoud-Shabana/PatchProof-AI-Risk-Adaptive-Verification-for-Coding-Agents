from __future__ import annotations
import json
import time
import uuid
from .paths import ARTIFACTS_DIR


class Trace:
    def __init__(self, case_id: str, mode: str):
        out = ARTIFACTS_DIR / "trajectories"
        out.mkdir(parents=True, exist_ok=True)
        self.path = out / f"{case_id}-{mode}-{uuid.uuid4().hex[:8]}.jsonl"

    def add(self, kind: str, **payload):
        record = {"ts": time.time(), "kind": kind, **payload}
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
