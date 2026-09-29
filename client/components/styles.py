# Component: loads the design's fonts and CSS classes into the page.
# Call apply_styles() once at the top of every page.
# Colors and fonts come from docs/stitch_interview_prep_web_app/DESIGN.md.

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="st-"], p, li, label { font-family: 'Inter', sans-serif; }
h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; letter-spacing: -0.02em; }

/* Small green pill above a section title, e.g. "MVP FEATURES 1 & 2" */
.pill {
    display: inline-block; padding: 2px 10px; border-radius: 9999px;
    background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0;
    font: 700 12px 'Plus Jakarta Sans', sans-serif; letter-spacing: 0.06em;
    text-transform: uppercase;
}
.section-header { text-align: center; margin: 1rem 0 2rem; }
.section-header h1 { font-size: 40px; font-weight: 800; margin: 0.5rem 0; }
.section-header p { color: #64748b; font-size: 18px; }

/* Monospace label, e.g. "Role track: Senior Backend Developer" */
.mono { font: 500 13px 'JetBrains Mono', monospace; color: #64748b; }

/* Card for one "question to ask the interviewer" */
.reverse-q {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 12px 16px; margin-bottom: 12px;
}
.reverse-q .category {
    font: 700 12px 'Plus Jakarta Sans', sans-serif; color: #15803d;
    text-transform: uppercase; letter-spacing: 0.04em;
}

/* Green hint box, e.g. "Interviewer tip" */
.tip {
    background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
    padding: 12px 16px; color: #0f172a;
}
.tip b { color: #15803d; }

/* Rounded white cards for st.container(border=True) */
[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px; background: #fff; }

/* Pill-shaped buttons */
.stButton button { border-radius: 9999px; font-weight: 600; }
</style>
"""


def apply_styles():
    st.markdown(CSS, unsafe_allow_html=True)
