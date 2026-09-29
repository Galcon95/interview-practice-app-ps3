# Feature 2: "Questions to ask the interviewer" generator.
# Used together with feature 1 (same role / level).

from server.llm import LLMClient
from server.prompt_loader import load_prompt


def generate_interviewer_questions(role, level):
    # Returns a list of 5 dicts: {"category": "...", "question": "..."}
    system_prompt = load_prompt("interviewer_questions")
    user_prompt = f"Role: {role}\nLevel: {level}"
    reply = LLMClient().complete_json(system_prompt, user_prompt)
    return reply["questions"]
