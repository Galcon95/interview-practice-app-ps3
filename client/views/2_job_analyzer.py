# Page — Feature 3: Job description analyzer.
# The workflow has 3 steps, each shown as its own section on this page:
#   1. Paste     the user pastes the job description (JD) text          <- done
#   2. Review    the AI extracts basic info, role metadata and skills    <- done (editing: TODO)
#   3. Plan      a strategy dashboard with next actions                  (TODO)
#
# What the page remembers between reruns (st.session_state):
#   "jd_text"       the JD that passed validation, or missing if none yet
#   "jd_analysis"   the AI's result for that JD:
#                   {"basic_info", "role_metadata", "skills", "other_requirements"}

import streamlit as st

import api_client
from components.section_header import section_header
from components.job_overview import job_overview
from components.skill_list import skill_list

# --- Page --- (page config and styles are set once in app.py)
section_header(
    "MVP feature 3",
    "Job Description Analyzer",
    "Paste a job posting. Get the role, the skills and a prep plan for the interview.",
)

min_chars, max_chars = api_client.get_job_description_limits()
settings = st.session_state.get("llm_settings")  # from the sidebar (set in app.py)

# --- Step 1: Paste the job description ---
with st.container(border=True):
    st.markdown("#### 1. Paste the job description")
    text = st.text_area(
        "Job description",
        height=280,
        max_chars=max_chars,  # the text area itself stops the user at the limit
        placeholder="Paste the full job posting here: title, company, responsibilities, requirements...",
        label_visibility="collapsed",
    )
    st.markdown(
        f'<span class="mono">{len(text.strip())} characters · at least {min_chars} needed</span>',
        unsafe_allow_html=True,
    )

    if st.button("Analyze job description", type="primary"):
        error = api_client.validate_job_description(text)  # guard 1, before any paid call
        if error:
            st.error(error)
        else:
            with st.spinner("The AI is reading the job description..."):
                try:
                    analysis = api_client.analyze_job_description(text.strip(), settings)
                    # Saved in session_state, so they survive the reruns of the next steps.
                    st.session_state["jd_text"] = text.strip()
                    st.session_state["jd_analysis"] = analysis
                except Exception as error:
                    st.error(f"Could not analyze the job description: {error}")

# --- Step 2: Review the extracted details ---
with st.container(border=True):
    st.markdown("#### 2. Review role and skills")
    if "jd_analysis" not in st.session_state:
        st.info("Paste a job description and click **Analyze job description**.")
    else:
        analysis = st.session_state["jd_analysis"]
        job_overview(analysis)

        st.divider()
        st.markdown("##### Required skills")
        skills = analysis["skills"]
        col_hard, col_concepts, col_soft = st.columns(3, gap="large")
        with col_hard:
            skill_list("Tech stack", **skills["hard_skills"])
        with col_concepts:
            skill_list("Concepts & domain", **skills["concepts"])
        with col_soft:
            skill_list("Soft skills", **skills["soft_skills"])

        if analysis["other_requirements"]:
            st.markdown("**Other requirements**")
            for requirement in analysis["other_requirements"]:
                st.markdown(f"- {requirement}")

        if st.session_state["jd_text"] != text.strip():
            st.warning("The text above has changed. Click **Analyze job description** again to update.")

# --- Step 3: Strategy dashboard (later block) ---
with st.container(border=True):
    st.markdown("#### 3. Your interview prep plan")
    st.info("Coming later: focus breakdown, must-know stack, priority topics and next actions.")
