# Component: centered page header with an optional pill, a big title and a subtitle.
# Used at the top of every page.

import streamlit as st


def section_header(title, subtitle, pill=None):
    """Draw the centered page header: an optional small green pill, a big title and a subtitle.

    Args:
        title: the page title. May contain a little HTML, e.g.
            '<span class="highlight">IT Interview</span>' for a green keyword.
            Only for fixed texts written in the code, never for user input,
            because the title is drawn as HTML without escaping.
        subtitle: one sentence under the title.
        pill: a short label above the title for the user, e.g. "For IT & tech jobs",
            or None for no pill. Not for project terms such as "MVP feature 3".
    """
    pill_html = f'<span class="pill">{pill}</span>' if pill else ""
    # One line on purpose: an empty line inside HTML (e.g. when there is no pill) ends the
    # HTML block in Markdown, and the indented lines after it would be shown as code.
    st.markdown(
        f'<div class="section-header">{pill_html}<h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
