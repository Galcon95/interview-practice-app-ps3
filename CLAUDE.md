# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

An interview-practice web app built with Streamlit (Python), for a Turing College project. It's at an early stage: `test-app.py` is a Streamlit "Hello World" used to check the setup, and the rest is placeholder files.

MVP features: (1) role-based Q&A generator, IT jobs only; (2) "questions to ask the interviewer", together with 1; (3) job description analyzer (role + skills, then 1 and 2); (4) self-introduction polisher; (5) resume upload and skill match against a job (coverage %); (6) security guards: input validation, prompt-injection filter, scope enforcement in the system prompt, optional rate limiting.

- `client/`: front end (Streamlit). `app.py` is the entry point: it sets page config and styles once, then lists every page with `st.navigation(position="top")` (menu order and labels are set there; the menu is in the top bar, the sidebar only holds the LLM settings). `views/` holds one page per feature (not named `pages/`, which would switch on Streamlit's automatic page discovery and clash with `st.navigation`), `api_client.py` has one call per feature, `components/` holds reusable widgets that pages combine.
- `server/`: back end. `main.py` is the API (one endpoint per feature), `features/` has one module per feature, `guards/` has guards 1, 2 and 4, `prompts/` has one system prompt per feature plus `guardrail.md` (guard 3); a feature with several prompt techniques has a folder instead (for now only `prompts/qa_generator/`), one file per technique: `zero_shot`, `role_and_rules` (the default the app uses), `few_shot`, `chain_of_thought`, `self_critique`. They are listed in `TECHNIQUES` in the feature module; shared helpers are in `server/prompt_techniques.py`; only the Prompt Lab passes a non-default `technique`, `prompt_loader.py` reads them, `llm.py` calls the model, `document_reader.py` turns resumes into text. Secrets go in `server/.env` (see `.env.example`).
- LLM: OpenRouter via the `openai` package (`server/llm.py`, class `LLMClient`, default model `openai/gpt-5-mini`, JSON replies). The key is `OPENROUTER_API_KEY`, from `server/.env` or a Windows environment variable (already set on this machine, so tests that click "Generate" make real, paid calls).
- LLM settings: `server/llm.py` defines `MODELS` (label + whether the model supports temperature) and the defaults. `components/settings_sidebar.py` is drawn once in `app.py` and stored in `st.session_state["llm_settings"]`; pages pass it through `api_client` to the feature, which does `LLMClient(**settings)`. GPT-5 models ignore temperature (not sent) and count hidden reasoning in `max_tokens`, so keep it high (default 4000). A cut-off reply (`finish_reason == "length"`) raises a clear error.
- Debug log: `LLMClient` logs every request payload and raw reply through `LLMLogger` (`server/llm_logger.py`) to the terminal and `server/logs/llm.log` (git-ignored, rotates at 1 MB). `LLM_LOG_LEVEL` = DEBUG (default, full JSON), INFO (one line per call) or WARNING (errors only).
- Developer mode: `config.ini` in the project root, `[app] developer_mode = on/off` (default off; read by `client/app_config.py` on every run, so no restart is needed). When on, `app.py` adds the 🧪 Prompt Lab page (`views/9_prompt_lab.py`), which runs the 5 prompt techniques of the Role Q&A question generator on one fixed test case (role, level, model) and shows the results side by side. Its test cases are in `prompt_lab/test_cases.ini` (one INI section per case: `role`, `level`, optional `note` and `expected_topics`), read on every page load by `server/prompt_lab.py`, which checks each case with `validate_role_and_level` and reports bad ones instead of failing. Each result gets automatic measurements (`measure_questions`: words, packed questions, behavioral phrases, expected topics covered, all keyword heuristics) and 1–5 stars from the developer for the 4 rubric criteria in `RUBRIC` (role fit, level fit, variety, clarity, each with anchors for 1/3/5). Optionally an AI judge (LLM-as-judge, `judge_questions`, prompt `prompts/prompt_lab_judge.md`, default model `JUDGE_DEFAULT_MODEL` = Gemini 2.5 Flash, temperature 0) scores with the same rubric; it is blind to the technique, and the rubric text is filled in from `RUBRIC` so there is only one copy. A technique is saved to `prompt_lab/scores.csv` (opens in Excel) if the developer scored it fully or the judge scored it; the other side's columns stay empty. The page compares the techniques (your and the judge's averages) and you vs. the judge (difference per criterion, agreement within 1 star, same best technique). Run + judge of 5 techniques is exactly the 10 calls per minute that guard 4 allows. Never write fake or test scores into the real `scores.csv`; tests use temporary files. When off, that page isn't registered at all. Customer pages never depend on developer mode. Keep `config.ini` committed with `off`.
- No FastAPI for now: `client/api_client.py` adds the project root to `sys.path` and imports `server/` directly. It's the only client file allowed to touch `server/`.

## Commands

```bash
pip install -r client/requirements.txt -r server/requirements.txt   # use "streamlit[auth]" if using st.login (see docs/streamlit-auth.md)
streamlit run client/app.py              # run from the project root; serves on http://localhost:8501
```

Always start from the project root: `.streamlit/config.toml` (the theme) is only read from the folder Streamlit is started in. Streamlit is installed in Python 3.13; the bare `python` in the shell points to an unrelated venv, so use `py -3.13` if needed.

