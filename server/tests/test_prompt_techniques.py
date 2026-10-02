# Tests for server/prompt_techniques.py (shared helpers for prompt techniques).
# No LLM calls. Run from the project root: py -3.13 -m pytest

import pytest

from server.prompt_techniques import check_technique, reasoning_text


def test_reasoning_text_returns_the_reasoning_of_chain_of_thought():
    """The "reasoning" text of a chain-of-thought reply is returned, without spaces around it."""
    assert reasoning_text({"reasoning": "  1. Skills: Python  "}) == "1. Skills: Python"


def test_reasoning_text_joins_a_review_list():
    """A self-critique "review" list becomes one line per correction."""
    assert reasoning_text({"review": ["Removed a duplicate", "Shortened Q3"]}) == "Removed a duplicate\nShortened Q3"


def test_reasoning_text_is_none_without_reasoning():
    """Replies without reasoning (zero-shot, few-shot) give None, also for an empty text."""
    assert reasoning_text({"questions": []}) is None
    assert reasoning_text({"reasoning": "   "}) is None


def test_check_technique_accepts_a_known_technique():
    """A technique in the list passes without an error."""
    check_technique("few_shot", {"few_shot": {}, "zero_shot": {}})


def test_check_technique_rejects_an_unknown_technique():
    """An unknown technique raises ValueError, naming the allowed ones."""
    with pytest.raises(ValueError, match="Unknown prompt technique: 'magic'. Choose one of: few_shot, zero_shot"):
        check_technique("magic", {"few_shot": {}, "zero_shot": {}})
