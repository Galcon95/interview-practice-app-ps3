---
name: write-system-prompt
description: Use when adding or rewriting a system prompt for the app in prompts/ (e.g. a new prompting technique like self-consistency, ReAct, or a new interview mode).
---

# Write a system prompt

System prompts for the app live in `prompts/`, one file per technique.

## Steps

1. Create `prompts/<technique_name>.md`. Start the file with an HTML comment that names the technique and explains in one line why it's different, e.g.
   `<!-- Technique: Self-consistency. ... -->`
   The loader strips comments, so the model never sees them.
2. Use the placeholders `{role}`, `{level}` and `{question_type}`. `src/prompts.py` fills them in.
3. Keep the shared behavior: run a mock interview, ask **one question at a time**, and give feedback after each answer.
4. Don't add safety rules. `GUARDRAIL_PROMPT` in `src/guards.py` is appended automatically.
5. Register the file in `TECHNIQUES` in `src/prompts.py` (UI label -> filename).
6. Add a row for it in `docs/prompt-comparison.md`.

## Quality checklist

- The technique is actually different from the existing ones, not a reworded copy.
- The instructions are specific (format, length, tone) and don't contradict each other.
- The prompt still works for behavioral, technical and system design questions.
