# Prompt Lab (developer mode): test data, rubric, measurements and saved scores.
#   - Test cases: prompt_lab/test_cases.ini (see that file for its format). Each case is
#     checked with the same guard as the app, so a test case can never send something to
#     the model that the Role Q&A page would refuse.
#   - Rubric: 4 criteria scored 1 to 5 by the developer (RUBRIC).
#   - LLM-as-judge: an AI scores with the same rubric, blind to the technique (judge_questions).
#   - Measurements: counted from the questions, no AI (measure_questions).
#   - Scores: appended to prompt_lab/scores.csv, one row per technique and run.

import configparser
import csv
import re
from pathlib import Path

from server.guards.input_validation import validate_role_and_level
from server.llm import LLMClient
from server.prompt_loader import load_prompt

LAB_DIR = Path(__file__).parent.parent / "prompt_lab"
TEST_CASES_FILE = LAB_DIR / "test_cases.ini"
SCORES_FILE = LAB_DIR / "scores.csv"

# The rubric: what a 1, a 3 and a 5 mean, so scores from different runs are comparable.
RUBRIC = [
    {
        "key": "role_fit",
        "label": "Role fit",
        "question": "Are the questions about the tools and the daily work of this role?",
        "anchors": {
            1: "Generic: they would fit almost any IT job.",
            3: "Mostly about the role, some are generic.",
            5: "Every question is clearly about this role's tools and work.",
        },
    },
    {
        "key": "level_fit",
        "label": "Level fit",
        "question": "Are they as hard as this level needs?",
        "anchors": {
            1: "Clearly too easy or too hard for the level.",
            3: "Mostly right, one or two miss the level.",
            5: "Every question fits the level (e.g. fundamentals for Junior, trade-offs for Senior).",
        },
    },
    {
        "key": "variety",
        "label": "Variety",
        "question": "Do they cover different topics and mix technical and behavioral questions?",
        "anchors": {
            1: "Repetitive, or only one kind of question.",
            3: "Some overlap, or the mix is one-sided.",
            5: "Five different topics, with technical and behavioral questions.",
        },
    },
    {
        "key": "clarity",
        "label": "Clarity",
        "question": "Could an interviewer say them out loud as they are?",
        "anchors": {
            1: "Long, several questions in one, hard to follow.",
            3: "Understandable, but some are long or packed.",
            5: "Short, one clear question each, natural spoken language.",
        },
    },
]
RUBRIC_KEYS = [criterion["key"] for criterion in RUBRIC]

# Phrases that usually mark a behavioral question ("Tell me about a time ...").
BEHAVIORAL_PHRASES = [
    "tell me about", "describe a time", "describe a situation", "give an example of a time",
    "a time when", "a time you", "have you ever", "how did you handle", "how do you handle",
    "disagree", "conflict", "feedback",
]
# Small words that don't decide whether a topic is covered.
TOPIC_STOPWORDS = {"and", "the", "for", "with", "vs", "of", "a", "an", "to", "in", "on", "or"}

# LLM-as-judge: scores the questions with the same RUBRIC. A model from another family than
# the one that writes the questions, because models tend to rate their own text higher.
JUDGE_DEFAULT_MODEL = "google/gemini-2.5-flash"
JUDGE_KEYS = [f"judge_{key}" for key in RUBRIC_KEYS]

# Columns of scores.csv. The developer's columns (RUBRIC_KEYS, total) or the judge's
# columns (judge_...) are empty if that side did not score the technique.
SCORE_COLUMNS = [
    "saved_at", "case", "role", "level", "model", "technique",
    *RUBRIC_KEYS, "total",
    "judge_model", *JUDGE_KEYS, "judge_total",
    "questions", "avg_words", "multi_part", "behavioral", "topics_covered", "topics_expected",
    "seconds", "question_texts",
]
INT_COLUMNS = {
    *RUBRIC_KEYS, "total", *JUDGE_KEYS, "judge_total",
    "questions", "multi_part", "behavioral", "topics_covered", "topics_expected",
}
FLOAT_COLUMNS = {"avg_words", "seconds"}


