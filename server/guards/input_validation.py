# Guard 1: Input validation.
# Runs before the API call, so bad input never costs money
# (empty text, too long, wrong file type, ...).

# Job descriptions: shorter than this is not a real JD, longer is too expensive.
JD_MIN_CHARS = 200
JD_MAX_CHARS = 15000


# Screenshots: bigger images cost more and are not needed to read a job posting.
IMAGE_MAX_MB = 5

# The first bytes of a file show its real type (a renamed .exe stays an .exe).
IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


def image_type(data):
    # Returns "image/png", "image/jpeg", "image/webp", or None for anything else.
    for signature, mime_type in IMAGE_SIGNATURES.items():
        if data.startswith(signature):
            return mime_type
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def validate_image(data, name="The image"):
    # Returns an error message (string), or None if the image is fine.
    if not data:
        return f"{name} is empty."
    if image_type(data) is None:
        return f"{name} is not a PNG, JPG or WebP image."
    size_mb = len(data) / (1024 * 1024)
    if size_mb > IMAGE_MAX_MB:
        return f"{name} is too big ({size_mb:.1f} MB, at most {IMAGE_MAX_MB} MB allowed)."
    return None


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
