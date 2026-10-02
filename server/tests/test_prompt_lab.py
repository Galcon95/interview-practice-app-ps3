# Tests for server/prompt_lab.py: test cases (INI), rubric, measurements and saved scores (CSV).
# They use temporary files; one test reads the real prompt_lab/test_cases.ini, none writes
# to the real prompt_lab/scores.csv. No LLM calls. Run from the project root: py -3.13 -m pytest

import pytest

from server import prompt_lab
from server.prompt_lab import (
    JUDGE_DEFAULT_MODEL,
    RUBRIC,
    RUBRIC_KEYS,
    SCORE_COLUMNS,
    TEST_CASES_FILE,
    judge_questions,
    load_scores,
    load_test_cases,
    measure_questions,
    save_scores,
    sentence_count,
    score_row,
    topic_covered,
)

CASE = {"name": "Junior QA", "role": "QA Engineer", "level": "Junior", "note": "",
        "expected_topics": ["bug reports", "teamwork", "SQL"]}
QUESTIONS = [
    "What makes a good bug report?",
    "Tell me about a time you worked in a team. What did you learn?",
    "How do you test a login form?",
]


# --- Rubric ---

def test_every_criterion_has_a_question_and_anchors_for_1_3_and_5():
    """Each rubric criterion says what it asks and what a 1, a 3 and a 5 mean."""
    assert len(RUBRIC) == 4
    for criterion in RUBRIC:
        assert criterion["question"] and set(criterion["anchors"]) == {1, 3, 5}


# --- Measurements ---

def test_measure_questions_counts_length_packed_behavioral_and_topics():
    """Words, packed questions (more than one sentence), behavioral phrases and topics are counted."""
    measured = measure_questions(QUESTIONS, CASE["expected_topics"])
    assert measured["count"] == 3
    assert measured["avg_words"] == pytest.approx((6 + 14 + 7) / 3)
    assert measured["multi_part"] == 1  # the teamwork question has two sentences
    assert measured["behavioral"] == 1  # "Tell me about a time"
    assert measured["topics_covered"] == ["bug reports", "teamwork"]
    assert measured["topics_missing"] == ["SQL"]


def test_measure_questions_without_questions():
    """No questions give zeros instead of a division error."""
    measured = measure_questions([], ["SQL"])
    assert measured["count"] == 0 and measured["avg_words"] == 0.0 and measured["topics_missing"] == ["SQL"]


@pytest.mark.parametrize("text, expected", [
    ("What makes a good bug report?", 1),
    ("How do you test a login form? Give an example.", 2),
    ("Tell me about a time you worked in a team. What did you learn?", 2),
    ("Which tools do you use, e.g. Selenium vs. Playwright?", 1),  # abbreviations don't count
])
def test_sentence_count(text, expected):
    """Sentences are counted by . ? and !, but not after e.g., i.e., vs. or etc.

    Args:
        text: one question.
        expected: the number of sentences in it.
    """
    assert sentence_count(text) == expected


@pytest.mark.parametrize("topic, text, expected", [
    ("manual vs. automated testing", "when do you automate tests versus test manually?", True),
    ("test automation basics", "how would you start with test automation?", True),  # "basics" is a filler
    ("teamwork", "tell me about your team", True),
    ("SLOs and reliability", "how do you set slos for a service?", True),  # half of the words is enough
    ("SQL", "how do you design a rest api?", False),
    ("data pipelines", "what is your favourite tool?", False),
])
def test_topic_covered(topic, text, expected):
    """A topic is covered if at least half of its words appear with their first 4 letters.

    Args:
        topic: the expected topic.
        text: the questions in lower case.
        expected: whether the topic should count as covered.
    """
    assert topic_covered(topic, text) is expected


# --- Saved scores ---

def test_score_row_has_every_column_and_the_total():
    """A row has a value for every CSV column; total is the sum of the four scores."""
    scores = {"role_fit": 5, "level_fit": 4, "variety": 3, "clarity": 2}
    row = score_row(CASE, "openai/gpt-5-mini", "few_shot", {"questions": QUESTIONS, "seconds": 7.25},
                    scores, "2026-10-01 14:30")
    assert set(row) == set(SCORE_COLUMNS)
    assert row["total"] == 14 and row["topics_covered"] == 2 and row["topics_expected"] == 3
    assert row["question_texts"].count(" | ") == 2