def load_test_cases(path=TEST_CASES_FILE):
    """Read the Prompt Lab's test cases from the INI file, and check each one.

    The file is read on every call, so changes show up at the next page reload.
    A case with a missing or wrong role or level is skipped and reported.

    Args:
        path: the INI file; only the tests pass another one.

    Returns:
        A tuple (cases, problems):
            cases: a list of dicts {"name", "role", "level", "note",
                "expected_topics"} in the order of the file; "note" is a str
                ("" if missing), "expected_topics" a list of str (empty if missing).
            problems: a list of messages (str) about the file or skipped cases,
                e.g. "[Chef Junior] Unknown role: 'Chef'. ...". Empty if all is fine.
    """
    path = Path(path)
    if not path.exists():
        return [], [f"Test case file not found: {path}"]

    config = configparser.ConfigParser()
    try:
        config.read(path, encoding="utf-8")
    except configparser.Error as error:
        return [], [f"The test case file could not be read: {error}"]

    cases, problems = [], []
    for name in config.sections():
        section = config[name]
        role = section.get("role", "").strip()
        level = section.get("level", "").strip()
        error = validate_role_and_level(role, level)
        if error:
            problems.append(f"[{name}] {error}")
            continue
        topics = section.get("expected_topics", "")
        cases.append({
            "name": name,
            "role": role,
            "level": level,
            "note": section.get("note", "").strip(),
            "expected_topics": [topic.strip() for topic in topics.split(",") if topic.strip()],
        })
    if not cases and not problems:
        problems.append(f"The test case file has no test cases: {path}")
    return cases, problems


def measure_questions(questions, expected_topics=()):
    """Measure a set of questions, without AI: length, packed questions, behavioral ones, topics.

    The behavioral and topic counts are keyword heuristics, so they are estimates.

    Args:
        questions: the questions (list of str).
        expected_topics: topics good questions should cover, e.g. ["bug reports", "SQL"].

    Returns:
        A dict:
            "count": number of questions
            "avg_words": average words per question (float)
            "multi_part": questions with more than one sentence (several questions or
                tasks in one, e.g. "How do you ...? Give an example.")
            "behavioral": questions with a phrase like "Tell me about a time ..."
            "topics_covered": the expected topics found in the questions (list of str)
            "topics_missing": the expected topics not found (list of str)
    """
    texts = [question.lower() for question in questions]
    all_text = " ".join(texts)
    covered = [topic for topic in expected_topics if topic_covered(topic, all_text)]
    return {
        "count": len(questions),
        "avg_words": sum(len(q.split()) for q in questions) / len(questions) if questions else 0.0,
        "multi_part": sum(1 for text in texts if sentence_count(text) > 1),
        "behavioral": sum(1 for text in texts if any(phrase in text for phrase in BEHAVIORAL_PHRASES)),
        "topics_covered": covered,
        "topics_missing": [topic for topic in expected_topics if topic not in covered],
    }


def sentence_count(text):
    """Count the sentences in a text; abbreviations like "e.g." or "vs." don't end a sentence.

    Args:
        text: one question.

    Returns:
        The number of sentences (int), at least 1 for a non-empty text.
    """
    text = re.sub(r"\b(e\.g|i\.e|vs|etc)\.", "", text.lower())
    return len([part for part in re.split(r"[.?!]+(?:\s+|$)", text) if part.strip()])


def topic_covered(topic, text):
    """Check whether a topic appears in a text, by the start of its words.

    Each word of the topic (without small words like "and" or "vs.") is looked for with its
    first 4 letters, so "automated testing" matches "automate tests" and "teamwork" matches
    "team". The topic counts as covered if at least half of its words are found, so a filler
    word like "basics" in "test automation basics" doesn't decide it.

    Args:
        topic: the topic, e.g. "manual vs. automated testing".
        text: the text to search, in lower case.

    Returns:
        True if at least half of the topic's words are found, otherwise False.
    """
    words = [word for word in re.findall(r"[a-z0-9+#/]+", topic.lower()) if word not in TOPIC_STOPWORDS]
    found = sum(1 for word in words if word[:4] in text)
    return bool(words) and found * 2 >= len(words)


