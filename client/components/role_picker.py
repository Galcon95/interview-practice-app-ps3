# Component: dropdowns for IT role and seniority level.
# Used by the Q&A generator page. Returns (role, level).

import streamlit as st

ROLES = [
    "Frontend Developer",
    "Backend Developer",
    "Full-Stack Developer",
    "DevOps / SRE",
    "Data / AI Engineer",
    "QA Engineer",
]
LEVELS = ["Junior", "Mid", "Senior", "Lead"]


def role_picker():
    col_role, col_level = st.columns(2)
    role = col_role.selectbox("Role", ROLES)
    level = col_level.selectbox("Level", LEVELS)
    return role, level
