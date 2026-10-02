# Learning Streamlit with the Interview Practice App

This guide teaches Streamlit by following the path this project took: from a
"Hello World" page to a multipage app with reusable components, shared state, a
theme, custom CSS and a small custom component written in JavaScript.

Each stage adds **one new idea**. Every example is a complete Python file: save
it (e.g. as `stage2.py`) and start it with

```bash
py -3.13 -m streamlit run stage2.py
```

The examples use a **fake AI function** in place of the real LLM call, so they
cost nothing and work without an API key. The real app calls the model through
`client/api_client.py`, but the Streamlit side looks the same.

Written for Streamlit 1.64 (the version installed for this project).

| Stage | New idea | Where in the app |
|---|---|---|
| 1 | A script becomes a web page | `test-app.py` |
| 2 | Input, button, output | first version of Role Q&A |
| 3 | Layout: columns, containers, sidebar, expander | `views/1_qa_generator.py` |
| 4 | The rerun model and `st.session_state` | `components/question_panel.py` |
| 5 | Callbacks, `st.rerun()` and widget keys | `views/2_job_analyzer.py` |
| 6 | Talking to the back end: spinner, errors | `client/api_client.py` |
| 7 | Multipage apps with `st.navigation` | `client/app.py` |
| 8 | Components: reusable functions | `client/components/` |
| 9 | State shared across pages | `components/settings_sidebar.py` |
| 10 | More widgets: uploads, ratings, tables | screenshot input, Prompt Lab |
| 11 | Look and feel: theme, CSS, HTML | `.streamlit/config.toml`, `styles.py` |
| 12 | A custom component (HTML + JS) | `components/paste_box.py` |
| 13 | Testing a Streamlit page | `streamlit.testing` |

---

## Stage 1: A script becomes a web page

Streamlit turns a normal Python script into a web page. Each `st.` call adds
one element to the page, in order from top to bottom.

```python
# stage1.py: the "Hello World" from test-app.py
import streamlit as st

st.title("Hello World!")
st.markdown("This text is :red[Red], this is :blue[Blue], and this is :rainbow[Rainbow]!")
st.write("st.write shows almost anything:", 42, {"role": "Backend Developer"})
```

Things to know:

- `streamlit run stage1.py` starts a small web server on <http://localhost:8501>
  and opens the browser.
- Save the file and the browser offers **Rerun** (or reruns by itself if you
  choose "Always rerun"). There's no build step.
- `st.markdown` understands Markdown plus Streamlit extras such as `:red[...]`
  and `:material/icon_name:` icons.

---

## Stage 2: Input, button, output

The first real version of the app: the user types a role, clicks a button and
sees questions.

```python
# stage2.py: the smallest useful GUI
import streamlit as st


def fake_generate_questions(role):
    """Pretend to be the AI: return 3 interview questions for a role."""
    return [
        f"What does a typical day look like for a {role}?",
        f"Which tools does a {role} use most, and why?",
        f"Tell me about a hard problem you solved as a {role}.",
    ]


st.title("Interview Question Generator")

role = st.text_input("Job role", placeholder="e.g. Backend Developer")

if st.button("Generate questions", type="primary"):
    if not role.strip():
        st.error("Please enter a role first.")
    else:
        for number, question in enumerate(fake_generate_questions(role), start=1):
            st.markdown(f"**Q{number}.** {question}")
```

How it works:

- `st.text_input` draws an input field **and returns its current value** (a
  `str`). There's no `onChange` handler and no `getValue()`: the variable
  `role` simply holds what is in the box.
- `st.button` returns `True` **only in the run right after the click**, and
  `False` in every other run.
- Output is just more `st.` calls. To show text in a box, use
  `st.text_area("Answer", value=text, disabled=True)` or `st.code(text)`.

Try it: click the button, then change the role text. The questions disappear.
Stage 4 explains why.

---

## Stage 3: Layout

The page with everything stacked from top to bottom gets long fast. Streamlit
has layout elements that you use with `with`.

