# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

An interview-practice web app built with Streamlit (Python), for a Turing College project. It's at an early stage: `test-app.py` is a Streamlit "Hello World" used to check the setup, and the rest is placeholder files.

MVP features: (1) role-based Q&A generator, IT jobs only; (2) "questions to ask the interviewer", together with 1; (3) job description analyzer (role + skills, then 1 and 2); (4) self-introduction polisher; (5) resume upload and skill match against a job (coverage %); (6) security guards: input validation, prompt-injection filter, scope enforcement in the system prompt, optional rate limiting.

- `client/`: front end (Streamlit). `app.py` is the entry point: it sets page config and styles once, then lists every page with `st.navigation(position="top")` (menu order and labels are set there; the menu is in the top bar, the sidebar only holds the LLM settings). `views/` holds one page per feature (not named `pages/`, which would switch on Streamlit's automatic page discovery and clash with `st.navigation`), `api_client.py` has one call per feature, `components/` holds reusable widgets that pages combine.
- `server/`: back end. `main.py` is the API (one endpoint per feature), `features/` has one module per feature, `guards/` has guards 1, 2 and 4, `prompts/` has one system prompt per feature plus `guardrail.md` (guard 3), `prompt_loader.py` reads them, `llm.py` calls the model, `document_reader.py` turns resumes into text. Secrets go in `server/.env` (see `.env.example`).
- LLM: OpenRouter via the `openai` package (`server/llm.py`, class `LLMClient`, default model `openai/gpt-5-mini`, JSON replies). The key is `OPENROUTER_API_KEY`, from `server/.env` or a Windows environment variable (already set on this machine, so tests that click "Generate" make real, paid calls).
- LLM settings: `server/llm.py` defines `MODELS` (label + whether the model supports temperature) and the defaults. `components/settings_sidebar.py` is drawn once in `app.py` and stored in `st.session_state["llm_settings"]`; pages pass it through `api_client` to the feature, which does `LLMClient(**settings)`. GPT-5 models ignore temperature (not sent) and count hidden reasoning in `max_tokens`, so keep it high (default 4000). A cut-off reply (`finish_reason == "length"`) raises a clear error.
- Debug log: `LLMClient` logs every request payload and raw reply through `LLMLogger` (`server/llm_logger.py`) to the terminal and `server/logs/llm.log` (git-ignored, rotates at 1 MB). `LLM_LOG_LEVEL` = DEBUG (default, full JSON), INFO (one line per call) or WARNING (errors only).
- No FastAPI for now: `client/api_client.py` adds the project root to `sys.path` and imports `server/` directly. It's the only client file allowed to touch `server/`.

## Commands

```bash
pip install -r client/requirements.txt -r server/requirements.txt   # use "streamlit[auth]" if using st.login (see docs/streamlit-auth.md)
streamlit run client/app.py              # run from the project root; serves on http://localhost:8501
```

Always start from the project root: `.streamlit/config.toml` (the theme) is only read from the folder Streamlit is started in. Streamlit is installed in Python 3.13; the bare `python` in the shell points to an unrelated venv, so use `py -3.13` if needed.

`client/requirements.txt` and `server/requirements.txt` list dependencies. Tests in `server/tests/` are empty placeholders, and there's no linter config yet.

## Skills and agents

- `.claude/skills/interview-feedback/`: review an interview answer (scores, strengths, improvements, model answer).
- `.claude/skills/write-system-prompt/`: add a new prompt technique to `prompts/`.
- `.claude/skills/compare-prompts/`: compare the prompt techniques and fill in `docs/prompt-comparison.md`.
- `.claude/agents/question-generator.md`: writes practice questions for a given role, level and question type.
- `.claude/agents/security-tester.md`: tests `src/guards.py` against injection attempts.

Some of these still use old paths: `prompts/` is now `server/prompts/`, and `src/guards.py` is now `server/guards/`. `docs/prompt-comparison.md` doesn't exist yet. Update them as the app is built step by step.

## Notes

- Platform: Windows.
- JD Analyzer screenshot input (paste box, Gemini 2.5 Flash reading, flow into the text analysis): see `docs/jd-analyzer-screenshot.md`.
- Streamlit loads `client/api_client.py`, `client/components/` and `server/` only once at start: restart the app after changing them (pages in `views/` and prompts are re-read on every run).
- Authentication plan: `docs/streamlit-auth.md` recommends Streamlit's built-in OIDC (`st.login()` / `st.user`, Streamlit ≥ 1.45) with Google, with credentials in `.streamlit/secrets.toml`. Add that file to `.gitignore` before creating it.
