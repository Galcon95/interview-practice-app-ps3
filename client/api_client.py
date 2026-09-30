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

from server import llm  # noqa: E402 (import after the path fix)
from server.features import qa_generator, interviewer_questions, job_analyzer  # noqa: E402
from server.guards import input_validation  # noqa: E402

# settings (in all functions below): {"model", "temperature", "max_tokens"}
# from the sidebar, or None for the server's defaults.


def get_models():
    # Models for the settings panel: {model_id: {"label", "temperature"}}
    return llm.MODELS


def get_default_settings():
    return {
        "model": llm.DEFAULT_MODEL,
        "temperature": llm.DEFAULT_TEMPERATURE,
        "max_tokens": llm.DEFAULT_MAX_TOKENS,
    }


def generate_questions(role, level, settings=None):
    # Feature 1: returns a list of 5 questions for the role and level.
    return qa_generator.generate_questions(role, level, settings)


def generate_interviewer_questions(role, level, settings=None):
    # Feature 2: returns 5 dicts {"category", "question"} to ask the interviewer.
    return interviewer_questions.generate_interviewer_questions(role, level, settings)


def validate_job_description(text):
    # Feature 3, step 1: returns an error message, or None if the JD can be analyzed.
    return input_validation.validate_input(
        text,
        input_validation.JD_MIN_CHARS,
        input_validation.JD_MAX_CHARS,
        name="The job description",
    )


def get_job_description_limits():
    # (min, max) characters, so the page can show them to the user.
    return input_validation.JD_MIN_CHARS, input_validation.JD_MAX_CHARS


def validate_screenshot(data):
    # Feature 3, screenshot input: returns an error message, or None if the image can be used.
    return input_validation.validate_image(data, name="The screenshot")


def get_screenshot_max_mb():
    return input_validation.IMAGE_MAX_MB


def read_job_screenshot(data):
    # Feature 3, screenshot input: returns the text of the job posting in the image.
    # Always uses the fixed vision model (job_analyzer.SCREENSHOT_MODEL), not the sidebar settings.
    return job_analyzer.read_job_screenshot(data)


def analyze_job_description(text, settings=None):
    # Feature 3, step 2: returns {"basic_info", "role_metadata", "skills", "other_requirements"}.
    return job_analyzer.analyze_job_description(text, settings)


# TODO: polish_introduction(text)                     -> feature 4
# TODO: match_resume(resume_file, job_description)    -> feature 5
