from __future__ import annotations
from pathlib import Path
import difflib
import os
import shutil
import subprocess
import tempfile


class Sandbox:
    def __init__(self, case_dir: Path):
        self.case_dir = case_dir.resolve()
        self._tmp = Path(tempfile.mkdtemp(prefix="patchproof_")).resolve()
        self.workspace = self._tmp / "workspace"
        shutil.copytree(self.case_dir / "seed", self.workspace)

    def close(self):
        shutil.rmtree(self._tmp, ignore_errors=True)

    def _safe(self, rel: str) -> Path:
        p = (self.workspace / rel).resolve()
        if self.workspace not in p.parents and p != self.workspace:
            raise ValueError("Path escapes sandbox")
        return p

    def list_files(self) -> list[str]:
        return sorted(
            str(p.relative_to(self.workspace)).replace("\\", "/")
            for p in self.workspace.rglob("*")
            if p.is_file() and ".pytest_cache" not in p.parts and "__pycache__" not in p.parts
        )

    def read_file(self, rel: str) -> str:
        return self._safe(rel).read_text(encoding="utf-8")

    def write_file(self, rel: str, content: str):
        p = self._safe(rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        for cache in self.workspace.rglob("__pycache__"):
            shutil.rmtree(cache, ignore_errors=True)

    @staticmethod
    def _test_env(extra=None):
        return {
            **os.environ,
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            **(extra or {}),
        }

    def run_public_tests(self) -> tuple[bool, str]:
        proc = subprocess.run(
            ["python", "-m", "pytest", "-q"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            timeout=30,
            env=self._test_env(),
        )
        return proc.returncode == 0, (proc.stdout + "\n" + proc.stderr).strip()

    def run_hidden_tests(self) -> tuple[bool, str]:
        hidden = self.case_dir / "hidden"
        eval_dir = self._tmp / "hidden_eval"
        shutil.copytree(hidden, eval_dir)
        proc = subprocess.run(
            ["python", "-m", "pytest", "-q", str(eval_dir)],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            timeout=60,
            env=self._test_env({"PYTHONPATH": str(self.workspace)}),
        )
        return proc.returncode == 0, (proc.stdout + "\n" + proc.stderr).strip()

    def unified_diff(self) -> str:
        seed = self.case_dir / "seed"
        files = set()
        for base in (seed, self.workspace):
            for p in base.rglob("*"):
                if p.is_file() and "__pycache__" not in p.parts and ".pytest_cache" not in p.parts:
                    files.add(str(p.relative_to(base)).replace("\\", "/"))
        chunks = []
        for rel in sorted(files):
            a = seed / rel
            b = self.workspace / rel
            old = a.read_text(encoding="utf-8").splitlines(True) if a.exists() else []
            new = b.read_text(encoding="utf-8").splitlines(True) if b.exists() else []
            if old == new:
                continue
            chunks.extend(difflib.unified_diff(old, new, fromfile=f"a/{rel}", tofile=f"b/{rel}"))
        return "".join(chunks)