`client/requirements.txt` and `server/requirements.txt` list dependencies. Run the tests from the project root with `py -3.13 -m pytest` (`pytest.ini` sets the test folder and puts the root on the import path). Tests for guards 1, 3 and 4 are in `server/tests/`, tests for client code (e.g. `app_config.py`) in `client/tests/`; none makes LLM calls; `test_injection_filter.py` (guard 2) and `test_resume_matcher.py` are still empty placeholders. There's no linter config yet.

Guard 1 rule (details: `docs/guard-1-input-validation.md`): every feature function in `server/features/` checks its own input (functions in `guards/input_validation.py`) and raises `ValueError` before any LLM call, so no page can skip it. Pages may call the same check through `api_client` first, to show the error without a round trip. Allowed roles and levels live in `input_validation.py` (`IT_ROLES`, `LEVELS`); the Role Q&A dropdowns get them from `api_client.get_roles_and_levels()`.

Guard 3 rule: `prompt_loader.load_prompt(name)` returns the feature prompt plus `prompts/guardrail.md` at the end (HTML comments removed), so every feature gets the scope rules automatically. Always load prompts through `load_prompt()`. When the model replies `{"out_of_scope": true, "reason": ...}`, `LLMClient.complete_json()` raises `OutOfScopeError` (a `ValueError`), which the pages show like other bad input. `server/tests/test_guardrail.py` covers this without LLM calls.

Guard 4 rule: one user for now (no logins), so `guards/rate_limit.py` keeps one shared sliding-window counter: at most `MAX_REQUESTS` (10) LLM calls per `WINDOW_SECONDS` (60). `LLMClient.complete_json()` calls `check_rate_limit()` before every request and raises `RateLimitError` (a `ValueError`); refused calls don't count. "Process screenshot" makes 2 calls. `server/tests/conftest.py` resets the counter before every test.

Code style: every function and class has a docstring that says what it does, with `Args:`, `Returns:` and `Raises:` sections where they apply (Google style, plain English). Tests get a one-line docstring saying what they check. Comments inside function bodies explain the "why" of single steps. `server/` and `client/` both follow this.

## Skills and agents

- `.claude/skills/interview-feedback/`: review an interview answer (scores, strengths, improvements, model answer).
- `.claude/skills/write-system-prompt/`: add a new prompt technique to `prompts/`.
- `.claude/skills/compare-prompts/`: compare the prompt techniques and fill in `docs/prompt-comparison.md`.
- `.claude/agents/question-generator.md`: writes practice questions for a given role, level and question type.
- `.claude/agents/security-tester.md`: tests `src/guards.py` against injection attempts.
- `prompt_lab/injection_tests.ini`: 10 prompt-injection test cases for the JD Analyzer (a `[base]` posting with its correct answers, then one section per attack with `attack`, `position`, `input`, `refusal_allowed`, `forbidden` words (matched at the start of a word) and `pass_if`). For now they are run by hand; `server/tests/test_injection_tests_file.py` keeps the file valid.

Some of these still use old paths: `prompts/` is now `server/prompts/`, and `src/guards.py` is now `server/guards/`. `docs/prompt-comparison.md` doesn't exist yet. Update them as the app is built step by step.

## Notes

- Platform: Windows.
- Texts in the GUI are for the customer: no project terms ("MVP", "feature 3"), no developer notes ("This is the … page", "coming later: …"). Project terms belong in code comments and docs only. `section_header(title, subtitle, pill=None)`: pages only pass a pill if it says something useful to the user (e.g. "For IT & tech jobs"). Unbuilt tools say "coming soon" in plain words.
- HTML in `st.markdown(..., unsafe_allow_html=True)`: never let an empty line appear inside the HTML (e.g. from an empty `{placeholder}` or from joined f-strings). Markdown ends the HTML block there, and the indented lines after it are shown as a code block with the raw tags. Build optional or repeated parts on one line. After changing such HTML, check the pages in a real browser (look for code blocks / raw tags), not only with AppTest, which doesn't render Markdown.
- Look: `.streamlit/config.toml` follows `docs/stitch_interview_prep_web_app/DESIGN.md`. Light page with white, bordered inputs (`[theme]`); the sidebar is a dark "HUD" panel (`[theme.sidebar]`, `#0b1a11`). Dark HUD elements are for status and technical readouts, never for text the user types. `components/hud_bar.py` draws the dark terminal-style status bar (card 2 of the JD Analyzer); it HTML-escapes everything, because it shows user content. Its guard badge reads `server/guards/__init__.py` `GUARDS`: set a guard to `True` there when it is built.
- JD Analyzer screenshot input (up to 5 screenshots per posting, e.g. title + tasks; paste box; one Gemini 2.5 Flash call for all of them; flow into the text analysis): see `docs/jd-analyzer-screenshot.md`.
- Streamlit loads `client/api_client.py`, `client/components/` and `server/` only once at start: restart the app after changing them (pages in `views/` and prompts are re-read on every run).
- Authentication plan: `docs/streamlit-auth.md` recommends Streamlit's built-in OIDC (`st.login()` / `st.user`, Streamlit ≥ 1.45) with Google, with credentials in `.streamlit/secrets.toml`. Add that file to `.gitignore` before creating it.
