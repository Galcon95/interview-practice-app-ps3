# Feature 1: Role-based Q&A generator (IT jobs only for now).
# Step 2: questions for a role and level. Model answers come later.
# The prompt has 5 techniques (prompts/qa_generator/); the app always uses the default,
# the Prompt Lab (developer mode) compares them for the same role and level.

from server.guards.input_validation import validate_role_and_level
from server.llm import LLMClient
from server.prompt_loader import load_prompt
from server.prompt_techniques import check_technique, reasoning_text

TECHNIQUES = {
    "zero_shot": {
        "label": "1 · Zero-shot",
        "description": 'Just the request: "Give me 5 interview questions for the job title and level." No role, no rules, no examples.',
    },
    "role_and_rules": {
        "label": "2 · Zero-shot with role and rules",
        "description": "A role (experienced technical interviewer), what each level means, and rules for the mix of questions.",
    },
    "few_shot": {
        "label": "3 · Few-shot",
        "description": "Example questions on C++, JavaScript and software engineering, each with topic, level and type, plus one complete example.",
    },
    "chain_of_thought": {
        "label": "4 · Chain-of-Thought",
        "description": "The rules of 2, plus step-by-step planning first: the role's skills, what the level means, a topic for each question.",
    },
    "self_critique": {
        "label": "5 · Self-critique",
        "description": "The rules of 2, plus a draft that is checked against a checklist (level fit, variety, length) and corrected.",
    },
}
DEFAULT_TECHNIQUE = "role_and_rules"


def generate_questions(role, level, settings=None):
    """Generate 5 interview questions for an IT role and level (feature 1), with the default technique.

    Args:
        role: the IT role, one of input_validation.IT_ROLES, e.g. "Backend Developer".
        level: the seniority level, one of input_validation.LEVELS, e.g. "Senior".
        settings: the LLM settings from the sidebar ({"model", "temperature",
            "max_tokens"}), or None for the defaults in llm.py.

    Returns:
        A list of 5 questions (str).

    Raises:
        ValueError: the role or level is not allowed (guard 1, before the LLM
            call), or an error from the LLM call (see LLMClient.complete_json).
    """
    return generate_questions_with_technique(role, level, settings)["questions"]


def generate_questions_with_technique(role, level, settings=None, technique=DEFAULT_TECHNIQUE):
    """Generate 5 interview questions with a chosen prompt technique, and return the model's reasoning too.

    Used by the Prompt Lab to compare the techniques; the app uses generate_questions().

    Args:
        role: the IT role, one of input_validation.IT_ROLES, e.g. "Backend Developer".
        level: the seniority level, one of input_validation.LEVELS, e.g. "Senior".
        settings: the LLM settings ({"model", "temperature", "max_tokens"}), or
            None for the defaults in llm.py.
        technique: the prompt technique, one of TECHNIQUES.

    Returns:
        A dict {"questions": list of str, "reasoning": str or None}. "reasoning"
        is the model's planning (chain_of_thought) or corrections (self_critique).

    Raises:
        ValueError: the role or level is not allowed or the technique is unknown
            (before the LLM call), or an error from the LLM call (see
            LLMClient.complete_json).
    """
    error = validate_role_and_level(role, level)  # guard 1, before the paid call
    if error:
        raise ValueError(error)
    check_technique(technique, TECHNIQUES)
    system_prompt = load_prompt(f"qa_generator/{technique}")
    user_prompt = f"Role: {role}\nLevel: {level}"
    reply = LLMClient(**(settings or {})).complete_json(system_prompt, user_prompt)
    questions = [q.strip() for q in reply.get("questions", []) if isinstance(q, str) and q.strip()]
    return {"questions": questions, "reasoning": reasoning_text(reply)}
