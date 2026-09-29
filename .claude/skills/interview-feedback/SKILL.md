---
name: interview-feedback
description: Use when evaluating a candidate's answer to an interview question and giving structured, actionable feedback. Triggers on "review my answer", "give feedback on this interview answer", "how did I do", or when designing the app's feedback prompts/output format.
---

# Interview Feedback

Evaluate an interview answer and return structured feedback that the app can display.

## Inputs

- **Question**: the interview question that was asked.
- **Answer**: the candidate's response.
- **Context** (optional): target role, seniority level, question type (behavioral, technical, system design).

If the question or answer is missing, ask for it before evaluating.

## Steps

1. Identify the question type and what a strong answer needs (e.g. STAR structure for behavioral questions, correctness and trade-offs for technical ones).
2. Score the answer from 1 to 10 on each criterion:
   - **Clarity**: is it well structured and easy to follow?
   - **Relevance**: does it answer the question that was asked?
   - **Depth**: does it show real understanding, with specifics and examples?
3. List 2 strengths, quoting or pointing to the parts of the answer that show them.
4. List 2 improvements, each one concrete and something the candidate can act on.
5. Write a short model answer (under 150 words) that shows the improvements.

## Output format

```markdown
### Scores
| Criterion | Score | Note |
|-----------|-------|------|
| Clarity   | x/10  | ...  |
| Relevance | x/10  | ...  |
| Depth     | x/10  | ...  |

### Strengths
- ...
- ...

### Improvements
- ...
- ...

### Model answer
...
```

## Guidelines

- Be honest but encouraging. The goal is practice, not judgment.
- Keep the feedback specific to this answer. Avoid generic advice like "be more confident".
- Match expectations to the stated seniority level.
