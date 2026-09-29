# Component: a panel with a title, its own "Generate" button and a list of questions.
# It is configurable, so the same panel is used for interview questions
# and for questions to ask the interviewer (and later on the JD Analyzer page).
#
#   key          unique name, keeps each panel's results apart in st.session_state
#   title        heading of the panel
#   button_label text on the button
#   generate     function called on click, with no arguments, that returns a list of items
#   render_item  function that draws one item: render_item(number, item)
#   label        text shown above the results, e.g. "Junior Backend Developer"

import streamlit as st


def question_panel(key, title, button_label, generate, render_item, label):
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
