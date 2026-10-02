# Guard 4: Rate limiting.
# Stops endless requests (a stuck button, a script, click spamming) from running up
# the OpenRouter bill. For now the app has one user, so there is one shared counter:
# at most MAX_REQUESTS LLM calls in any WINDOW_SECONDS. With logins, this would
# become one counter per user.
#
# How it works (a "sliding window"): remember the time of each recent call. Before a
# new call, forget the times older than the window, then count the rest.
# LLMClient.complete_json() calls check_rate_limit() before every request.

import math
import threading
import time
from collections import deque

MAX_REQUESTS = 10
WINDOW_SECONDS = 60

_request_times = deque()  # times of the recent calls, oldest first
_lock = threading.Lock()  # Streamlit runs each browser tab in its own thread


def check_rate_limit(now=None):
    """Check whether another LLM call is allowed right now, and count it if so (guard 4).

    Calls older than WINDOW_SECONDS are forgotten first. If MAX_REQUESTS calls
    are left, the new call is refused. A refused call is not counted, so
    clicking again while blocked does not make the wait longer.

    Args:
        now: the current time in seconds, only passed by the tests. Normally
            None, and time.monotonic() is used.

    Returns:
        An error message (str) that says how many seconds to wait, or None if
        the call may go ahead.
    """
    now = time.monotonic() if now is None else now
    with _lock:
        while _request_times and now - _request_times[0] >= WINDOW_SECONDS:
            _request_times.popleft()
        if len(_request_times) >= MAX_REQUESTS:
            wait = math.ceil(WINDOW_SECONDS - (now - _request_times[0]))
            return (
                f"Too many requests: at most {MAX_REQUESTS} AI calls per "
                f"{WINDOW_SECONDS} seconds. Please wait {wait} seconds."
            )
        _request_times.append(now)
        return None


def reset_rate_limit():
    """Forget all counted calls, so the limit starts again at 0 (used by the tests)."""
    with _lock:
        _request_times.clear()