```python
# stage3.py: columns, bordered containers, an expander and the sidebar
import streamlit as st

ROLES = ["Frontend Developer", "Backend Developer", "Data Engineer"]
LEVELS = ["Junior", "Mid", "Senior", "Lead"]

st.set_page_config(page_title="Interview Practice", layout="wide")  # first st call
st.title("Role-Based Q&A")

with st.sidebar:
    st.markdown("### Settings")
    count = st.slider("Number of questions", 1, 5, 3)

# Two dropdowns side by side
col_role, col_level = st.columns(2)
role = col_role.selectbox("Role", ROLES)
level = col_level.selectbox("Level", LEVELS)

# Two panels side by side, each a card with a border
col_left, col_right = st.columns(2, gap="large")

with col_left:
    with st.container(border=True):
        st.markdown("#### Interview questions")
        for number in range(1, count + 1):
            st.markdown(f"**Q{number}.** A {level} {role} question...")
            with st.expander("Show model answer"):
                st.write("The answer is hidden, so you can try first.")

with col_right:
    with st.container(border=True):
        st.markdown("#### Questions to ask the interviewer")
        st.info("Pick a role and level, then click **Generate**.")
```

Notes:

- `st.columns(2)` returns two column objects. You can either call methods on
  them (`col_role.selectbox(...)`) or use `with col_left:`. Both do the same.
- `st.columns([3, 1])` makes columns with relative widths.
- `st.set_page_config` must be the **first** Streamlit call of a run.
  `layout="wide"` uses the full browser width.
- `st.sidebar` is the panel on the left. In this app it only holds the LLM
  settings.
- `st.container(horizontal=True)` places its children in a row (used for the
  two buttons on the Home page).

---

## Stage 4: The rerun model and `st.session_state`

This is **the most important idea in Streamlit**.

> Every time the user changes a widget or clicks a button, Streamlit runs your
> **whole script again**, from the first line to the last.

That's why the questions in stage 2 disappeared: in the next run, the button
returns `False` again, so the `if` block isn't run and nothing is drawn.

All normal variables are created fresh in every run. To remember something
between runs, put it into `st.session_state`, a dict that belongs to the
browser tab and survives reruns.

```python
# stage4.py: keep the results after the click
import streamlit as st


def fake_generate_questions(role):
    """Pretend to be the AI: return 3 interview questions for a role."""
    return [f"Question {n} for a {role}" for n in range(1, 4)]


st.title("Interview Question Generator")

role = st.text_input("Job role", value="Backend Developer")

# 1. The button only CHANGES the state...
if st.button("Generate questions", type="primary"):
    st.session_state["questions"] = fake_generate_questions(role)
    st.session_state["questions_for"] = role

# 2. ...and the page always DRAWS what is in the state.
questions = st.session_state.get("questions", [])
if not questions:
    st.info("Enter a role and click **Generate questions**.")
else:
    st.caption(f"Generated for: {st.session_state['questions_for']}")
    for number, question in enumerate(questions, start=1):
        st.markdown(f"**Q{number}.** {question}")

# A small extra: the role changed after the questions were made
if questions and role != st.session_state["questions_for"]:
    st.warning("The role has changed. Click **Generate questions** again to update.")
```

The pattern "**events change the state, the page draws the state**" is used
on every page of the app. For example, `components/question_panel.py` stores
the AI's reply in `st.session_state[f"{key}_items"]` and draws it on every run.

Useful dict methods (all used in the app):

| Code | Meaning |
|---|---|
| `st.session_state["x"] = 1` | store |
| `st.session_state.get("x", default)` | read, with a default if missing |
| `st.session_state.setdefault("x", [])` | set only if missing (good for start values) |
| `st.session_state.pop("x", None)` | read once and remove (a short-lived note) |
| `"x" in st.session_state` | check |

---

## Stage 5: Widget keys, callbacks and `st.rerun()`

### Widget keys

Each widget gets an ID. If two widgets have the same label and settings, they
need different `key`s, or Streamlit raises a `DuplicateElementId` error. With a
`key`, the widget's value is **also stored in `st.session_state[key]`**:

```python
st.text_area("Job description", key="jd_input")
st.write(st.session_state["jd_input"])  # the same text
```

### Callbacks (`on_click`, `on_change`)

A callback is a function Streamlit calls **before** the rerun, as soon as the
user clicks or changes a widget. Use it when the click should change the state
and the page should already show the new state in the same run.

