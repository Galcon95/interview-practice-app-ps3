# Guard 1: Input validation.
# Runs before the API call, so bad input never costs money
# (empty text, too long, wrong file type, ...).

# Role Q&A: the only roles and levels the app supports (IT jobs only).
# The dropdowns on the page show these lists, and the server checks against them,
# because widget limits are only enforced in the browser.
IT_ROLES = [
    "Frontend Developer",
    "Backend Developer",
    "Full-Stack Developer",
    "DevOps / SRE",
    "Data / AI Engineer",
    "QA Engineer",
]
LEVELS = ["Junior", "Mid", "Senior", "Lead"]

# Job descriptions: shorter than this is not a real JD, longer is too expensive.
JD_MIN_CHARS = 200
JD_MAX_CHARS = 15000


# Screenshots: bigger images cost more and are not needed to read a job posting.
# One posting can be split over several screenshots (e.g. the title and the tasks).
IMAGE_MAX_MB = 5            # per screenshot
IMAGE_MAX_COUNT = 5         # screenshots per job posting
IMAGES_MAX_TOTAL_MB = 15    # all screenshots of one posting together

# The first bytes of a file show its real type (a renamed .exe stays an .exe).
IMAGE_SIGNATURES = {
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"\xff\xd8\xff": "image/jpeg",
}


def image_type(data):
    """Find the real type of an image from its first bytes (its "magic number").

    The file name is never used, so a program renamed to "job.png" is not
    taken for an image.

    Args:
        data: the file content as bytes.

    Returns:
        "image/png", "image/jpeg" or "image/webp", or None if the bytes are
        none of these types.
    """
    for signature, mime_type in IMAGE_SIGNATURES.items():
        if data.startswith(signature):
            return mime_type
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def validate_image(data, name="The image"):
    """Check that an image is a real PNG, JPG or WebP file of at most IMAGE_MAX_MB (guard 1).

    The checks run in this order, and the first problem found is returned:
    empty, wrong type, too big.

    Args:
        data: the file content as bytes.
        name: how the image is called in the error message, e.g. "The screenshot".

    Returns:
        An error message (str) for the user, or None if the image is fine.
    """
    if not data:
        return f"{name} is empty."
    if image_type(data) is None:
        return f"{name} is not a PNG, JPG or WebP image."
    size_mb = len(data) / (1024 * 1024)
    if size_mb > IMAGE_MAX_MB:
        return f"{name} is too big ({size_mb:.1f} MB, at most {IMAGE_MAX_MB} MB allowed)."
    return None


def validate_images(images):
    """Check the screenshots of one job posting, each on its own and all together (guard 1).

    The checks run in this order, and the first problem found is returned:
    no images, too many, each image (see validate_image), too big together.

    Args:
        images: the images as a list of bytes, in reading order.

    Returns:
        An error message (str) for the user, or None if the images are fine.
        Messages about one image name its number, e.g. "Screenshot 2 is too big (...)".
    """
    if not images:
        return "No screenshot added."
    if len(images) > IMAGE_MAX_COUNT:
        return f"Too many screenshots ({len(images)}, at most {IMAGE_MAX_COUNT} allowed)."
    for number, data in enumerate(images, start=1):
        error = validate_image(data, name=f"Screenshot {number}")
        if error:
            return error
    total_mb = sum(len(data) for data in images) / (1024 * 1024)
    if total_mb > IMAGES_MAX_TOTAL_MB:
        return (
            f"The screenshots are too big together ({total_mb:.1f} MB, "
            f"at most {IMAGES_MAX_TOTAL_MB} MB allowed)."
        )
    return None


def validate_role_and_level(role, level):
    """Check that the role and the level are in the allowed lists (guard 1).

    The page only offers dropdowns, but widget limits are only enforced in the
    browser, so the server checks again. The comparison is exact (case matters).

    Args:
        role: the IT role, must be one of IT_ROLES, e.g. "QA Engineer".
        level: the seniority level, must be one of LEVELS, e.g. "Junior".

    Returns:
        An error message (str) that lists the allowed values, or None if both are fine.
    """
    if role not in IT_ROLES:
        return f"Unknown role: {role!r}. Choose one of: {', '.join(IT_ROLES)}."
    if level not in LEVELS:
        return f"Unknown level: {level!r}. Choose one of: {', '.join(LEVELS)}."
    return None


def validate_job_description(text):
    """Check the length of a job description (guard 1).

    Args:
        text: the job description, pasted or read from a screenshot.

    Returns:
        An error message (str), or None if the text has JD_MIN_CHARS to
        JD_MAX_CHARS characters.
    """
    return validate_input(text, JD_MIN_CHARS, JD_MAX_CHARS, name="The job description")


def validate_input(text, min_chars, max_chars, name="Text"):
    """Check that a text is not empty and has a length between two limits (guard 1).

    Spaces and line breaks at the start and end don't count. The checks run in
    this order, and the first problem found is returned: empty, too short, too long.

    Args:
        text: the text to check; None counts as empty.
        min_chars: the smallest number of characters allowed.
        max_chars: the largest number of characters allowed.
        name: how the text is called in the error message, e.g. "The job description".

    Returns:
        An error message (str) for the user, or None if the text is fine.
    """
    text = (text or "").strip()
    if not text:
        return f"{name} is empty."
    if len(text) < min_chars:
        return f"{name} is too short ({len(text)} characters, at least {min_chars} needed)."
    if len(text) > max_chars:
        return f"{name} is too long ({len(text)} characters, at most {max_chars} allowed)."
    return None
