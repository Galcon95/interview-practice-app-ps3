# Page — Feature 1 + 2: Role-based Q&A generator (IT jobs only for now).
# The user picks an IT role and level once. Two panels, each with its own button:
#   left:  interview questions for the role (feature 1)
#   right: questions to ask the interviewer (feature 2)
# Both panels are the same configurable component, question_panel.

import streamlit as st

import api_client
from components.section_header import section_header
from components.role_picker import role_picker
from components.question_panel import question_panel
from components.qa_card import qa_card
from components.reverse_question_card import reverse_question_card

# --- Page --- (page config and styles are set once in app.py)
section_header(
    "Role-Based Q&A & Reverse Questions Generator",
    "Practice questions with model answers, plus smart questions to ask the interviewer.",
)

role, level = role_picker(*api_client.get_roles_and_levels())  # shared by both panels
settings = st.session_state.get("llm_settings")  # from the sidebar (set in app.py)
model = settings["model"] if settings else "default model"

col_role, col_reverse = st.columns(2, gap="large")

with col_role:
    question_panel(
        key="role_questions",
        title="Interview questions",
        button_label="Generate interview questions",
        generate=lambda: api_client.generate_questions(role, level, settings),
        render_item=qa_card,  # qa_card(number, question)
        label=f"{level} {role} · {model}",
    )
    st.markdown(
        '<div class="tip"><b>Interviewer tip:</b> Senior interviewers ask about '
        "trade-offs. Say why you chose one tool over another.</div>",
        unsafe_allow_html=True,
    )

with col_reverse:
    question_panel(
        key="reverse_questions",
        title="Questions to ask the interviewer",
        button_label="Generate reverse questions",
        generate=lambda: api_client.generate_interviewer_questions(role, level, settings),
        render_item=lambda number, item: reverse_question_card(item["category"], item["question"]),
        label=f"{level} {role} · {model}",
    )