```python
# stage5a.py: a list with "add" and "remove" buttons using callbacks
import streamlit as st

st.session_state.setdefault("skills", ["Python", "SQL"])


def add_skill():
    """Add the typed skill to the list and empty the input box."""
    skill = st.session_state["new_skill"].strip()
    if skill and skill not in st.session_state["skills"]:
        st.session_state["skills"].append(skill)
    st.session_state["new_skill"] = ""  # allowed here: the callback runs before the box is drawn


def remove_skill(skill):
    """Remove one skill from the list (if it's still there)."""
    if skill in st.session_state["skills"]:
        st.session_state["skills"].remove(skill)


st.text_input("New skill", key="new_skill", on_change=add_skill)  # Enter adds it
st.button("Add", on_click=add_skill)

for skill in st.session_state["skills"]:
    col_name, col_remove = st.columns([4, 1], vertical_alignment="center")
    col_name.write(skill)
    col_remove.button("Remove", key=f"remove_{skill}", on_click=remove_skill, args=(skill,))
```

The key and the argument are the skill's **name**, not its position. With
positions, removing item 0 shifts all the others, and a fast second click can
hit the wrong item or one that's gone.

The screenshot list on the JD Analyzer works like this
(`components/screenshot_input.py`: `remove(index)` and `remove_all()` are
`on_click` callbacks).

### The rule behind `st.rerun()`

> You can't change a widget's value in `st.session_state` **after** the widget
> was drawn in the same run. Streamlit raises a `StreamlitAPIException`.

There are two ways around it:

1. Change it in a **callback** (as above), or
2. Leave a note in the state, call `st.rerun()` (start the script again at
   once), and make the change **at the top of the page**, before the widget is
   drawn.

The JD Analyzer uses way 2: after reading the screenshots, it must switch the
input view back to "Text".

```python
# stage5b.py: switch a widget from code, using a note and st.rerun()
import streamlit as st

# Step 2 (next run): apply the note before the widget is drawn.
if st.session_state.pop("show_text", False):
    st.session_state["input_mode"] = "📝 Text"

mode = st.segmented_control(
    "Input", ["📝 Text", "🖼️ Screenshot"], default="📝 Text", required=True, key="input_mode"
)

if mode == "🖼️ Screenshot":
    if st.button("Process screenshot", type="primary"):
        st.session_state["job_text"] = "Text read from the screenshot..."  # its box isn't drawn now
        st.session_state["show_text"] = True  # Step 1: leave a note...
        st.rerun()                            # ...and start again at once
else:
    st.text_area("Job description", key="job_text")
```

`st.stop()` is the opposite: it ends the current run here, and nothing below it
is drawn (handy after an error message).

---

## Stage 6: Talking to the back end

In this project the front end never imports from `server/` itself. One file,
`client/api_client.py`, has one function per feature, and pages call those.
If the server ever becomes a real API (FastAPI), only that file changes.

The page side shows a spinner while waiting and turns errors into messages:

```python
# stage6.py: a slow call with a spinner, input checks and error messages
import time

import streamlit as st

LEVELS = ["Junior", "Mid", "Senior", "Lead"]


def generate_questions(role, level):
    """Fake back end call: check the input like guard 1, then 'ask the AI'.

    Raises:
        ValueError: the input is not allowed (shown to the user as an error).
    """
    if level not in LEVELS:
        raise ValueError(f"Unknown level: {level}")
    if len(role) > 50:
        raise ValueError("The role name is too long.")
    time.sleep(2)  # the AI is thinking
    return [f"{level} {role} question {n}" for n in range(1, 6)]


role = st.text_input("Role", "Data Engineer")
level = st.selectbox("Level", LEVELS)

if st.button("Generate", type="primary"):
    with st.spinner("Asking the AI..."):
        try:
            st.session_state["questions"] = generate_questions(role, level)
        except ValueError as error:      # bad input, out of scope, rate limit
            st.error(str(error))
        except Exception as error:       # network, API key, ...
            st.error(f"Could not generate questions: {error}")

for question in st.session_state.get("questions", []):
    st.markdown(f"- {question}")
```

Message elements: `st.error`, `st.warning`, `st.info`, `st.success`, and
`st.toast` (a small pop-up that disappears by itself). All take an optional
`icon=":material/...:"`.

In the app, every feature function in `server/features/` checks its own input
and raises `ValueError` **before** the paid LLM call (guard 1). Pages may also
run the same check first through `api_client`, to show the error at once.

