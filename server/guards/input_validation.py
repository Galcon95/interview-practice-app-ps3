# Guard 1: Input validation.
# Runs before the API call, so bad input never costs money
# (empty text, too long, wrong file type, ...).

# Job descriptions: shorter than this is not a real JD, longer is too expensive.
JD_MIN_CHARS = 200
JD_MAX_CHARS = 15000


def validate_input(text, min_chars, max_chars, name="Text"):
    # Returns an error message (string), or None if the text is fine.
    text = (text or "").strip()
    if not text:
        return f"{name} is empty."
    if len(text) < min_chars:
        return f"{name} is too short ({len(text)} characters, at least {min_chars} needed)."
    if len(text) > max_chars:
        return f"{name} is too long ({len(text)} characters, at most {max_chars} allowed)."
    return None
