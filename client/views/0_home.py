# Page: Home. Built like the home page in docs/stitch_interview_prep_web_app/:
#   1. Hero: headline, two buttons into the app, chips
#   2. How it works: 3 numbered steps
#   3. Feature cards: one per feature, with its status and a link
#   4. Security guards: a dark section with the real status of each guard
# The CSS classes (.chips, .steps, .feature, .guard-section, ...) are in components/styles.py.

import streamlit as st

import api_client
from components.section_header import section_header

# Pages, in the same order and with the same icons as the menu in app.py.
FEATURES = [
    {
        "icon": "💬",
        "title": "Role Q&A",
        "text": "Practice interview questions for your IT role and level, plus smart questions to ask the interviewer.",
        "page": "views/1_qa_generator.py",
        "live": True,
    },
    {
        "icon": "📄",
        "title": "JD Analyzer",
        "text": "Paste a job posting or screenshots. Get the title, seniority, focus and the exact skills it asks for.",
        "page": "views/2_job_analyzer.py",
        "live": True,
    },
    {
        "icon": "✍️",
        "title": "Intro Polisher",
        "text": 'Turn your "tell me about yourself" into a clear, confident pitch for the interview.',
        "page": "views/3_intro_polisher.py",
        "live": False,
    },
    {
        "icon": "🎯",
        "title": "Resume Matcher",
        "text": "Upload your resume and see how well it covers the skills the job asks for.",
        "page": "views/4_resume_match.py",
        "live": False,
    },
]

# What each guard does, by its name in server/guards/__init__.py GUARDS.
GUARD_TEXTS = {
    "Input validation": "Checks length, file type and size before any AI call, so bad input never costs money.",
    "Prompt-injection filter": 'Catches attempts like "ignore your instructions" hidden in the text you paste.',
    "Scope enforcement": "Every AI prompt ends with rules that keep the AI on interview preparation for IT jobs.",
    "Rate limiting": "Limits the AI calls per minute, so a stuck button or a script can't run up the bill.",
}

# --- 1. Hero --- (page config and styles are set once in app.py)
section_header(
    'AI-Powered <span class="highlight">IT Interview</span> Preparation',
    "Analyze job descriptions, match your resume, polish your intro and practice role-based Q&A.",
    pill="For IT & tech jobs",
)

with st.container(horizontal=True, horizontal_alignment="center"):
    if st.button("Analyze a job description", type="primary", icon=":material/arrow_forward:", icon_position="right"):
        st.switch_page("views/2_job_analyzer.py")
    if st.button("Practice Role Q&A", icon=":material/forum:"):
        st.switch_page("views/1_qa_generator.py")

st.markdown(
    """
    <div class="chips">
        <span class="chip">⚡ JD skill extraction</span>
        <span class="chip">🖼️ Screenshot input</span>
        <span class="chip">🛡️ Security guards</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 2. How it works ---
st.markdown(
    """
    <div class="home-section">
        <span class="pill">How it works</span>
        <h2>From job posting to interview practice</h2>
    </div>
    <div class="steps">
        <div class="step"><span class="num">01</span>
            <div><b>Paste a job description</b><span>As text, or as screenshots of the posting.</span></div></div>
        <div class="step"><span class="num">02</span>
            <div><b>Review role and skills</b><span>The AI finds the level, the focus and the required skills.</span></div></div>
        <div class="step"><span class="num">03</span>
            <div><b>Practice questions</b><span>Interview questions for the role, and questions to ask back.</span></div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- 3. Feature cards ---
st.markdown(
    """
    <div class="home-section">
        <span class="pill">Features</span>
        <h2>Everything for your next IT interview</h2>
    </div>
    """,
    unsafe_allow_html=True,
)
for row in (FEATURES[:2], FEATURES[2:]):
    for column, feature in zip(st.columns(2, gap="medium"), row):
        with column, st.container(border=True):
            badge = '<span class="badge-live">Live</span>' if feature["live"] else '<span class="badge-soon">Coming soon</span>'
            st.markdown(
                f"""
                <div class="feature">
                    <div class="feature-head"><span class="icon">{feature["icon"]}</span>{badge}</div>
                    <h4>{feature["title"]}</h4>
                    <p>{feature["text"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(
                feature["page"],
                label="Open" if feature["live"] else "Coming soon",
                icon=":material/arrow_forward:" if feature["live"] else ":material/schedule:",
                icon_position="right",
                disabled=not feature["live"],
            )

# --- 4. Security guards (dark section, real status from the server) ---
guards = api_client.get_guard_status()
# Each card on one line: an empty line inside HTML would end the HTML block in Markdown.
cards = "".join(
    f'<div class="guard"><span class="label">GUARD {number:02d}</span><b>{name}</b>'
    f'<span>{GUARD_TEXTS.get(name, "")}</span><br>'
    f'<span class="state {"on" if active else "planned"}">{"● Active" if active else "○ Planned"}</span></div>'
    for number, (name, active) in enumerate(guards.items(), start=1)
)
st.markdown(
    f"""
    <div class="guard-section">
        <div class="home-section">
            <span class="pill">Security</span>
            <h2>Built-in security guards</h2>
            <p>{sum(guards.values())} of {len(guards)} guards are active. They run before every AI call.</p>
        </div>
        <div class="guards">{cards}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
