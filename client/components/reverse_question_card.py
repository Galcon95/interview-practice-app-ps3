# Component: one "question to ask the interviewer", with its category.
# Used by the Q&A generator and job analyzer pages.

import streamlit as st


def reverse_question_card(category, question):
    st.markdown(
        f"""
        <div class="reverse-q">
            <div class="category">{category}</div>
            <div>"{question}"</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