> **Restart after changing imported modules.** Streamlit reruns the page script
> on every click, but modules it **imports** (`api_client.py`, `components/`,
> `server/`) are loaded only once. After you change them, stop the app
> (Ctrl+C) and start it again.

---

## Stage 7: Multipage apps

### Option A: the `pages/` folder (automatic)

The project started with `client/pages/`. Streamlit finds every file in a
folder called `pages/` next to the main script and lists it in the sidebar.
That's quick, but you can't control the menu much, and every page has to repeat
the page config, the styles and the sidebar.

### Option B: `st.navigation` (what the app uses now)

`client/app.py` is a **frame** that runs on every click. It does the shared
work once, then runs the chosen page:

```python
# app.py: the frame for all pages
import streamlit as st

pages = [
    st.Page("views/0_home.py", title="Home", icon="🏠", default=True),
    st.Page("views/1_qa_generator.py", title="Role Q&A", icon="💬"),
    st.Page("views/2_job_analyzer.py", title="JD Analyzer", icon="📄"),
]

DEVELOPER_MODE = False  # the real app reads this from config.ini
if DEVELOPER_MODE:
    # Not registered at all when off: not even its URL works.
    pages.append(st.Page("views/9_prompt_lab.py", title="Prompt Lab", icon="🧪"))

st.set_page_config(page_title="IntervAI", layout="wide")  # once, for all pages

with st.sidebar:                                           # once, for all pages
    st.session_state["model"] = st.selectbox("Model", ["gpt-5-mini", "gemini-2.5-flash"])

page = st.navigation(pages, position="top")  # draws the menu, returns the chosen page
page.run()                                   # runs that page's file
```

```python
# views/0_home.py: a page is a normal script, without set_page_config
import streamlit as st

st.title("Welcome")
st.write(f"Model chosen in the sidebar: {st.session_state['model']}")

if st.button("Practice Role Q&A", type="primary"):
    st.switch_page("views/1_qa_generator.py")   # go to another page from code

st.page_link("views/2_job_analyzer.py", label="Open the JD Analyzer", icon="📄")  # a link
```

Create `views/1_qa_generator.py` and `views/2_job_analyzer.py` with a
`st.title(...)` each, then run `streamlit run app.py`.

Rules learned in this project:

- **Don't call the folder `pages/`** when you use `st.navigation`, or the
  automatic discovery switches on as well and clashes with it. This app uses
  `views/`.
- `position="top"` puts the menu in the top bar; the default is the sidebar.
- Paths in `st.Page`, `st.switch_page` and `st.page_link` are relative to the
  main script (`app.py`).
- A page can also be a function: `st.Page(show_about, title="About")`.
- Group pages under headings with a dict:
  `st.navigation({"Practice": [...], "Tools": [...]})`.
- Pages in `views/` are re-read on every run (no restart needed). `app.py`'s
  imports are not.

---

## Stage 8: Components (reusable functions)

When the same UI part shows up twice, make it a **function that draws
widgets**. Streamlit has no special "component class": a component is simply a
Python function that calls `st.` functions, and it may return what the user
chose. The app keeps them in `client/components/`, one per file.

### A component that returns values

```python
# components/role_picker.py
import streamlit as st


def role_picker(roles, levels):
    """Draw two dropdowns side by side and return (role, level)."""
    col_role, col_level = st.columns(2)
    role = col_role.selectbox("Role", roles)
    level = col_level.selectbox("Level", levels)
    return role, level
```

### A component that only draws

```python
# components/qa_card.py
import streamlit as st


def qa_card(number, question, answer=None):
    """Draw one question as a card, with the model answer hidden in an expander."""
    with st.container(border=True):
        st.markdown(f"**Q{number}. {question}**")
        if answer is None:
            return
        with st.expander("Show model answer (STAR)"):
            st.markdown(f"**Situation & Task:** {answer['situation']}")
            st.markdown(f"**Action:** {answer['action']}")
            st.markdown(f"**Result:** {answer['result']}")
```

### A configurable component with its own state

The Role Q&A page has two panels that look and work the same: a title, a
button and a list. Only the AI call and the item look differ. So the panel gets
those as **functions** (`generate`, `render_item`), and a `key` that keeps the
state of the two panels apart.