def judge_questions(case, questions, model=JUDGE_DEFAULT_MODEL):
    """Let an AI judge score a set of questions with the rubric (LLM-as-judge).

    The judge gets the role, the level, the expected topics and the questions, but not
    the technique that wrote them, so it can't favor one. Temperature 0, so the same
    questions get the same scores as far as possible.

    Args:
        case: the test case dict from load_test_cases().
        questions: the questions to score (list of str).
        model: the judge's OpenRouter model ID.

    Returns:
        A dict {criterion key: {"score": 1 to 5, "reason": str}} for every key in RUBRIC_KEYS.

    Raises:
        ValueError: there are no questions, or the judge's reply has no valid score
            (1 to 5) for a criterion; or an error from the LLM call (see
            LLMClient.complete_json, e.g. the rate limit).
    """
    if not questions:
        raise ValueError("There are no questions to judge.")
    rubric_text = "\n".join(
        f"- {c['key']} ({c['label']}): {c['question']}\n"
        f"  1 = {c['anchors'][1]}\n  3 = {c['anchors'][3]}\n  5 = {c['anchors'][5]}"
        for c in RUBRIC
    )
    system_prompt = load_prompt("prompt_lab_judge").replace("{rubric}", rubric_text)
    topics = ", ".join(case["expected_topics"]) or "(none given)"
    numbered = "\n".join(f"Q{number}. {question}" for number, question in enumerate(questions, start=1))
    user_prompt = f"Role: {case['role']}\nLevel: {case['level']}\nExpected topics: {topics}\n\nQuestions:\n{numbered}"
    reply = LLMClient(model=model, temperature=0, max_tokens=4000).complete_json(system_prompt, user_prompt)

    verdict = {}
    for key in RUBRIC_KEYS:
        item = reply.get(key) if isinstance(reply.get(key), dict) else {}
        score = item.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
            raise ValueError(f"The AI judge gave no valid score (1 to 5) for {key!r}: {score!r}")
        verdict[key] = {"score": score, "reason": str(item.get("reason", "")).strip()}
    return verdict


def score_row(case, model, technique, result, scores, saved_at, judge=None, judge_model=""):
    """Build one row for scores.csv from a technique's result, the developer's and the judge's scores.

    Args:
        case: the test case dict from load_test_cases().
        model: the model ID that wrote the questions, e.g. "openai/gpt-5-mini".
        technique: the technique key, e.g. "few_shot".
        result: {"questions", "seconds"} from the run.
        scores: the developer's {criterion key: score 1 to 5} for every key in
            RUBRIC_KEYS, or None if the developer did not score this technique.
        saved_at: the time of saving, e.g. "2026-10-01 14:30".
        judge: the judge's verdict from judge_questions(), or None.
        judge_model: the judge's model ID ("" without a judge).

    Returns:
        A dict with one value per column in SCORE_COLUMNS; the columns of a side
        that did not score are None (empty in the CSV).
    """
    measured = measure_questions(result["questions"], case["expected_topics"])
    return {
        "saved_at": saved_at,
        "case": case["name"],
        "role": case["role"],
        "level": case["level"],
        "model": model,
        "technique": technique,
        **{key: scores[key] if scores else None for key in RUBRIC_KEYS},
        "total": sum(scores[key] for key in RUBRIC_KEYS) if scores else None,
        "judge_model": judge_model if judge else "",
        **{f"judge_{key}": judge[key]["score"] if judge else None for key in RUBRIC_KEYS},
        "judge_total": sum(judge[key]["score"] for key in RUBRIC_KEYS) if judge else None,
        "questions": measured["count"],
        "avg_words": round(measured["avg_words"], 1),
        "multi_part": measured["multi_part"],
        "behavioral": measured["behavioral"],
        "topics_covered": len(measured["topics_covered"]),
        "topics_expected": len(case["expected_topics"]),
        "seconds": round(result["seconds"], 1),
        "question_texts": " | ".join(result["questions"]),
    }


def save_scores(rows, path=SCORES_FILE):
    """Append rows to scores.csv; the file and its header line are created the first time.

    Args:
        rows: dicts from score_row().
        path: the CSV file; only the tests pass another one.
    """
    path = Path(path)
    new_file = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: Excel then reads characters like ä or – correctly.
    with path.open("a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=SCORE_COLUMNS)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)


def load_scores(path=SCORES_FILE):
    """Read all saved scores from scores.csv.

    Args:
        path: the CSV file; only the tests pass another one.

    Returns:
        A list of dicts, one per saved row, with the number columns as int or
        float, and None where a side did not score; empty if the file does not exist yet.
    """
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            for column in INT_COLUMNS:
                row[column] = int(row[column]) if row.get(column) else None
            for column in FLOAT_COLUMNS:
                row[column] = float(row[column]) if row.get(column) else None
            rows.append(row)
    return rows
