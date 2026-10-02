# The only file in client/ that talks to the back end (server/).
# Pages call these functions and never import from server/ themselves.
# Right now the calls are direct Python imports. If the server ever becomes
# a real API (FastAPI), only this file changes.

import sys
from pathlib import Path

# "streamlit run client/app.py" only lets Python find files inside client/.
# Adding the project root makes the server/ package importable.
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from server import llm, prompt_lab, prompt_loader  # noqa: E402 (import after the path fix)
from server.features import qa_generator, interviewer_questions, job_analyzer  # noqa: E402
from server.guards import GUARDS, input_validation  # noqa: E402


def get_models():
    """Get the models the user can choose in the settings sidebar.

    Returns:
        A dict {model_id: {"label": str, "temperature": bool}}, e.g.
        {"openai/gpt-5-mini": {"label": "GPT-5 mini ($0.25 / $2)", "temperature": False}}.
        "temperature" says whether the model supports that setting.
    """
    return llm.MODELS


def get_default_settings():
    """Get the server's default LLM settings, used as start values in the sidebar.

    Returns:
        A dict {"model": str, "temperature": float, "max_tokens": int}.
    """
    return {
        "model": llm.DEFAULT_MODEL,
        "temperature": llm.DEFAULT_TEMPERATURE,
        "max_tokens": llm.DEFAULT_MAX_TOKENS,
    }



def get_guard_status():
    """Get which security guards are built and running, for the status shown on the pages.

    Returns:
        A dict {guard name (str): active (bool)}, e.g. {"Input validation": True, ...},
        in the order of the guards (1 to 4).
    """
    return dict(GUARDS)


def get_roles_and_levels():
    """Get the IT roles and levels the server accepts, for the dropdowns on the Role Q&A page.

    Returns:
        A tuple (roles, levels): two lists of str, e.g. ["Frontend Developer", ...]
        and ["Junior", "Mid", "Senior", "Lead"].
    """
    return input_validation.IT_ROLES, input_validation.LEVELS


def generate_questions(role, level, settings=None):
    """Generate interview questions for a role and level (feature 1).

    Args:
        role: the IT role, one of the roles from get_roles_and_levels().
        level: the seniority level, one of the levels from get_roles_and_levels().
        settings: the LLM settings from the sidebar ({"model", "temperature",
            "max_tokens"}), or None for the server's defaults.

    Returns:
        A list of 5 questions (str).

    Raises:
        ValueError: the role or level is not allowed, the request is out of
            scope, or there were too many requests. Other errors of the LLM call
            are passed on as well.
    """
    return qa_generator.generate_questions(role, level, settings)


def generate_interviewer_questions(role, level, settings=None):
    """Generate questions to ask the interviewer, for a role and level (feature 2).

    Args:
        role: the IT role, one of the roles from get_roles_and_levels().
        level: the seniority level, one of the levels from get_roles_and_levels().
        settings: the LLM settings from the sidebar ({"model", "temperature",
            "max_tokens"}), or None for the server's defaults.

    Returns:
        A list of 5 dicts: {"category": "Tech stack", "question": "..."}.

    Raises:
        ValueError: the role or level is not allowed, the request is out of
            scope, or there were too many requests. Other errors of the LLM call
            are passed on as well.
    """
    return interviewer_questions.generate_interviewer_questions(role, level, settings)


def validate_job_description(text):
    """Check a job description before analyzing it, without calling the LLM (guard 1).

    Lets the page show the error at once. analyze_job_description() checks
    again on the server, so this check is a convenience, not the guard itself.

    Args:
        text: the job description from the text box.

    Returns:
        An error message (str), or None if the text can be analyzed.
    """
    return input_validation.validate_job_description(text)


def get_job_description_limits():
    """Get the allowed length of a job description, to show it on the page.

    Returns:
        A tuple (min_chars, max_chars) of int, e.g. (200, 15000).
    """
    return input_validation.JD_MIN_CHARS, input_validation.JD_MAX_CHARS


