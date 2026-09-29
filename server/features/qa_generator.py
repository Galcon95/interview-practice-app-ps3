# Feature 1: Role-based Q&A generator (IT jobs only for now).
# Step 2: questions for a role and level. Model answers come later.

from server.llm import LLMClient
from server.prompt_loader import load_prompt


def generate_questions(role, level):
    # Returns a list of 5 interview questions (strings) for the role and level.
    system_prompt = load_prompt("qa_generator")
    user_prompt = f"Role: {role}\nLevel: {level}"
    reply = LLMClient().complete_json(system_prompt, user_prompt)
    return reply["questions"]
