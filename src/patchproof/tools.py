from __future__ import annotations
from pathlib import PurePosixPath
from .sandbox import Sandbox
from .models import ToolResult


def _is_existing_test(path: str) -> bool:
    p = PurePosixPath(path.replace("\\", "/"))
    return p.name.startswith("test_") or "tests" in p.parts


def _write_allowed(path: str, write_policy: str) -> bool:
    p = PurePosixPath(path.replace("\\", "/"))
    name = p.name
    if write_policy == "all":
        return True
    if write_policy == "none":
        return False
    if write_policy == "production_only":
        return not _is_existing_test(path)
    if write_policy == "tests_only":
        return name.startswith("test_agent_") and name.endswith(".py")
    return False


def execute_tool(sandbox: Sandbox, action: dict, write_policy: str) -> ToolResult:
    name = action.get("action")
    try:
        if name == "list_files":
            return ToolResult(True, "\n".join(sandbox.list_files()))
        if name == "read_file":
            return ToolResult(True, sandbox.read_file(action["path"]))
        if name == "run_tests":
            ok, out = sandbox.run_public_tests()
            return ToolResult(ok, out)
        if name == "write_file":
            path = action["path"]
            if not _write_allowed(path, write_policy):
                return ToolResult(False, f"write_file is disallowed for {path} in this stage")
            sandbox.write_file(path, action["content"])
            return ToolResult(True, f"Wrote {path}")
        return ToolResult(False, f"Unknown or disallowed action: {name}")
    except Exception as exc:
        return ToolResult(False, f"{type(exc).__name__}: {exc}")
