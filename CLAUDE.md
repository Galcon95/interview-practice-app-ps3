# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

An interview-practice web app built with Streamlit (Python), for a Turing College project. It's at an early stage: `test-app.py` is a Streamlit "Hello World" used to check the setup, and the rest is placeholder files.

MVP features: (1) role-based Q&A generator, IT jobs only; (2) "questions to ask the interviewer", together with 1; (3) job description analyzer (role + skills, then 1 and 2); (4) self-introduction polisher; (5) resume upload and skill match against a job (coverage %); (6) security guards: input validation, prompt-injection filter, scope enforcement in the system prompt, optional rate limiting.

- `client/`: front end (Streamlit). `app.py` is the home page, `api_client.py` has one call per feature, `pages/` holds one screen per feature (number prefix sets menu order), `components/` holds reusable widgets that pages combine.
- `server/`: back end. `main.py` is the API (one endpoint per feature), `features/` has one module per feature, `guards/` has guards 1, 2 and 4, `prompts/` has one system prompt per feature plus `guardrail.md` (guard 3), `prompt_loader.py` reads them, `llm.py` calls the model, `document_reader.py` turns resumes into text. Secrets go in `server/.env` (see `.env.example`).

## Commands

```bash
pip install streamlit          # use "streamlit[auth]" if using st.login (see docs/streamlit-auth.md)
streamlit run test-app.py      # serves on http://localhost:8501
```

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
- Authentication plan: `docs/streamlit-auth.md` recommends Streamlit's built-in OIDC (`st.login()` / `st.user`, Streamlit ≥ 1.45) with Google, with credentials in `.streamlit/secrets.toml`. Add that file to `.gitignore` before creating it.
