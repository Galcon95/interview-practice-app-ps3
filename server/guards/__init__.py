# Feature 6: Security guards. They run before any LLM call.
# Guard 3 (scope enforcement) is a system prompt: see prompts/guardrail.md.

# Which guards are built and running. The page shows this (e.g. "Guards 3/4 active"),
# so update it when a guard is added.
GUARDS = {
    "Input validation": True,         # guard 1: guards/input_validation.py
    "Prompt-injection filter": False,  # guard 2: guards/injection_filter.py (not built yet)
    "Scope enforcement": True,         # guard 3: prompts/guardrail.md + prompt_loader.py
    "Rate limiting": True,             # guard 4: guards/rate_limit.py
}
