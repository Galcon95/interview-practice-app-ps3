# Page — Feature 5: Resume vs. job skills matching.
# The user uploads a resume and pastes a job description; the app shows
# which skills match, which are missing, and the coverage (e.g. 60%).

# TODO: document_upload + job text -> api_client.match_resume
#       -> match_score + skill_list (matched / missing)

import streamlit as st

from components.section_header import section_header

section_header(
    "Resume Matcher",
    "Upload your resume and see how well it covers the skills the job asks for.",
)
st.info("This tool is coming soon. Meanwhile, try the **JD Analyzer** or **Role Q&A**.", icon=":material/schedule:")
