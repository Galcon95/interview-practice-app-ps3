# Feature 3: Job description analyzer.
# Step 2: the LLM turns the job description text into structured data
# (basic info, role metadata, exact skills). Red/green flags come later,
# then qa_generator (1) and interviewer_questions (2) are reused.

from server.guards.input_validation import image_type
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
    # Returns {"basic_info", "role_metadata", "skills", "other_requirements"} (see the prompt).
    #   skills: {group: {"required": [...], "nice_to_have": [...]}} for each group in SKILL_GROUPS
    # settings: {"model", "temperature", "max_tokens"} from the sidebar, or None for defaults
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


def read_job_screenshot(data):
    # Step 1 (screenshot input): the vision model copies the text out of the image.
    # Returns the text; the caller then analyzes it like pasted text.
    # data: the image bytes, already checked by guards/input_validation.validate_image
    system_prompt = load_prompt("jd_image_reader")
    client = LLMClient(model=SCREENSHOT_MODEL, temperature=0, max_tokens=SCREENSHOT_MAX_TOKENS)
    reply = client.complete_json(
        system_prompt,
        "Copy the text of the job posting in this screenshot.",
        images=[(data, image_type(data))],
    )
    if not reply.get("is_job_posting"):
        raise ValueError("The screenshot does not seem to show a job posting.")
    return join_wrapped_lines((reply.get("text") or "").strip())


def join_wrapped_lines(text):
    # Vision models often keep the line breaks of the screen ("...combined with professional
    # \nexperience in..."), even when the prompt asks them not to, so we fix it here:
    # a line that is not empty and does not start a list item ("- ") continues the line before.
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if line and lines and lines[-1] and not line.startswith("- "):
            lines[-1] += " " + line
        else:
            lines.append(line)
    return "\n".join(lines)


def clean_list(items):
    # Keeps non-empty strings, without duplicates, in their original order.
    result = []
    for item in items or []:
        if isinstance(item, str) and item.strip() and item.strip() not in result:
            result.append(item.strip())
    return result
