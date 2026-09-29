# Loads the system prompts stored as files in server/prompts/.
# TODO: add the scope guardrail (guard 3, prompts/guardrail.md) to each prompt.

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(name):
    # load_prompt("qa_generator") reads server/prompts/qa_generator.md
    return (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
