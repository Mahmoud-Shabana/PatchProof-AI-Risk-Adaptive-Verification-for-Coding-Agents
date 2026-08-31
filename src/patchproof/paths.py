from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parents[1]
PROMPTS_DIR = PROJECT_ROOT / "prompts"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")