```python
# stage8.py: one component, used twice on a page
import streamlit as st


def question_panel(key, title, button_label, generate, render_item):
    """Draw a card with a title, a button and the results, kept in st.session_state.

    Args:
        key: a unique name; it keeps the state of several panels apart.
        generate: a function without arguments that returns a list of items.
        render_item: a function render_item(number, item) that draws one item.
    """
    with st.container(border=True):
        st.markdown(f"#### {title}")
        if st.button(button_label, type="primary", key=f"{key}_button"):
            with st.spinner("Asking the AI..."):
                st.session_state[f"{key}_items"] = generate()

        items = st.session_state.get(f"{key}_items", [])
        if not items:
            st.info(f"Click **{button_label}**.")
        for number, item in enumerate(items, start=1):
            render_item(number, item)


def qa_card(number, question):
    """Draw one interview question."""
    st.markdown(f"**Q{number}.** {question}")


def reverse_card(number, item):
    """Draw one question to ask the interviewer, with its category."""
    st.caption(item["category"].upper())
    st.markdown(item["question"])


role = st.selectbox("Role", ["Backend Developer", "Data Engineer"])
left, right = st.columns(2, gap="large")

with left:
    question_panel(
        key="role_questions",
        title="Interview questions",
        button_label="Generate interview questions",
        generate=lambda: [f"A question for a {role} #{n}" for n in range(1, 4)],
        render_item=qa_card,
    )
with right:
    question_panel(
        key="reverse_questions",
        title="Questions to ask the interviewer",
        button_label="Generate reverse questions",
        generate=lambda: [{"category": "Team", "question": f"How big is the {role} team?"}],
        render_item=reverse_card,
    )
```

Tips for components:

- **Prefix every key** inside a component with the `key` parameter
  (`f"{key}_button"`), so the component can be used more than once per page.
- Pass in data (`roles`, `levels`) instead of importing the back end in the
  component. Then only the page and `api_client` know about the server.
- Return plain values (`str`, `dict`, `list`), so the page decides what to do.

---

## Stage 9: State shared across pages

`st.session_state` belongs to the browser tab, not to a page, so all pages see
the same dict. The app uses this in two ways.

**1. A widget in the frame, read by every page.** The LLM settings are drawn
once in `app.py` and stored for the pages:

```python
# in app.py
st.session_state["llm_settings"] = settings_sidebar(models, defaults)

# in any page
settings = st.session_state.get("llm_settings")
```

The sidebar widgets have fixed keys (`key="setting_model"` etc.), so they keep
their values when the user switches pages.

**2. A widget that keeps its value while it's hidden.** Normally Streamlit
deletes a widget's value when the widget isn't drawn in a run (another page, or
a hidden view). `persist_state="session"` keeps it:

```python
st.text_area(
    "Job description",
    key="jd_input",
    persist_state="session",  # keep the text in the Screenshot view and on other pages
)
```

(Older Streamlit versions needed a trick for this: copy the value into a
second, non-widget key, and copy it back before drawing the widget.)

**Document your state.** Pages with many keys list them in the comment at the
top of the file. See `views/2_job_analyzer.py`:

```python
# What the page remembers between reruns (st.session_state):
#   "jd_input"      what is typed in the text box
#   "jd_screenshots" the screenshots in reading order: a list of {"name", "data"}
#   "jd_analysis"   the AI's result for that JD
```

---

## Stage 10: More widgets

### Toggle between two inputs: `st.segmented_control`

```python
mode = st.segmented_control(
    "Input", ["📝 Text", "🖼️ Screenshot"],
    default="📝 Text",
    required=True,              # one option is always selected
    label_visibility="collapsed",
)
```

`st.pills` looks similar and also allows several choices
(`selection_mode="multi"`).

### File upload, and how to empty the uploader

```python
# stage10a.py: collect uploaded images in a list in session_state
import streamlit as st

st.session_state.setdefault("shots", [])
st.session_state.setdefault("uploader_id", 0)
uploader_key = f"uploader_{st.session_state['uploader_id']}"


def on_upload():
    """Move the new files into our own list, then give the uploader a new key."""
    for file in st.session_state[uploader_key] or []:
        st.session_state["shots"].append({"name": file.name, "data": file.getvalue()})
    st.session_state["uploader_id"] += 1  # new key = a new, empty uploader


st.file_uploader(
    "Upload screenshots",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key=uploader_key,
    on_change=on_upload,
)

columns = st.columns(5)
for column, shot in zip(columns, st.session_state["shots"]):
    column.image(shot["data"], caption=shot["name"])
```

