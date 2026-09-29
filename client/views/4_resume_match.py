# Page — Feature 5: Resume vs. job skills matching.
# The user uploads a resume and pastes a job description; the app shows
# which skills match, which are missing, and the coverage (e.g. 60%).

# TODO: document_upload + job text -> api_client.match_resume
#       -> match_score + skill_list (matched / missing)

import streamlit as st

st.write('This is the resume matching page.')