# Component: shows skills as colored tags (Streamlit Markdown badges).
# Green = required, gray = nice to have. Used by the job analyzer page
# (later also the resume match page, with matched / missing marks).

import streamlit as st


def skill_list(title, required, nice_to_have):
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
    # ":green-badge[C++]" is drawn as a tag; square brackets in the text would end the tag early.
    text = text.replace("[", "(").replace("]", ")")
    return f":{color}-badge[{text}]"