The trick: an uploader keeps its files until its key changes. Changing the key
after each upload gives an empty uploader, and **our own list** is the only
place the files live (see `components/screenshot_input.py`).

### Star ratings: `st.feedback`

```python
stars = st.feedback("stars", key="score_clarity")  # None, or 0..4 for 1..5 stars
if stars is not None:
    st.write(f"You gave {stars + 1} stars")
```

The Prompt Lab uses one per rubric criterion.

### Tables and numbers: `st.dataframe`, `st.metric`

```python
import pandas as pd
import streamlit as st

table = pd.DataFrame(
    {"technique": ["zero_shot", "few_shot"], "you": [14.0, 17.5], "topics": [60, 85]}
).set_index("technique")

st.metric("Best technique", "few_shot", delta="+3.5 stars")
st.dataframe(table, column_config={
    "you": st.column_config.NumberColumn("you (of 20)", format="%.1f"),
    "topics": st.column_config.ProgressColumn("topics %", min_value=0, max_value=100),
})
```

`column_config` sets the header text and the look of each column.

### Long work in parallel

The Prompt Lab runs 5 techniques at the same time with a `ThreadPoolExecutor`.
**Worker threads must not call `st.` functions**: they only compute and return
data, and the main script draws it afterwards.

```python
from concurrent.futures import ThreadPoolExecutor

with st.spinner("Running 5 techniques..."):
    with ThreadPoolExecutor(max_workers=5) as pool:
        results = dict(zip(techniques, pool.map(run_technique, techniques)))  # no st. inside
for technique, result in results.items():
    st.write(technique, result)
```

---

## Stage 11: Look and feel

### The theme: `.streamlit/config.toml`

Colors and fonts for all widgets. Streamlit reads this file **only from the
folder you start it in**, so always start the app from the project root.

```toml
[theme]
base = "light"
primaryColor = "#16a34a"              # buttons, active widgets
backgroundColor = "#f8fafc"           # page
secondaryBackgroundColor = "#ffffff"  # input fields
textColor = "#0f172a"
borderColor = "#cbd5e1"
showWidgetBorder = true

[theme.sidebar]                       # a dark sidebar with its own colors
backgroundColor = "#0b1a11"
textColor = "#f8fafc"
```

Restart the app after changing it.

### Your own CSS

For things the theme can't do (fonts, rounded cards, pill buttons), the app
injects one `<style>` block, once, from `app.py` (`components/styles.py`):

```python
import streamlit as st

CSS = """
<style>
.stButton button { border-radius: 9999px; font-weight: 600; }   /* pill buttons */
.pill { padding: 2px 10px; border-radius: 9999px; background: #f0fdf4; color: #15803d; }
</style>
"""


def apply_styles():
    """Load the app's CSS into the page."""
    st.markdown(CSS, unsafe_allow_html=True)
```

### HTML in `st.markdown`

```python
def section_header(title, subtitle, pill=None):
    """Draw a centered header with an optional pill."""
    pill_html = f'<span class="pill">{pill}</span>' if pill else ""
    # One line on purpose: see the warning below.
    st.markdown(
        f'<div class="section-header">{pill_html}<h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
```

Two warnings, both learned the hard way in this project:

1. **No empty lines inside the HTML.** Markdown ends the HTML block at an empty
   line (for example from an empty `{pill_html}` on its own line), and the
   indented lines after it are shown as a **code block with raw tags**. Build
   optional or repeated parts on one line. After changing such HTML, check the
   page in a real browser.
2. **Escape user content.** Never put text the user typed (or the AI wrote)
   into HTML unescaped. Use `html.escape(text)` first, like
   `components/hud_bar.py` does. Plain `st.markdown(text)` without
   `unsafe_allow_html` is safe.

---

## Stage 12: A custom component (HTML + JavaScript)

Streamlit has no widget for "paste an image from the clipboard". With
`st.components.v2.component` you can write a small one: some HTML, some CSS,
and a JavaScript function that sends data back to Python.

