# Component: loads the design's fonts and CSS classes into the page.
# app.py calls apply_styles() once, for all pages.
# Colors and fonts come from docs/stitch_interview_prep_web_app/DESIGN.md.

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

html, body, [class*="st-"], p, li, label { font-family: 'Inter', sans-serif; }
/* ...but not for Streamlit's icons (icon=":material/..."), they need their own icon font */
[data-testid="stIconMaterial"], [data-testid="stAlertDynamicIcon"] {
    font-family: 'Material Symbols Rounded' !important;
}
h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif !important; letter-spacing: -0.02em; }

/* Small green pill above a section title, e.g. "FOR IT & TECH JOBS" */
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

/* Dark "HUD" status bar, like a terminal window (DESIGN.md: HUD surfaces). Used by hud_bar(). */
.hud {
    display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px;
    background: #0b1a11; border: 1px solid #1e3a29; border-radius: 16px;
    padding: 10px 16px; margin-bottom: 16px;
    font: 500 13px 'JetBrains Mono', monospace; color: #94a3b8;
}
.hud .dots { display: flex; gap: 6px; }
.hud .dots span { width: 10px; height: 10px; border-radius: 9999px; }
.hud .path { color: #a7f3d0; }
/* The details shorten with "..." when space is short, so the status stays on the same line. */
.hud .details {
    color: #64748b; flex: 1 1 0; min-width: 0;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.hud .status {
    margin-left: auto; padding: 2px 10px; border-radius: 9999px; white-space: nowrap;
    border: 1px solid #1e3a29; background: rgba(34, 197, 94, 0.08); color: #4ade80;
    box-shadow: 0 0 20px -3px rgba(34, 197, 94, 0.25);
}
.hud .status.partial { color: #fbbf24; background: rgba(251, 191, 36, 0.08); box-shadow: none; }

/* --- Home page --- */

/* Keyword in a headline, in emerald with a soft green underline (DESIGN.md: Headlines) */
.highlight {
    color: #16a34a; text-decoration: underline; text-decoration-color: #86efac;
    text-decoration-thickness: 6px; text-underline-offset: 8px;
}

/* Row of small white chips under the hero, e.g. "⚡ JD skill extraction" */
.chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin: 8px 0 40px; }
.chip {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 9999px; padding: 6px 14px;
    font-size: 14px; color: #0f172a; box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
}

/* Centered small heading above a home page section */
.home-section { text-align: center; margin: 40px 0 16px; }
.home-section h2 { font-size: 28px; font-weight: 800; margin: 8px 0 4px; }
.home-section p { color: #64748b; }

/* "How it works": numbered step cards in a grid that wraps on small screens */
.steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
.step {
    display: flex; gap: 14px; align-items: flex-start; background: #fff;
    border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px 20px;
    box-shadow: 0 1px 3px 0 rgba(15, 23, 42, 0.04);
}
.step .num {
    font: 700 14px 'JetBrains Mono', monospace; color: #16a34a; background: #f0fdf4;
    border: 1px solid #bbf7d0; border-radius: 10px; padding: 6px 10px;
}
.step b { display: block; margin-bottom: 2px; }
.step span { color: #64748b; font-size: 14px; }

/* Feature cards (inside st.container(border=True)) */
.feature-head { display: flex; justify-content: space-between; align-items: center; }
.feature-head .icon { font-size: 28px; }
.feature h4 { font-size: 20px; margin: 8px 0 4px; padding: 0; }
.feature p { color: #64748b; min-height: 48px; }
.badge-live, .badge-soon {
    font: 700 11px 'Plus Jakarta Sans', sans-serif; letter-spacing: 0.06em; text-transform: uppercase;
    border-radius: 9999px; padding: 2px 10px;
}
.badge-live { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.badge-soon { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

/* Dark security section with one card per guard (DESIGN.md: HUD surfaces) */
.guard-section {
    background: #0b1a11; border: 1px solid #1e3a29; border-radius: 24px;
    padding: 32px; margin: 40px 0 16px; color: #f8fafc;
}
.guard-section .home-section { margin-top: 0; }
.guard-section h2 { color: #fff; }
.guard-section .home-section p { color: #94a3b8; }
.guards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }
.guard {
    background: rgba(255, 255, 255, 0.03); border: 1px solid #1e3a29;
    border-radius: 16px; padding: 16px;
}
.guard .label { font: 500 12px 'JetBrains Mono', monospace; color: #4ade80; }
.guard b { display: block; color: #fff; margin: 6px 0 4px; }
.guard span { color: #94a3b8; font-size: 14px; }
.guard .state { display: inline-block; margin-top: 12px; font: 500 12px 'JetBrains Mono', monospace; }
.guard .state.on { color: #4ade80; }
.guard .state.planned { color: #fbbf24; }
</style>
"""


def apply_styles():
    """Load the app's fonts and CSS classes (the CSS above) into the page.

    Called once in app.py, so the styles apply to every page.
    """
    st.markdown(CSS, unsafe_allow_html=True)
