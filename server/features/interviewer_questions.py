# Feature 2: "Questions to ask the interviewer" generator.
# Used together with feature 1 (same role / level).

from server.guards.input_validation import validate_role_and_level
from server.llm import LLMClient
from server.prompt_loader import load_prompt


def generate_interviewer_questions(role, level, settings=None):
    """Generate 5 questions the candidate can ask the interviewer (feature 2).

    Args:
        role: the IT role, one of input_validation.IT_ROLES, e.g. "DevOps / SRE".
        level: the seniority level, one of input_validation.LEVELS, e.g. "Mid".
        settings: the LLM settings from the sidebar ({"model", "temperature",
            "max_tokens"}), or None for the defaults in llm.py.

    Returns:
        A list of 5 dicts: {"category": "Tech stack", "question": "..."}.

    Raises:
        ValueError: the role or level is not allowed (guard 1, before the LLM
            call), or an error from the LLM call (see LLMClient.complete_json).
    """
    error = validate_role_and_level(role, level)  # guard 1, before the paid call
    if error:
        raise ValueError(error)
    system_prompt = load_prompt("interviewer_questions")
    user_prompt = f"Role: {role}\nLevel: {level}"
    reply = LLMClient(**(settings or {})).complete_json(system_prompt, user_prompt)
    return reply["questions"]
