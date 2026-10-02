# Component: a panel with a title, its own "Generate" button and a list of questions.
# It is configurable, so the same panel is used for interview questions
# and for questions to ask the interviewer (and later on the JD Analyzer page).
# Parameters: see the docstring of question_panel().

import streamlit as st


def question_panel(key, title, button_label, generate, render_item, label):
    """Draw a panel with a title, a "Generate" button and the list of results.

    The results are kept in st.session_state, because the page reruns on every
    click. If the call fails, the error is shown in the panel.

    Args:
        key: a unique name for this panel. It keeps the results of several
            panels on one page apart in st.session_state.
        title: the heading of the panel.
        button_label: the text on the button, e.g. "Generate interview questions".
        generate: a function without arguments that is called on click and
            returns a list of items (it calls api_client).
        render_item: a function render_item(number, item) that draws one item,
            e.g. qa_card.
        label: the text shown above the results, e.g. "Junior Backend Developer · GPT-5 mini".
    """
    with st.container(border=True):
        st.markdown(f"#### {title}")

        # The script reruns on every click, so the results live in st.session_state.
        if st.button(button_label, type="primary", key=f"{key}_button"):
            with st.spinner("Asking the AI..."):
                try:
                    st.session_state[f"{key}_items"] = generate()
                    st.session_state[f"{key}_label"] = label
                except Exception as error:
                    st.error(f"Could not generate questions: {error}")

        items = st.session_state.get(f"{key}_items", [])
        if not items:
            st.info(f"Pick a role and level, then click **{button_label}**.")
            return

        st.markdown(
            f'<span class="mono">Generated for: {st.session_state[f"{key}_label"]}</span>',
            unsafe_allow_html=True,
        )
        for number, item in enumerate(items, start=1):
            render_item(number, item)
