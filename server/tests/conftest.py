# Shared test setup. pytest runs the fixtures marked autouse before every test.

import pytest

from server.guards.rate_limit import reset_rate_limit


@pytest.fixture(autouse=True)
def fresh_rate_limit():
    """Reset the rate limit counter before and after every test (runs automatically).

    The counter is shared by the whole program, so without this, calls made in
    one test would count against the next one.

    Yields:
        Nothing; the test runs at the "yield".
    """
    reset_rate_limit()
    yield
    reset_rate_limit()