def validate_screenshots(images):
    """Check the screenshots of one job posting before storing them, without calling the LLM (guard 1).

    Args:
        images: the images as a list of bytes, in reading order (pasted or uploaded).

    Returns:
        An error message (str), or None if every image is a PNG, JPG or WebP
        file within the limits (see get_screenshot_limits()).
    """
    return input_validation.validate_images(images)


def get_screenshot_limits():
    """Get the screenshot limits, for the uploader and the page.

    Returns:
        A dict {"max_mb": int, "max_count": int, "max_total_mb": int}: the size
        of one screenshot, the number of screenshots, and their size together.
    """
    return {
        "max_mb": input_validation.IMAGE_MAX_MB,
        "max_count": input_validation.IMAGE_MAX_COUNT,
        "max_total_mb": input_validation.IMAGES_MAX_TOTAL_MB,
    }


def read_job_screenshots(images):
    """Read the text of a job posting from one or more screenshots (feature 3, screenshot input).

    All screenshots go to the model in one call, so it can join them into one
    text. Always uses the fixed vision model (job_analyzer.SCREENSHOT_MODEL),
    not the sidebar settings.

    Args:
        images: the images as a list of bytes (PNG, JPG or WebP), in reading order.

    Returns:
        The text of the job posting (str).

    Raises:
        ValueError: the images are not allowed, do not show a job posting, the
            request is out of scope, or there were too many requests. Other
            errors of the LLM call are passed on as well.
    """
    return job_analyzer.read_job_screenshots(images)


def analyze_job_description(text, settings=None):
    """Analyze a job description with the LLM (feature 3).

    Args:
        text: the job description, pasted or read from a screenshot.
        settings: the LLM settings from the sidebar ({"model", "temperature",
            "max_tokens"}), or None for the server's defaults.

    Returns:
        A dict {"basic_info", "role_metadata", "skills", "other_requirements"}
        (see server/features/job_analyzer.py for the fields).

    Raises:
        ValueError: the text is empty, too short or too long, the request is out
            of scope, or there were too many requests. Other errors of the LLM
            call are passed on as well.
    """
    return job_analyzer.analyze_job_description(text, settings)


# Features that have several prompt techniques (Prompt Lab, developer mode only):
# feature name -> (server module, prompt folder in server/prompts/).
PROMPT_LAB_FEATURES = {
    "role_qa": (qa_generator, "qa_generator"),
}


def get_prompt_techniques(feature):
    """Get the prompt techniques of a feature, for the Prompt Lab.

    Args:
        feature: a key of PROMPT_LAB_FEATURES, e.g. "role_qa" (interview questions).

    Returns:
        A dict {technique: {"label": str, "description": str, "default": bool}},
        in the order 1 to 5; "default" is True for the one the app uses.
    """
    module, _ = PROMPT_LAB_FEATURES[feature]
    return {
        key: {**info, "default": key == module.DEFAULT_TECHNIQUE}
        for key, info in module.TECHNIQUES.items()
    }


def get_prompt_text(feature, technique):
    """Get the system prompt of one technique, as the model receives it (with the guardrail).

    Args:
        feature: a key of PROMPT_LAB_FEATURES, e.g. "role_qa".
        technique: a key of get_prompt_techniques(feature), e.g. "few_shot".

    Returns:
        The full system prompt (str).
    """
    _, folder = PROMPT_LAB_FEATURES[feature]
    return prompt_loader.load_prompt(f"{folder}/{technique}")


def get_prompt_lab_test_cases():
    """Get the Prompt Lab's test cases from prompt_lab/test_cases.ini (read fresh on every call).

    Returns:
        A tuple (cases, problems): the valid cases as dicts {"name", "role",
        "level", "note", "expected_topics"}, and messages (str) about skipped
        cases or a missing file. See server/prompt_lab.py.
    """
    return prompt_lab.load_test_cases()