```python
# stage12.py: a tiny version of components/paste_box.py
import base64

import streamlit as st

HTML = '<div id="box" contenteditable="true">Click here, then press Ctrl+V</div>'
CSS = "#box { border: 2px dashed var(--st-border-color); padding: 24px; text-align: center; }"
JS = """
export default function (component) {
    const { parentElement, setTriggerValue } = component
    const box = parentElement.querySelector("#box")
    const onPaste = (event) => {
        event.preventDefault()
        const item = Array.from(event.clipboardData?.items ?? []).find((i) => i.type.startsWith("image/"))
        if (!item) return
        const reader = new FileReader()
        reader.onload = () => setTriggerValue("pasted", { data_url: reader.result })  // -> Python
        reader.readAsDataURL(item.getAsFile())
    }
    box.addEventListener("paste", onPaste)
    return () => box.removeEventListener("paste", onPaste)  // cleanup
}
"""

# Register once, at import time.
_paste_box = st.components.v2.component("mini_paste_box", html=HTML, css=CSS, js=JS)

result = _paste_box(key="paste", on_pasted_change=lambda: None)
if result.pasted:  # only set in the run right after a paste
    data = base64.b64decode(result.pasted["data_url"].split(",", 1)[1])
    st.session_state["image"] = data  # store it, or it's gone in the next run
if "image" in st.session_state:
    st.image(st.session_state["image"])
```

Key points:

- `setTriggerValue("pasted", ...)` sends a **one-time event** to Python and
  starts a rerun. The value is there only in that one run, so store it in
  `st.session_state`.
- `on_pasted_change=...` tells Streamlit that the component has a `pasted`
  value to listen for.
- `var(--st-border-color)` and similar CSS variables pick up the app's theme.
- Return a cleanup function from the JS, which removes the event listeners.

---

## Stage 13: Testing a Streamlit page

Code that has no `st.` calls (validation, config reading) is tested with plain
pytest, like `client/tests/test_app_config.py`. For the page itself, Streamlit
has `AppTest`, which runs a script without a browser and lets you click
buttons from code:

```python
# test_stage4.py: run with py -3.13 -m pytest test_stage4.py
from streamlit.testing.v1 import AppTest


def test_questions_stay_after_click():
    """The questions are still shown in the run after the click."""
    at = AppTest.from_file("stage4.py").run()
    at.text_input[0].input("Data Engineer").run()
    at.button[0].click().run()
    assert "Data Engineer" in at.caption[0].value
    at.run()  # one more rerun without a click
    assert len(at.markdown) == 3
```

Limits: `AppTest` doesn't render Markdown or HTML, so it can't find the "raw
tags shown as code" problem from stage 11. Check those in a real browser. And
be careful with tests that click "Generate" on the real app: they make real,
paid LLM calls.

---

## Cheat sheet: common pitfalls

| Problem | Cause | Fix |
|---|---|---|
| Results disappear after the next click | The whole script reruns; the button is `False` again | Store results in `st.session_state` (stage 4) |
| `DuplicateElementId` | Two widgets with the same label and settings | Give each a unique `key` |
| `StreamlitAPIException` when setting `st.session_state[key]` | The widget was already drawn in this run | Use a callback, or a note + `st.rerun()` (stage 5) |
| A typed text is lost when switching views or pages | Streamlit deletes the values of widgets that aren't drawn | `persist_state="session"` (stage 9) |
| A change in `components/` or `api_client.py` has no effect | Imported modules are loaded once | Restart the app |
| The theme isn't applied | The app was started from another folder | Start from the project root |
| HTML shows up as a code block with raw tags | An empty line inside the HTML | Build the HTML on one line (stage 11) |
| `set_page_config` error | It wasn't the first `st.` call | Call it once, at the top of `app.py` |
| Pages show up twice / strange menu | A `pages/` folder together with `st.navigation` | Rename the folder (e.g. `views/`) |
| Nothing is drawn from a thread | Worker threads can't draw | Return data, draw in the main script |

## Where to read more

- Streamlit docs: <https://docs.streamlit.io>
- This project: `client/app.py` (the frame), `client/views/2_job_analyzer.py`
  (the most state handling), `client/components/screenshot_input.py`
  (callbacks and key tricks), `client/components/paste_box.py` (custom
  component).
- `docs/jd-analyzer-screenshot.md` explains the screenshot flow in detail.
