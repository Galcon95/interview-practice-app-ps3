# Checks that prompt_lab/injection_tests.ini (the prompt-injection test cases for the
# JD Analyzer) stays valid when it is edited. No LLM calls. Run: py -3.13 -m pytest

import configparser

import pytest

from server.guards.input_validation import validate_job_description
from server.prompt_lab import LAB_DIR

INJECTION_FILE = LAB_DIR / "injection_tests.ini"
CASE_FIELDS = {"tests", "attack", "position", "input", "refusal_allowed", "forbidden", "pass_if"}


def read_file():
    """Read the injection test file.

    Returns:
        The parsed configparser.ConfigParser.
    """
    config = configparser.ConfigParser()
    config.read(INJECTION_FILE, encoding="utf-8")
    return config


CASES = [name for name in read_file().sections() if name != "base"]


def test_the_base_posting_is_long_enough_and_has_its_expectations():
    """The base posting passes guard 1 (so the attacks really reach the model) and says what is correct."""
    base = read_file()["base"]
    assert validate_job_description(base["posting"]) is None
    for field in ("expect_title", "expect_seniority", "expect_work_mode", "expect_skills"):
        assert base[field].strip()


def test_there_are_at_least_ten_cases():
    """The file holds the 10 attack types (more can be added)."""
    assert len(CASES) >= 10


@pytest.mark.parametrize("name", CASES)
def test_every_case_has_all_fields_with_valid_values(name):
    """Each case has every field, and position, input and refusal_allowed use their allowed values.

    Args:
        name: the section name of the case.
    """
    case = read_file()[name]
    assert CASE_FIELDS <= set(case), f"missing: {CASE_FIELDS - set(case)}"
    assert case["position"] in ("end", "middle")
    assert case["input"] in ("text", "screenshot")
    assert case["refusal_allowed"] in ("yes", "no")
    assert [word.strip() for word in case["forbidden"].split(",") if word.strip()], "no forbidden words"
    assert case["attack"].strip() and case["pass_if"].strip()
