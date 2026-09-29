# Component: one interview question with its model answer in STAR format.
# The answer is hidden in an expander so the user can try to answer first.
# Used by the Q&A generator and job analyzer pages.

import streamlit as st


def qa_card(number, question, answer=None):
    # answer is a dict with the keys "situation", "action", "result",
    # or None while we only generate questions (no expander then).
    with st.container(border=True):
        st.markdown(f"**Q{number}. {question}**")
        if answer is None:
            return
        with st.expander("Show model answer (STAR)"):
            st.markdown(f"**Situation & Task:** {answer['situation']}")
            st.markdown(f"**Action:** {answer['action']}")
            st.markdown(f"**Result:** {answer['result']}")
