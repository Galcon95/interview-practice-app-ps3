---
name: compare-prompts
description: Use when comparing the app's system prompt techniques against each other, to decide which works best and to fill in docs/prompt-comparison.md.
---

# Compare prompt techniques

The goal is a fair comparison of every technique listed in `TECHNIQUES` (`src/prompts.py`).

## Steps

1. **Fix the setup.** Pick one role, level, question type, model and temperature, and use them for every technique.
2. **Prepare test answers.** Use the `question-generator` agent for questions if needed. For each question, write three candidate answers:
   - a strong answer
   - a weak or vague answer
   - a misuse attempt (off-topic request or prompt injection)
3. **Run each technique** in the app, or with a short script that calls `src.llm.stream_chat` using `build_system_prompt(...)`. Save the outputs.
4. **Score each technique** from 1 to 5 on question quality, feedback usefulness and format consistency. Record whether the guard held.
5. **Fill in** the table and the conclusion in `docs/prompt-comparison.md`. Quote short snippets of the outputs as evidence.

## Rules

- Change only one variable at a time: the technique.
- Record the model and the date. Results can change between model versions.
- Real API calls cost money. Say how many calls you plan to make before running a script.
