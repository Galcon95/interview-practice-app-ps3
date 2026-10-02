<!-- Technique 1: Zero-shot, minimal.
     Just the request, as a user would type it, plus the reply format.
     No role, no rules, no examples. -->
Give me 5 interview questions for the job title and level the user gives you.

Reply with JSON only, in exactly this format:
{"questions": ["question 1", "question 2", "question 3", "question 4", "question 5"]}
