# Tests for guard 4 (server/guards/rate_limit.py) and its use in LLMClient.
# The tests pass their own times ("now"), so nothing has to wait a real minute.
# No real LLM call. Run from the project root: py -3.13 -m pytest

from types import SimpleNamespace

import pytest

from server import llm
from server.guards.rate_limit import MAX_REQUESTS, WINDOW_SECONDS, check_rate_limit
from server.llm import LLMClient, RateLimitError


def use_up_the_limit(now=0.0):
    """Make MAX_REQUESTS calls at the same moment, and check that all of them are allowed.

    Args:
        now: the time in seconds at which the calls happen.
    """
    for _ in range(MAX_REQUESTS):
        assert check_rate_limit(now=now) is None


def test_calls_up_to_the_limit_pass():
    """The first MAX_REQUESTS calls are all allowed."""
    use_up_the_limit()


def test_one_call_too_many_is_refused():
    """One call over the limit is refused, and the message names the limit."""
    use_up_the_limit(now=0.0)
    error = check_rate_limit(now=1.0)
    assert "Too many requests" in error
    assert f"at most {MAX_REQUESTS} AI calls per {WINDOW_SECONDS} seconds" in error


def test_the_message_says_how_long_to_wait():
    """The message says how many seconds are left until the oldest call is forgotten."""
    use_up_the_limit(now=0.0)
    assert f"wait {WINDOW_SECONDS - 20} seconds" in check_rate_limit(now=20.0)


def test_a_refused_call_does_not_count():
    """Refused calls are not counted: clicking again while blocked does not make the wait longer."""
    use_up_the_limit(now=0.0)
    for second in range(1, 30):
        assert check_rate_limit(now=float(second)) is not None
    assert check_rate_limit(now=float(WINDOW_SECONDS)) is None


def test_calls_are_allowed_again_after_the_window():
    """Calls are allowed again exactly WINDOW_SECONDS after the oldest one."""
    use_up_the_limit(now=0.0)
    assert check_rate_limit(now=WINDOW_SECONDS - 0.1) is not None
    assert check_rate_limit(now=float(WINDOW_SECONDS)) is None


def test_the_window_slides():
    """The window slides: 5 calls at 0 s and 5 at 30 s, so at 60 s exactly 5 new calls fit."""
    for _ in range(5):
        check_rate_limit(now=0.0)
    for _ in range(5):
        check_rate_limit(now=30.0)
    for _ in range(5):
        assert check_rate_limit(now=60.0) is None
    assert check_rate_limit(now=60.0) is not None


def test_llm_client_stops_before_the_paid_call(monkeypatch):
    """After MAX_REQUESTS calls, LLMClient raises RateLimitError and never contacts the model.

    Args:
        monkeypatch: pytest's helper for temporary changes, undone after the test.
    """
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    logged = []
    monkeypatch.setattr(llm, "LLMLogger", lambda: SimpleNamespace(
        log_request=lambda *a: None,
        log_response=lambda *a: None,
        log_rate_limited=lambda model, message: logged.append(message),
    ))
    sent = []
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"questions": []}'), finish_reason="stop")],
        usage=None,
    )
    client = LLMClient()
    client.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(
        create=lambda **payload: sent.append(payload) or response
    )))

    for _ in range(MAX_REQUESTS):
        client.complete_json("system", "user")
    with pytest.raises(RateLimitError, match="Too many requests"):
        client.complete_json("system", "user")
    assert len(sent) == MAX_REQUESTS  # the refused call was never sent
    assert len(logged) == 1


def test_rate_limit_error_is_a_value_error():
    """RateLimitError is a ValueError, so the pages show it as a normal error message."""
    assert issubclass(RateLimitError, ValueError)
