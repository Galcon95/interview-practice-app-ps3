# Page — Feature 3: Job description analyzer.
# The workflow has 3 steps, each shown as its own section on this page:
#   1. Paste     the user pastes the job description (JD) text,         <- done
#                or screenshots that the AI turns into text first
#   2. Review    the AI extracts basic info, role metadata and skills    <- done (editing: TODO)
#   3. Plan      a strategy dashboard with next actions                  (TODO)
#
# What the page remembers between reruns (st.session_state):
#   "jd_input_mode" which input view is shown: "📝 Text" or "🖼️ Screenshot"
#   "jd_input"      what is typed in the text box (kept while hidden, also across pages)
#   "jd_screenshots" the pasted or uploaded screenshots in reading order: a list of {"name", "data"}
#   "jd_show_text", "jd_read_note"  short-lived notes after "Process screenshots" (see below)
#   "jd_text"       the JD that passed validation, or missing if none yet
#   "jd_analysis"   the AI's result for that JD:
#                   {"basic_info", "role_metadata", "skills", "other_requirements"}
#   "jd_meta"       how that result was made: {"source", "model"}, shown in the HUD bar

import streamlit as st

import api_client
from components.section_header import section_header
from components.job_overview import job_overview
from components.skill_list import skill_list
from components.screenshot_input import screenshot_input
from components.hud_bar import hud_bar

# --- Page --- (page config and styles are set once in app.py)
section_header(
    "Job Description Analyzer",
    "Paste a job posting. Get the role, the skills and a prep plan for the interview.",
)

min_chars, max_chars = api_client.get_job_description_limits()
settings = st.session_state.get("llm_settings")  # from the sidebar (set in app.py)


def analyze(text, source="pasted text"):
    """Check a job description, then let the AI analyze it, and store the result.

    Problems are shown on the page with st.error(). On success, the text and
    the result are stored in st.session_state["jd_text"] and ["jd_analysis"].

    Args:
        text: the job description, from the text box or read from a screenshot.
        source: where the text came from, for the HUD bar, e.g. "2 screenshots".

    Returns:
        True if the analysis worked, False if the text was refused or the call failed.
    """
    error = api_client.validate_job_description(text)
    if error:
        st.error(error)
        return False
    with st.spinner("The AI is analyzing the job description..."):
        try:
            analysis = api_client.analyze_job_description(text.strip(), settings)
        except Exception as error:
            st.error(f"Could not analyze the job description: {error}")
            return False
    # Saved in session_state, so they survive the reruns of the next steps.
    st.session_state["jd_text"] = text.strip()
    st.session_state["jd_analysis"] = analysis
    model = (settings or api_client.get_default_settings())["model"]
    st.session_state["jd_meta"] = {"source": source, "model": model.split("/")[-1]}
    return True


# After "Process" the page shows the Text view with the text read from the screenshot.
# A widget's value can only be changed before the widget is drawn, so the Process button
# leaves a note ("jd_show_text") and reruns the page, and the switch is made here.
if st.session_state.pop("jd_show_text", False):
    st.session_state["jd_input_mode"] = "📝 Text"

# --- Step 1: Paste the job description (as text or as a screenshot) ---
with st.container(border=True):
    st.markdown("#### 1. Paste the job description")
    input_mode = st.segmented_control(
        "Input",
        ["📝 Text", "🖼️ Screenshot"],
        default="📝 Text",
        required=True,  # one option is always selected, clicking it again does not clear it
        key="jd_input_mode",
        label_visibility="collapsed",
    )

    if input_mode == "🖼️ Screenshot":
        screenshots = screenshot_input(
            key="jd_screenshots",
            validate=api_client.validate_screenshots,
            limits=api_client.get_screenshot_limits(),
        )
        # The text box is hidden, but its text is kept (persist_state in the text view).
        text = st.session_state.get("jd_input", "")

        count = len(screenshots)
        label = "Process screenshot" if count == 1 else f"Process {count} screenshots"
        if screenshots and st.button(label, type="primary", icon=":material/document_scanner:"):
            with st.spinner("The AI is reading the screenshots..."):
                try:
                    read_text = api_client.read_job_screenshots([shot["data"] for shot in screenshots])
                except Exception as error:
                    st.error(f"Could not read the screenshots: {error}")
                    read_text = None
            source = "1 screenshot" if count == 1 else f"{count} screenshots"
            if read_text is not None and analyze(read_text, source=source):
                # Put the text into the text box (it is not drawn in this view, so this is allowed).
                st.session_state["jd_input"] = read_text
                st.session_state["jd_show_text"] = True
                read_from = screenshots[0]["name"] if count == 1 else f"{count} screenshots"
                st.session_state["jd_read_note"] = f"Text read from {read_from}. Check it below."
                st.rerun()
            elif read_text:
                # The analysis failed (e.g. text too short), but show what was read anyway.
                st.text_area("Text read from the screenshots", read_text, height=200, disabled=True)
    else:
        if "jd_read_note" in st.session_state:
            st.success(st.session_state.pop("jd_read_note"), icon=":material/document_scanner:")
        text = st.text_area(
            "Job description",
            height=280,
            max_chars=max_chars,  # the text area itself stops the user at the limit
            placeholder="Paste the full job posting here: title, company, responsibilities, requirements...",
            label_visibility="collapsed",
            key="jd_input",
            persist_state="session",  # keep the text while hidden (Screenshot view, other pages)
        )
        st.markdown(
            f'<span class="mono">{len(text.strip())} characters · at least {min_chars} needed</span>',
            unsafe_allow_html=True,
        )
        if st.button("Analyze job description", type="primary"):
            analyze(text)

# --- Step 2: Review the extracted details ---
with st.container(border=True):
    st.markdown("#### 2. Review role and skills")
    if "jd_analysis" not in st.session_state:
        st.info("Paste a job description and click **Analyze job description**.")
    else:
        analysis = st.session_state["jd_analysis"]
        meta = st.session_state.get("jd_meta", {"source": "pasted text", "model": "default model"})
        hud_bar(
            path=["intervai", "jd-analysis", analysis["basic_info"].get("job_title") or "unknown role"],
            details=[f"source: {meta['source']}", f"model: {meta['model']}"],
            guards=api_client.get_guard_status(),
        )
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
    st.info("Coming soon: a prep plan for this job, with the topics to focus on and your next steps.")
