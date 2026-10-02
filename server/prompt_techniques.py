# Shared helpers for features that have several prompt techniques (see the Prompt Lab).
# A feature with techniques keeps one prompt file per technique in prompts/<feature>/
# and lists them in a TECHNIQUES dict.


def reasoning_text(reply):
    """Get the model's thinking from a reply, if the technique asks for it.

    Chain-of-thought writes it into "reasoning" (a text), self-critique into
    "review" (a list of corrections).

    Args:
        reply: the model's reply as a dict.

    Returns:
        The reasoning as one str (a list becomes one line per item), or None
        if the reply has none.
    """
    value = reply.get("reasoning") or reply.get("review")
    if isinstance(value, list):
        value = "\n".join(str(item) for item in value)
    return value.strip() if isinstance(value, str) and value.strip() else None


def check_technique(technique, techniques):
    """Check that a technique is one of a feature's techniques.

    Args:
        technique: the technique name, e.g. "few_shot".
        techniques: the feature's TECHNIQUES dict.

    Raises:
        ValueError: the technique is unknown (before any LLM call).
    """
    if technique not in techniques:
        raise ValueError(f"Unknown prompt technique: {technique!r}. Choose one of: {', '.join(techniques)}.")
