# Component: centered page header with a pill, a big title and a subtitle.
# Used at the top of every feature page.

import streamlit as st


def section_header(pill, title, subtitle):
    st.markdown(
        f"""
        <div class="section-header">
            <span class="pill">{pill}</span>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