def test_scores_are_saved_and_read_back(tmp_path):
    """Rows appended twice come back with the header once and numbers as numbers."""
    path = tmp_path / "scores.csv"
    scores = dict.fromkeys(RUBRIC_KEYS, 4)
    row = score_row(CASE, "openai/gpt-5-mini", "zero_shot", {"questions": QUESTIONS, "seconds": 6.0},
                    scores, "2026-10-01 14:30")
    save_scores([row], path)
    save_scores([row], path)
    rows = load_scores(path)
    assert len(rows) == 2
    assert rows[0]["total"] == 16 and rows[0]["avg_words"] == pytest.approx(9.0)
    assert rows[0]["case"] == "Junior QA" and rows[0]["technique"] == "zero_shot"
    assert path.read_text(encoding="utf-8-sig").count("saved_at") == 1  # one header line


def test_no_scores_file_gives_an_empty_list(tmp_path):
    """Before the first save, there are simply no scores."""
    assert load_scores(tmp_path / "missing.csv") == []


def write_cases(tmp_path, text):
    """Write a test case file into pytest's temporary folder.

    Args:
        tmp_path: pytest's temporary folder for this test.
        text: the content of the INI file.

    Returns:
        The path of the file.
    """
    path = tmp_path / "test_cases.ini"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_valid_case_is_read_with_all_fields(tmp_path):
    """Role, level, note and the comma-separated expected topics are read; spaces are stripped."""
    path = write_cases(tmp_path, (
        "[Junior QA]\n"
        "role = QA Engineer\n"
        "level = Junior\n"
        "note = Entry level.\n"
        "expected_topics = test cases ,  bug reports,, teamwork\n"
    ))
    cases, problems = load_test_cases(path)
    assert problems == []
    assert cases == [{
        "name": "Junior QA", "role": "QA Engineer", "level": "Junior",
        "note": "Entry level.", "expected_topics": ["test cases", "bug reports", "teamwork"],
    }]


def test_note_and_topics_are_optional(tmp_path):
    """Without note and expected_topics, the case still works with empty values."""
    cases, problems = load_test_cases(write_cases(tmp_path, "[Lead DevOps]\nrole = DevOps / SRE\nlevel = Lead\n"))
    assert problems == []
    assert cases[0]["note"] == "" and cases[0]["expected_topics"] == []


def test_cases_keep_the_order_of_the_file(tmp_path):
    """The cases come back in the order they are written in the file."""
    text = "[B]\nrole = QA Engineer\nlevel = Mid\n[A]\nrole = QA Engineer\nlevel = Lead\n"
    cases, _ = load_test_cases(write_cases(tmp_path, text))
    assert [case["name"] for case in cases] == ["B", "A"]


def test_a_case_with_a_wrong_role_is_skipped_and_reported(tmp_path):
    """A wrong role skips only that case, and the problem names the case."""
    text = "[Chef]\nrole = Chef\nlevel = Junior\n[OK]\nrole = QA Engineer\nlevel = Junior\n"
    cases, problems = load_test_cases(write_cases(tmp_path, text))
    assert [case["name"] for case in cases] == ["OK"]
    assert len(problems) == 1 and problems[0].startswith("[Chef] Unknown role")


def test_a_case_without_level_is_skipped_and_reported(tmp_path):
    """A missing level is reported like a wrong one."""
    cases, problems = load_test_cases(write_cases(tmp_path, "[No level]\nrole = QA Engineer\n"))
    assert cases == []
    assert problems[0].startswith("[No level] Unknown level")


def test_a_missing_file_is_reported(tmp_path):
    """Without the file, there are no cases and one clear problem."""
    cases, problems = load_test_cases(tmp_path / "missing.ini")
    assert cases == [] and "not found" in problems[0]


def test_an_empty_file_is_reported(tmp_path):
    """A file without sections gives a problem instead of an empty, silent page."""
    cases, problems = load_test_cases(write_cases(tmp_path, "; only a comment\n"))
    assert cases == [] and "no test cases" in problems[0]


def test_a_broken_file_is_reported(tmp_path):
    """A file that is not valid INI is reported instead of crashing the page."""
    cases, problems = load_test_cases(write_cases(tmp_path, "role = QA Engineer\n"))  # no [section]
    assert cases == [] and "could not be read" in problems[0]


def test_the_real_test_case_file_is_valid():
    """Every case in prompt_lab/test_cases.ini is valid, and there is more than one."""
    cases, problems = load_test_cases(TEST_CASES_FILE)
    assert problems == []
    assert len(cases) >= 2


# --- LLM-as-judge ---

