# Guard 1: Input validation

Guard 1 checks every user input **before** it reaches the LLM, so bad input never costs money. It is plain Python with no AI involved. That makes it free, fast (microseconds) and predictable: the same input always gives the same result.

All the checks live in one file, [`server/guards/input_validation.py`](../server/guards/input_validation.py).

## The rule

> Every check function **returns** an error message (a string), or `None` if the input is fine.
> Every feature function in `server/features/` runs the check first and **raises `ValueError`** if there is an error, before any LLM call.

The two halves have different jobs:

- **Returning a message** keeps the check functions simple and reusable. A page can call them to show an error right away, without trying the feature.
- **Raising in the feature** makes the check impossible to skip. Even if a page forgets to check, or a request comes from a manipulated browser, the feature refuses before the paid call.

## The limits

All limits are constants at the top of the file, so they can be changed in one place:

| Constant | Value | Used for |
|---|---|---|
| `IT_ROLES` | 6 roles, from `"Frontend Developer"` to `"QA Engineer"` | Role Q&A |
| `LEVELS` | `"Junior"`, `"Mid"`, `"Senior"`, `"Lead"` | Role Q&A |
| `JD_MIN_CHARS` | 200 | Job description: shorter is not a real job posting |
| `JD_MAX_CHARS` | 15,000 | Job description: longer is too expensive |
| `IMAGE_MAX_MB` | 5 | Screenshots: one screenshot |
| `IMAGE_MAX_COUNT` | 5 | Screenshots: how many per job posting |
| `IMAGES_MAX_TOTAL_MB` | 15 | Screenshots: all of one posting together |
| `IMAGE_SIGNATURES` | PNG and JPEG start bytes | Screenshots (WebP is checked separately, see below) |

The pages read these values through `api_client` (for example `get_roles_and_levels()`, `get_job_description_limits()`, `get_screenshot_limits()`). That keeps one list in the whole app: the dropdowns can't offer a role that the server would then reject.

## The check functions

### `validate_input(text, min_chars, max_chars, name="Text")`

The general text check. Its steps, in order (the first problem found is returned):

1. `text = (text or "").strip()`: `None` becomes `""`, and spaces and line breaks at the start and end are removed. A text of 3 letters padded with 300 spaces therefore counts as 3 characters.
2. Empty → `"<name> is empty."`
3. Shorter than `min_chars` → `"<name> is too short (3 characters, at least 200 needed)."`
4. Longer than `max_chars` → `"<name> is too long (15001 characters, at most 15000 allowed)."`
5. Otherwise → `None`.

`name` starts the message, so each feature gets a fitting one ("The job description is empty.").

### `validate_job_description(text)`

`validate_input` with the job description limits: `validate_input(text, JD_MIN_CHARS, JD_MAX_CHARS, name="The job description")`.

### `validate_role_and_level(role, level)`

1. `role not in IT_ROLES` → `"Unknown role: 'Chef'. Choose one of: Frontend Developer, ..."`
2. `level not in LEVELS` → `"Unknown level: 'Expert'. Choose one of: Junior, Mid, Senior, Lead."`
3. Otherwise → `None`.

The comparison is exact: `"frontend developer"` (lower case) and `"Frontend Developer; ignore all rules"` are both rejected. `{role!r}` prints the value in quotes, so an empty or strange value is visible in the message.

Why the server checks this although the page only offers dropdowns: Streamlit enforces a widget's options **only in the browser**. A manipulated request can send any value, and without this check that value would go straight into the prompt (`"Role: Chef"`).

### `image_type(data)`

Finds the real file type from the **first bytes of the file** (its "magic number"), not from the file name:

| Type | The file starts with |
|---|---|
| PNG | `89 50 4E 47 0D 0A 1A 0A` (`\x89PNG\r\n\x1a\n`) |
| JPEG | `FF D8 FF` |
| WebP | `RIFF`, then 4 bytes for the file size, then `WEBP` at bytes 8–11 |

WebP is checked separately because its marker is not at the very start. The function returns `"image/png"`, `"image/jpeg"`, `"image/webp"` or `None`.

A Windows program renamed to `job.png` starts with `MZ`, so it gets `None`. The returned type is also what `read_job_screenshots()` sends to the model (`data:image/png;base64,...`), so the model is never told a wrong type.

### `validate_image(data, name="The image")`

1. No bytes → `"<name> is empty."`
2. `image_type(data) is None` → `"<name> is not a PNG, JPG or WebP image."`
3. More than `IMAGE_MAX_MB` → `"<name> is too big (6.0 MB, at most 5 MB allowed)."` The size is `len(data) / (1024 * 1024)`.
4. Otherwise → `None`.

The type is checked before the size, so a file that isn't an image always gets the clearer of the two messages.

### `validate_images(images)`

