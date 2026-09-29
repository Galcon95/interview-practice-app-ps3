# Page: Home. Short welcome and an overview of the features.

import streamlit as st

from components.section_header import section_header

section_header(
    "IT & tech MVP edition",
    "AI-Powered IT Interview Preparation",
    "Analyze job descriptions, match your resume, polish your intro "
    "and practice role-based Q&A.",
)

st.markdown(
    """
- **Role Q&A**: practice questions with model answers, plus questions to ask the interviewer
- **JD Analyzer**: find the role and skills in a job description
- **Intro Polisher**: improve your "tell me about yourself" answer
- **Resume Matcher**: check how well your resume covers the job's skills
"""
)

st.write('This is the home page.')
