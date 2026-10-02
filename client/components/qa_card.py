# Component: one interview question with its model answer in STAR format.
# The answer is hidden in an expander so the user can try to answer first.
# Used by the Q&A generator and job analyzer pages.

import streamlit as st


def qa_card(number, question, answer=None):
    """Draw one interview question as a card, with its model answer hidden in an expander.

    Args:
        number: the question's number, shown as "Q1.", "Q2.", ...
        question: the question text.
        answer: the model answer as a dict {"situation", "action", "result"}
            (STAR format), or None. With None, only the question is shown (no
            expander); that is the case while the app only generates questions.
    """
    with st.container(border=True):
        st.markdown(f"**Q{number}. {question}**")
        if answer is None:
            return
        with st.expander("Show model answer (STAR)"):
            st.markdown(f"**Situation & Task:** {answer['situation']}")
            st.markdown(f"**Action:** {answer['action']}")
            st.markdown(f"**Result:** {answer['result']}")