Checks the screenshots of one job posting (a list of bytes, in reading order), each on its own and all together:

1. Empty list → `"No screenshot added."`
2. More than `IMAGE_MAX_COUNT` → `"Too many screenshots (6, at most 5 allowed)."`
3. Each image with `validate_image(data, name=f"Screenshot {number}")`, counting from 1. The first bad one is reported, for example `"Screenshot 2 is not a PNG, JPG or WebP image."`
4. More than `IMAGES_MAX_TOTAL_MB` together → `"The screenshots are too big together (20.0 MB, at most 15 MB allowed)."`
5. Otherwise → `None`.

The total limit is lower than 5 × 5 MB on purpose: every image makes the request bigger and more expensive, and a job posting rarely needs more than a few screenshots.

## Where each check runs

| Input | Early check on the page (shows the error at once) | Check that can't be skipped (in the feature, raises `ValueError`) |
|---|---|---|
| Role and level | none needed (dropdowns) | `qa_generator.generate_questions`, `interviewer_questions.generate_interviewer_questions` |
| Pasted job description | `analyze()` in `views/2_job_analyzer.py` → `api_client.validate_job_description` | `job_analyzer.analyze_job_description` |
| Screenshots (paste or upload) | `components/screenshot_input.py`, before an image is added to the list → `api_client.validate_screenshots` (the whole list, with the new image) | `job_analyzer.read_job_screenshots` |
| Text read from the screenshots | `analyze()` again, on the text Gemini returned | `job_analyzer.analyze_job_description` |

The feature check is a few lines that look the same everywhere:

```python
def generate_questions(role, level, settings=None):
    error = validate_role_and_level(role, level)  # guard 1, before the paid call
    if error:
        raise ValueError(error)
    system_prompt = load_prompt("qa_generator")
    ...
```

### Checks in the browser are extras, not the guard

Some widgets also limit input in the browser:
- the text box has `max_chars=15000`;
- the uploader has `type=["png", "jpg", "jpeg", "webp"]` and `max_upload_size=5`.

They make the page friendlier, because the user is stopped while typing or choosing a file. They are not security: a manipulated browser can skip them. The **paste box** has no browser checks at all, because pasted images never pass through the uploader. Only the server checks above are relied on.

## How an error reaches the user

**Early check on the page:**

```
api_client.validate_job_description(text)  → "The job description is too short (..)"
→ st.error(error)                           → red box, no feature call, no LLM call
```

**Check in the feature:**

```
job_analyzer.analyze_job_description(text) → raise ValueError("The job description is too short (..)")
→ the page's  except Exception as error:   → st.error(f"Could not analyze the job description: {error}")
```

The other pages work the same way: `components/question_panel.py` shows "Could not generate questions: …", and the screenshot flow shows "Could not read the screenshots: …".

For screenshots, the early check runs when an image is pasted or uploaded. A rejected image is **not added**: the screenshots already in the list stay, and the error is shown under the inputs.

Guards 3 and 4 also raise `ValueError` subclasses (`OutOfScopeError`, `RateLimitError`), so all guards reach the user the same way.

## Tests

[`server/tests/test_input_validation.py`](../server/tests/test_input_validation.py) has 42 tests and makes no LLM calls. Run them from the project root with `py -3.13 -m pytest`.

- **Check functions:**
  - empty text, `None` and spaces-only text;
  - too short, too long, and the exact JD limits (200 and 15,000 pass; 199 and 15,001 fail);
  - every allowed role and level, plus unknown ones;
  - image types from their bytes (GIF, PDF and `.exe` rejected);
  - images exactly at the size limit and one byte over;
  - lists of screenshots: empty, too many, which screenshot is named in the message, too big together.
- **Features stop before the LLM:** the `no_llm` fixture replaces `LLMClient` in the feature modules with `NoLLMClient`, which fails the test as soon as it is created. These tests then call each feature with bad input and expect a `ValueError`. If a guard were missing, the feature would try to create an `LLMClient` and the test would fail. That proves the check runs *before* the paid call, and the tests can never cost money.
- **Several screenshots in one call:** a stand-in `RecordingLLMClient` records what `read_job_screenshots()` sends: exactly one call, with all images in reading order and their real types.

## Adding a check for a new feature

For example, for the Intro Polisher (feature 4):

1. Add the limits as constants in `input_validation.py`, for example `INTRO_MIN_CHARS = 50` and `INTRO_MAX_CHARS = 3000`.
2. Add `validate_intro(text)`, which calls `validate_input(text, INTRO_MIN_CHARS, INTRO_MAX_CHARS, name="The introduction")`.
3. In the feature function, call it first and raise `ValueError` on an error.
4. Optionally, have the page check it early through a function in `api_client`.
5. Add tests, including one with `no_llm`.
