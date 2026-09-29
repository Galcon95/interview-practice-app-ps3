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

from server.features import qa_generator, interviewer_questions  # noqa: E402 (import after the path fix)


def generate_questions(role, level):
    # Feature 1: returns a list of 5 questions for the role and level.
    return qa_generator.generate_questions(role, level)


def generate_interviewer_questions(role, level):
    # Feature 2: returns 5 dicts {"category", "question"} to ask the interviewer.
    return interviewer_questions.generate_interviewer_questions(role, level)


# TODO: analyze_job_description(text)                 -> feature 3
# TODO: polish_introduction(text)                     -> feature 4
# TODO: match_resume(resume_file, job_description)    -> feature 5
