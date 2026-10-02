# Tests for the prompt techniques of server/features/qa_generator.py.
# No real LLM call: a stand-in records the prompts. Run from the project root: py -3.13 -m pytest

import pytest

from server.features import qa_generator
from server.features.qa_generator import DEFAULT_TECHNIQUE, TECHNIQUES
from server.prompt_loader import load_prompt

QUESTIONS = ["Q one?", "Q two?", "Q three?", "Q four?", "Q five?"]


def record_calls(monkeypatch, reply):
    """Replace LLMClient in qa_generator with a stand-in that records the prompts.

    Args:
        monkeypatch: pytest's helper for temporary changes, undone after the test.
        reply: the dict the stand-in "model" returns for every call.

    Returns:
        A list that gets one (system_prompt, user_prompt) pair per call.
    """
    calls = []

    class RecordingLLMClient:
        """Stands in for LLMClient: records the prompts and returns `reply`."""

        def __init__(self, **settings):
            """Accept the model settings; they are not needed here."""

        def complete_json(self, system_prompt, user_prompt, images=None):
            """Record the prompts and return the prepared reply."""
            calls.append((system_prompt, user_prompt))
            return reply

    monkeypatch.setattr(qa_generator, "LLMClient", RecordingLLMClient)
    return calls


def test_there_are_five_techniques_and_the_app_uses_role_and_rules():
    """The requirement asks for at least 5 techniques; the app keeps its tested prompt."""
    assert len(TECHNIQUES) >= 5
    assert DEFAULT_TECHNIQUE == "role_and_rules"


def test_the_app_function_still_returns_only_the_questions(monkeypatch):
    """generate_questions() (used by the Role Q&A page) returns the plain list, as before."""
    calls = record_calls(monkeypatch, {"questions": QUESTIONS})
    assert qa_generator.generate_questions("QA Engineer", "Junior") == QUESTIONS
    assert calls[0][0] == load_prompt("qa_generator/role_and_rules")


@pytest.mark.parametrize("technique", list(TECHNIQUES))
def test_each_technique_sends_its_own_prompt_and_the_same_test_case(monkeypatch, technique):
    """Each technique sends its own prompt file, and the user prompt (the test case) is always the same.

    Args:
        technique: one of TECHNIQUES (the test runs once per technique).
    """
    calls = record_calls(monkeypatch, {"questions": QUESTIONS})
    qa_generator.generate_questions_with_technique("Backend Developer", "Senior", technique=technique)
    assert calls == [(load_prompt(f"qa_generator/{technique}"), "Role: Backend Developer\nLevel: Senior")]


def test_all_techniques_have_different_prompts():
    """The five prompt files are really different, not copies."""
    texts = [load_prompt(f"qa_generator/{technique}") for technique in TECHNIQUES]
    assert len(set(texts)) == len(TECHNIQUES)


def test_unknown_technique_is_rejected_before_the_llm_call(monkeypatch):
    """An unknown technique raises ValueError, and no LLM call is made."""
    calls = record_calls(monkeypatch, {"questions": QUESTIONS})
    with pytest.raises(ValueError, match="Unknown prompt technique"):
        qa_generator.generate_questions_with_technique("QA Engineer", "Junior", technique="magic")
    assert calls == []


def test_reasoning_is_returned_and_empty_questions_are_dropped(monkeypatch):
    """The planning of chain-of-thought is returned; empty or non-text questions are left out."""
    record_calls(monkeypatch, {"reasoning": "1. Skills: Python", "questions": ["Real question?", "", None, "  "]})
    result = qa_generator.generate_questions_with_technique("QA Engineer", "Junior", technique="chain_of_thought")
    assert result == {"questions": ["Real question?"], "reasoning": "1. Skills: Python"}
