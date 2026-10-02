# Loads the system prompts stored as files in server/prompts/.
# Every prompt gets the scope guardrail (guard 3, prompts/guardrail.md) added at the end,
# so every feature is covered, also features added later.

import re
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"
GUARDRAIL = "guardrail"

# <!-- ... --> comments in the .md files are notes for developers, not for the model.
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def read_prompt_file(name):
    """Read one prompt file from server/prompts/, without its developer comments.

    <!-- ... --> comments are notes for developers and are never sent to the model.

    Args:
        name: the file name without ".md", e.g. "qa_generator" reads
            server/prompts/qa_generator.md.

    Returns:
        The text of the file (str), without comments and without spaces at the
        start and end.
    """
    text = (PROMPTS_DIR / f"{name}.md").read_text(encoding="utf-8")
    return HTML_COMMENT.sub("", text).strip()


def load_prompt(name):
    """Build the full system prompt of a feature: its own prompt, then the guardrail (guard 3).

    The guardrail comes last, because it replaces the feature's reply format
    when a request is out of scope. Features should always load their prompts
    with this function, so none of them can miss the guardrail.

    Args:
        name: the feature's prompt file without ".md", e.g. "job_analyzer".

    Returns:
        The system prompt (str) to send to the model.
    """
    return f"{read_prompt_file(name)}\n\n{read_prompt_file(GUARDRAIL)}"
