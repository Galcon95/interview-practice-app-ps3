# Component: shows the job analysis from the LLM (feature 3, step 2):
# a title line "Job title @ Company", then the location and role metadata as tiles.
# Missing values (None) are shown as "Not stated".

import streamlit as st


def job_overview(analysis):
    """Draw the job overview: "🎯 Job title @ Company", then 3 tiles (seniority, focus, location).

    Under each tile is the model's reason for its choice. Missing values are
    shown as "Not stated" or "Not detected".

    Args:
        analysis: the result of api_client.analyze_job_description(); uses its
            "basic_info" and "role_metadata" parts.
    """
    info = analysis["basic_info"]
    meta = analysis["role_metadata"]

    title = info.get("job_title") or "Unknown role"
    company = info.get("company") or "Unknown company"
    details = [d for d in (info.get("employment_type"), info.get("work_mode")) if d]
    st.markdown(f"##### 🎯 {title} @ {company}")
    if details:
        st.markdown(f'<span class="mono">{" | ".join(details)}</span>', unsafe_allow_html=True)

    col_level, col_focus, col_location = st.columns(3)
    with col_level:
        st.metric("Seniority (inferred)", meta.get("seniority") or "Not detected")
        st.caption(meta.get("seniority_reason") or "")
    with col_focus:
        st.metric("Role focus", meta.get("role_focus") or "Not detected")
        st.caption(meta.get("role_focus_reason") or "")
    with col_location:
        st.metric("Location", info.get("location") or "Not stated")
        st.caption(f"Work mode: {info.get('work_mode') or 'Not stated'}")
