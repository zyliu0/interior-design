from __future__ import annotations

from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent
SYSTEM_PROMPT_PATH = SKILL_ROOT / "prompts" / "system.md"


def load_system_prompt() -> str:
    return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8").rstrip() + "\n"


def compose(system_prompt: str, user_prompt: str | None) -> str:
    if not user_prompt or not user_prompt.strip():
        return system_prompt
    return (
        f"{system_prompt}\n"
        f"---\n"
        f"ADDITIONAL USER DIRECTION (secondary to all rules above):\n"
        f"{user_prompt.strip()}\n"
    )
