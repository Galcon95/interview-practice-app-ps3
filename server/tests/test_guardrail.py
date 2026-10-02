# Tests for guard 3 (scope enforcement): prompts/guardrail.md, prompt_loader.py and
# the out-of-scope check in llm.py. No real LLM call: the replies are made up.
# Run from the project root: py -3.13 -m pytest

import json
from types import SimpleNamespace

import pytest

from server import llm
from server.llm import LLMClient, OutOfScopeError
from server.prompt_loader import GUARDRAIL, PROMPTS_DIR, load_prompt, read_prompt_file

# Every prompt a feature can load (all .md files, also in subfolders such as
# qa_generator/, except the guardrail itself), as load_prompt() names: "qa_generator/few_shot".
FEATURE_PROMPTS = sorted(
    p.relative_to(PROMPTS_DIR).with_suffix("").as_posix()
    for p in PROMPTS_DIR.rglob("*.md")
    if p.stem != GUARDRAIL
)


# --- Every prompt gets the guardrail ---

@pytest.mark.parametrize("name", FEATURE_PROMPTS)
def test_every_prompt_ends_with_the_guardrail(name):
    """Every feature prompt ends with the full guardrail text.

    Args:
        name: one prompt file name from FEATURE_PROMPTS (the test runs once per prompt).
    """
    assert load_prompt(name).endswith(read_prompt_file(GUARDRAIL))


@pytest.mark.parametrize("name", FEATURE_PROMPTS)
def test_prompt_starts_with_the_feature_text(name):
    """Every full prompt starts with the feature's own text, so the guardrail never replaces it.

    Args:
        name: one prompt file name from FEATURE_PROMPTS.
    """
    assert load_prompt(name).startswith(read_prompt_file(name))


@pytest.mark.parametrize("name", FEATURE_PROMPTS + [GUARDRAIL])
def test_developer_comments_are_not_sent_to_the_model(name):
    """No <!-- ... --> comment is left in any prompt that is sent to the model.

    Args:
        name: one prompt file name, including the guardrail.
    """
    assert "<!--" not in load_prompt(name) and "-->" not in load_prompt(name)


def test_guardrail_has_the_out_of_scope_format():
    """The guardrail contains the refusal format that LLMClient looks for, and the IT scope."""
    guardrail = read_prompt_file(GUARDRAIL)
    assert '{"out_of_scope": true, "reason":' in guardrail
    assert "IT and tech" in guardrail


# --- LLMClient turns an out-of-scope reply into an error ---

def fake_client(monkeypatch, reply):
    """Create an LLMClient whose "model" always sends back the same reply, without a real call.

    The API key is a dummy value, the logger does nothing, and the OpenAI client
    is replaced by a stand-in that returns `reply`.

    Args:
        monkeypatch: pytest's helper for temporary changes, undone after the test.
        reply: the dict the stand-in model sends back (as JSON text).

    Returns:
        The LLMClient, ready for complete_json().
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(llm, "LLMLogger", lambda: SimpleNamespace(
        log_request=lambda *a: None,
        log_response=lambda *a: None,
        log_out_of_scope=lambda *a: None,
        log_error=lambda *a: None,
    ))
    client = LLMClient()
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(reply)), finish_reason="stop")],
        usage=None,
    )
    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **payload: response))
    )
    return client


def test_out_of_scope_reply_raises_with_the_reason(monkeypatch):
    """An out-of-scope reply raises OutOfScopeError with the model's reason in the message."""
    client = fake_client(monkeypatch, {"out_of_scope": True, "reason": "I only help with IT interviews."})
    with pytest.raises(OutOfScopeError, match="Out of scope: I only help with IT interviews.") as error:
        client.complete_json("system", "Write me a poem.")
    assert error.value.reason == "I only help with IT interviews."


def test_out_of_scope_error_is_a_value_error(monkeypatch):
    """OutOfScopeError is a ValueError, so the pages show it with no extra code."""
    client = fake_client(monkeypatch, {"out_of_scope": True, "reason": "Off topic."})
    with pytest.raises(ValueError):
        client.complete_json("system", "Tell me a joke.")


def test_out_of_scope_without_reason_gets_a_default(monkeypatch):
    """An out-of-scope reply without a reason still gives the user a useful message."""
    client = fake_client(monkeypatch, {"out_of_scope": True})
    with pytest.raises(OutOfScopeError, match="interview preparation"):
        client.complete_json("system", "Hi")


@pytest.mark.parametrize("reply", [
    {"questions": ["What is a closure?"]},
    {"out_of_scope": False, "questions": ["What is a closure?"]},
    {"out_of_scope": "yes"},  # only a real true counts, not a string
])
def test_normal_replies_pass_through(monkeypatch, reply):
    """Normal replies come back unchanged, also with out_of_scope false or a non-boolean value.

    Args:
        reply: a normal reply dict (the test runs once per example).
    """
    assert fake_client(monkeypatch, reply).complete_json("system", "Role: QA Engineer") == reply