def fake_judge(monkeypatch, reply):
    """Replace LLMClient in prompt_lab with a stand-in judge that records the call.

    Args:
        monkeypatch: pytest's helper for temporary changes, undone after the test.
        reply: the dict the stand-in judge returns.

    Returns:
        A list that gets one dict {"settings", "system", "user"} per call.
    """
    calls = []

    class RecordingJudge:
        """Stands in for LLMClient: records the settings and prompts, returns `reply`."""

        def __init__(self, **settings):
            """Remember the model settings of the call."""
            self.settings = settings

        def complete_json(self, system_prompt, user_prompt, images=None):
            """Record the prompts and return the prepared reply."""
            calls.append({"settings": self.settings, "system": system_prompt, "user": user_prompt})
            return reply

    monkeypatch.setattr(prompt_lab, "LLMClient", RecordingJudge)
    return calls


VALID_VERDICT = {key: {"score": 4, "reason": f"Reason for {key}."} for key in RUBRIC_KEYS}


def test_the_judge_gets_the_rubric_and_the_questions_but_not_the_technique(monkeypatch):
    """The judge prompt contains every criterion and its anchors, the case and the numbered questions."""
    calls = fake_judge(monkeypatch, VALID_VERDICT)
    judge_questions(CASE, QUESTIONS)
    call = calls[0]
    for criterion in RUBRIC:
        assert criterion["key"] in call["system"] and criterion["anchors"][5] in call["system"]
    assert "{rubric}" not in call["system"]
    assert "Role: QA Engineer" in call["user"] and "Level: Junior" in call["user"]
    assert "Expected topics: bug reports, teamwork, SQL" in call["user"]
    assert "Q1. What makes a good bug report?" in call["user"] and "Q3." in call["user"]
    for technique in ("zero_shot", "few_shot", "chain_of_thought", "self_critique", "role_and_rules"):
        assert technique not in call["user"]  # blind: the judge never sees the technique


def test_the_judge_uses_temperature_0_and_the_chosen_model(monkeypatch):
    """The judge runs at temperature 0 with the given model (default: JUDGE_DEFAULT_MODEL)."""
    calls = fake_judge(monkeypatch, VALID_VERDICT)
    judge_questions(CASE, QUESTIONS)
    judge_questions(CASE, QUESTIONS, model="openai/gpt-4.1-mini")
    assert calls[0]["settings"]["model"] == JUDGE_DEFAULT_MODEL and calls[0]["settings"]["temperature"] == 0
    assert calls[1]["settings"]["model"] == "openai/gpt-4.1-mini"


def test_a_valid_verdict_is_returned(monkeypatch):
    """Scores and reasons come back for every criterion."""
    fake_judge(monkeypatch, VALID_VERDICT)
    assert judge_questions(CASE, QUESTIONS) == VALID_VERDICT


@pytest.mark.parametrize("bad_score", [0, 6, "4", 3.5, None, True])
def test_an_invalid_score_is_rejected(monkeypatch, bad_score):
    """A score that is not a whole number from 1 to 5 raises ValueError.

    Args:
        bad_score: the invalid score the judge gives for clarity.
    """
    fake_judge(monkeypatch, {**VALID_VERDICT, "clarity": {"score": bad_score, "reason": "x"}})
    with pytest.raises(ValueError, match="no valid score"):
        judge_questions(CASE, QUESTIONS)


def test_a_missing_criterion_is_rejected(monkeypatch):
    """A reply without one of the criteria raises ValueError."""
    fake_judge(monkeypatch, {key: value for key, value in VALID_VERDICT.items() if key != "variety"})
    with pytest.raises(ValueError, match="variety"):
        judge_questions(CASE, QUESTIONS)


def test_no_questions_are_not_judged(monkeypatch):
    """Without questions, no judge call is made."""
    calls = fake_judge(monkeypatch, VALID_VERDICT)
    with pytest.raises(ValueError, match="no questions"):
        judge_questions(CASE, [])
    assert calls == []


def test_a_row_with_only_the_judge_is_saved_and_read_back(tmp_path):
    """Without the developer's stars, their columns stay empty and come back as None."""
    path = tmp_path / "scores.csv"
    row = score_row(CASE, "openai/gpt-5-mini", "few_shot", {"questions": QUESTIONS, "seconds": 5.0},
                    None, "2026-10-01 15:00", judge=VALID_VERDICT, judge_model=JUDGE_DEFAULT_MODEL)
    assert row["total"] is None and row["judge_total"] == 16
    save_scores([row], path)
    saved = load_scores(path)[0]
    assert saved["role_fit"] is None and saved["total"] is None
    assert saved["judge_clarity"] == 4 and saved["judge_total"] == 16 and saved["judge_model"] == JUDGE_DEFAULT_MODEL
