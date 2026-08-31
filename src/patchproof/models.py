from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    ok: bool
    output: str


@dataclass
class AgentOutcome:
    stage: str
    finished: bool
    summary: str = ""
    root_cause: str = ""
    evidence: list[str] = field(default_factory=list)
    steps: int = 0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunResult:
    case_id: str
    mode: str
    public_passed: bool
    hidden_passed: bool
    verified_resolved: bool
    steps: int
    duration_seconds: float
    trajectory_path: str
    patch_path: str
    outcome_summary: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
