# Feature 3: Job description analyzer.
# Step 2: the LLM turns the job description text into structured data
# (basic info, role metadata, exact skills). Red/green flags come later,
# then qa_generator (1) and interviewer_questions (2) are reused.

from server.guards.input_validation import image_type, validate_images, validate_job_description
from server.llm import LLMClient
from server.prompt_loader import load_prompt

# Reading a screenshot always uses this vision model, whatever is chosen in the sidebar:
# it reads text from images well and is cheap. Temperature 0: copy, don't be creative.
SCREENSHOT_MODEL = "google/gemini-2.5-flash"
SCREENSHOT_MAX_TOKENS = 8000  # a long job posting is about 2,000-3,000 tokens

# Allowed values, the same lists as in prompts/job_analyzer.md.
SENIORITY_LEVELS = ["Junior", "Mid", "Senior", "Staff", "Lead"]
WORK_MODES = ["Remote", "Hybrid", "Onsite"]
SKILL_GROUPS = ["hard_skills", "concepts", "soft_skills"]


def analyze_job_description(text, settings=None):
    """Turn a job description into structured data with the LLM (feature 3).

    Values the model returns outside the allowed lists (work_mode, seniority)
    become None, and all skill lists are cleaned with clean_list().

    Args:
        text: the job description, pasted or read from a screenshot.
        settings: the LLM settings from the sidebar ({"model", "temperature",
            "max_tokens"}), or None for the defaults in llm.py.

    Returns:
        A dict with 4 parts (the fields are explained in prompts/job_analyzer.md):
            "basic_info": job_title, company, location, work_mode, employment_type
            "role_metadata": seniority, seniority_reason, role_focus, role_focus_reason
            "skills": {group: {"required": [...], "nice_to_have": [...]}} for
                each group in SKILL_GROUPS
            "other_requirements": a list of str, e.g. degree or languages

    Raises:
        ValueError: the text is empty, too short or too long (guard 1, before
            the LLM call), or an error from the LLM call (see LLMClient.complete_json).
    """
    error = validate_job_description(text)  # guard 1, before the paid call
    if error:
        raise ValueError(error)
    system_prompt = load_prompt("job_analyzer")
    user_prompt = f"Job description:\n\n{text}"
    reply = LLMClient(**(settings or {})).complete_json(system_prompt, user_prompt)

    # The model can still break the rules; a value outside the list becomes None ("not detected").
    basic_info = reply.get("basic_info", {})
    role_metadata = reply.get("role_metadata", {})
    if basic_info.get("work_mode") not in WORK_MODES:
        basic_info["work_mode"] = None
    if role_metadata.get("seniority") not in SENIORITY_LEVELS:
        role_metadata["seniority"] = None

    # Every skill group always has both lists, so the page never has to check.
    raw_skills = reply.get("skills", {})
    skills = {
        group: {
            "required": clean_list(raw_skills.get(group, {}).get("required")),
            "nice_to_have": clean_list(raw_skills.get(group, {}).get("nice_to_have")),
        }
        for group in SKILL_GROUPS
    }
    return {
        "basic_info": basic_info,
        "role_metadata": role_metadata,
        "skills": skills,
        "other_requirements": clean_list(reply.get("other_requirements")),
    }


def read_job_screenshots(images):
    """Copy the text of a job posting out of one or more screenshots with a vision model.

    All screenshots go to the model in one call, in reading order, so it can
    join them into one text: it copies text where they overlap only once and
    leaves gaps between them as they are (see prompts/jd_image_reader.md).
    Always uses SCREENSHOT_MODEL (Gemini 2.5 Flash) at temperature 0, whatever
    is chosen in the sidebar. The caller then analyzes the text like pasted
    text, with analyze_job_description().

    Args:
        images: the images as a list of bytes (PNG, JPG or WebP), in reading
            order, e.g. [title_screenshot, tasks_screenshot].

    Returns:
        The text of the job posting (str), with broken lines joined by
        join_wrapped_lines().

    Raises:
        ValueError: no images, too many, one is not an image or too big, or all
            are too big together (guard 1, before the LLM call); the images do
            not show a job posting; or an error from the LLM call (see
            LLMClient.complete_json).
    """
    error = validate_images(images)  # guard 1, before the paid call
    if error:
        raise ValueError(error)
    system_prompt = load_prompt("jd_image_reader")
    client = LLMClient(model=SCREENSHOT_MODEL, temperature=0, max_tokens=SCREENSHOT_MAX_TOKENS)
    count = len(images)
    request = (
        "Copy the text of the job posting in this screenshot."
        if count == 1
        else f"Copy the text of the job posting in these {count} screenshots. "
        f"They are parts of one posting, in reading order (1 to {count})."
    )
    reply = client.complete_json(
        system_prompt,
        request,
        images=[(data, image_type(data)) for data in images],
    )
    if not reply.get("is_job_posting"):
        raise ValueError("The screenshots do not seem to show a job posting.")
    return join_wrapped_lines((reply.get("text") or "").strip())


def join_wrapped_lines(text):
    """Join lines that were only broken because the screen was too narrow.

    Vision models often keep the screen's line breaks in the middle of a
    sentence ("...combined with professional" / "experience in..."), even when
    the prompt asks them not to. A line is added to the line before only if it
    goes on with a lowercase letter, like the rest of a sentence does. Lines
    that start with a capital letter, a digit or "- " (a list item) stay on
    their own, so a title, a company line and a salary line are not glued
    together. Words are never changed.

    Args:
        text: the text read from a screenshot.

    Returns:
        The text (str) with each broken sentence on one line.
    """
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line and lines and lines[-1] and line[0].islower():
            lines[-1] += " " + line
        else:
            lines.append(line)
    return "\n".join(lines)


def clean_list(items):
    """Clean a list from the model's reply: only non-empty strings, no duplicates.

    Args:
        items: the list from the reply; None or other types are allowed.

    Returns:
        A new list of str, stripped of spaces, in the original order. Empty if
        items is None.
    """
    result = []
    for item in items or []:
        if isinstance(item, str) and item.strip() and item.strip() not in result:
            result.append(item.strip())
    return result
