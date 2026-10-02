# Component: shows skills as colored tags (Streamlit Markdown badges).
# Green = required, gray = nice to have. Used by the job analyzer page
# (later also the resume match page, with matched / missing marks).

import streamlit as st


def skill_list(title, required, nice_to_have):
    """Draw one group of skills as colored tags: green = required, gray = nice to have.

    Args:
        title: the group's heading, e.g. "Tech stack".
        required: the required skills, a list of str.
        nice_to_have: the optional skills, a list of str.
    """
    st.markdown(f"**{title}**")
    if not required and not nice_to_have:
        st.caption("None mentioned")
        return
    if required:
        st.markdown(" ".join(badge(skill, "green") for skill in required))
    if nice_to_have:
        st.caption("Nice to have")
        st.markdown(" ".join(badge(skill, "gray") for skill in nice_to_have))


def badge(text, color):
    """Turn a text into Streamlit Markdown for a colored tag, e.g. ":green-badge[C++]".

    Square brackets in the text would end the tag early, so they become
    round brackets.

    Args:
        text: the text on the tag, e.g. "C++".
        color: a Streamlit color name, e.g. "green" or "gray".

    Returns:
        The Markdown (str) for st.markdown().
    """
    text = text.replace("[", "(").replace("]", ")")
    return f":{color}-badge[{text}]"
