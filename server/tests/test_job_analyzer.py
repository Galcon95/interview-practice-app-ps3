# Tests for the helper functions in server/features/job_analyzer.py.
# No LLM calls. Run from the project root: py -3.13 -m pytest

from server.features.job_analyzer import clean_list, join_wrapped_lines


# --- join_wrapped_lines: fix line breaks that only came from the screen width ---

def test_a_sentence_broken_by_the_screen_is_joined():
    """A line that goes on with a lowercase letter is added to the line before."""
    text = "- Degree in computer science, combined with professional\nexperience in embedded software."
    assert join_wrapped_lines(text) == (
        "- Degree in computer science, combined with professional experience in embedded software."
    )


def test_lines_of_a_title_block_stay_separate():
    """Title, company and salary lines start with a capital letter, so they are not glued together."""
    text = "Senior Backend Engineer (Python)\nCloudCart GmbH · Berlin\nSalary: 75,000 EUR"
    assert join_wrapped_lines(text) == text


def test_list_items_stay_separate():
    """Each "- " list item stays on its own line."""
    text = "- Python\n- FastAPI\n- PostgreSQL"
    assert join_wrapped_lines(text) == text


def test_a_line_starting_with_a_digit_stays_separate():
    """A line that starts with a digit (e.g. "5+ years") is a new line, not the rest of a sentence."""
    text = "Your profile\n5+ years of experience with Python"
    assert join_wrapped_lines(text) == text


def test_empty_lines_between_sections_are_kept():
    """Empty lines (between sections or between screenshots) are never removed or joined over."""
    text = "Your tasks\n\n- Write tests\n\nYour profile"
    assert join_wrapped_lines(text) == text


def test_words_are_never_changed():
    """Joining only changes line breaks: the words stay exactly the same."""
    text = "Strong analytical skills, enabling you to understand\ncomplex system-wide relationships\nand communicate them\nclearly."
    assert join_wrapped_lines(text).split() == text.split()
    assert join_wrapped_lines(text).count("\n") == 0


# --- clean_list: tidy up lists from the model's reply ---

def test_clean_list_removes_empty_values_and_duplicates():
    """Empty strings, non-strings and duplicates are removed; spaces are stripped; order is kept."""
    assert clean_list(["C++", " Python ", "", None, 3, "C++", "Python"]) == ["C++", "Python"]


def test_clean_list_accepts_none():
    """None (a missing list in the reply) becomes an empty list."""
    assert clean_list(None) == []
