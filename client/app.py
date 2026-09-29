# Front end entry point of the Interview Preparation App.
# Run from the project root with: streamlit run client/app.py
#
# Flow on every click:
#   app.py -> page config + styles -> st.navigation (menu) -> page.run() -> the chosen page file

import streamlit as st

import api_client
from components.styles import apply_styles
from components.settings_sidebar import settings_sidebar

# All pages of the app, in menu order. Paths are relative to this file.
pages = [
    st.Page("views/0_home.py", title="Home", icon="🏠", default=True),
    st.Page("views/1_qa_generator.py", title="Role Q&A", icon="💬"),
    st.Page("views/2_job_analyzer.py", title="JD Analyzer", icon="📄"),
    st.Page("views/3_intro_polisher.py", title="Intro Polisher", icon="✍️"),
    st.Page("views/4_resume_match.py", title="Resume Matcher", icon="🎯"),
]

st.set_page_config(page_title="IntervAI", layout="wide")  # once, for all pages
apply_styles()                                             # once, for all pages

# LLM settings in the sidebar, for all pages. Pages read them from session_state.
st.session_state["llm_settings"] = settings_sidebar(
    api_client.get_models(), api_client.get_default_settings()
)

page = st.navigation(pages)  # draws the menu, returns the page that was clicked
page.run()                   # runs that page's file

# streamlit run client/app.py