def get_rubric():
    """Get the Prompt Lab's rubric: the criteria the developer scores from 1 to 5.

    Returns:
        A list of dicts {"key", "label", "question", "anchors"}; "anchors" says
        what a 1, a 3 and a 5 mean. See server/prompt_lab.py.
    """
    return prompt_lab.RUBRIC


def measure_questions(questions, expected_topics=()):
    """Measure a set of questions without AI (length, packed questions, behavioral ones, topics).

    Args:
        questions: the questions (list of str).
        expected_topics: the test case's expected topics (list of str).

    Returns:
        A dict {"count", "avg_words", "multi_part", "behavioral", "topics_covered",
        "topics_missing"}. See server/prompt_lab.measure_questions.
    """
    return prompt_lab.measure_questions(questions, expected_topics)


def save_lab_scores(case, model, results, scores, saved_at, judgments=None, judge_model=""):
    """Append the scores of one Prompt Lab run to prompt_lab/scores.csv.

    A technique is saved if the developer scored it fully or the AI judge scored it.

    Args:
        case: the test case dict from get_prompt_lab_test_cases().
        model: the model ID that wrote the questions.
        results: {technique: {"questions", "seconds", ...}} from the run.
        scores: the developer's {technique: {criterion key: score 1 to 5}}.
        saved_at: the time of saving, e.g. "2026-10-01 14:30".
        judgments: the judge's {technique: verdict from judge_questions()}, or None.
        judge_model: the judge's model ID.

    Returns:
        The number of rows saved (int).
    """
    judgments = judgments or {}
    techniques = [key for key in results if key in scores or key in judgments]
    rows = [
        prompt_lab.score_row(
            case, model, key, results[key], scores.get(key), saved_at,
            judge=judgments.get(key), judge_model=judge_model,
        )
        for key in techniques
    ]
    prompt_lab.save_scores(rows)
    return len(rows)


def get_judge_default_model():
    """Get the default model of the AI judge (from another model family than the default writer).

    Returns:
        The OpenRouter model ID (str).
    """
    return prompt_lab.JUDGE_DEFAULT_MODEL


def judge_questions(case, questions, model):
    """Let the AI judge score one technique's questions with the rubric (LLM-as-judge).

    Args:
        case: the test case dict from get_prompt_lab_test_cases().
        questions: the questions (list of str).
        model: the judge's model ID.

    Returns:
        {criterion key: {"score": 1 to 5, "reason": str}}. See server/prompt_lab.judge_questions.

    Raises:
        ValueError: no questions, an invalid reply, or the rate limit; other
            errors of the LLM call are passed on as well.
    """
    return prompt_lab.judge_questions(case, questions, model)


def load_lab_scores():
    """Read all saved Prompt Lab scores from prompt_lab/scores.csv.

    Returns:
        A list of dicts, one per saved technique and run (see server/prompt_lab.SCORE_COLUMNS);
        empty if nothing is saved yet.
    """
    return prompt_lab.load_scores()


def generate_questions_with_technique(role, level, settings=None, technique=None):
    """Generate interview questions with a chosen prompt technique (Prompt Lab).

    Args:
        role: the IT role, one of the roles from get_roles_and_levels().
        level: the seniority level, one of the levels from get_roles_and_levels().
        settings: the LLM settings from the sidebar, or None for the server's defaults.
        technique: a key of get_prompt_techniques("role_qa"), or None for the default.

    Returns:
        A dict {"questions": list of str, "reasoning": str or None}.

    Raises:
        ValueError: the role, level or technique is not allowed, the request is
            out of scope, or there were too many requests. Other errors of the
            LLM call are passed on as well.
    """
    technique = technique or qa_generator.DEFAULT_TECHNIQUE
    return qa_generator.generate_questions_with_technique(role, level, settings, technique=technique)


# TODO: polish_introduction(text)                     -> feature 4
# TODO: match_resume(resume_file, job_description)    -> feature 5
