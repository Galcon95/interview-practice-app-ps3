# Component: a dark "HUD" status bar in the style of a terminal window
# (DESIGN.md: "dark HUD containers for tactical readouts"), e.g.
#   ● ● ●  intervai // jd-analysis // qa-engineer   model: gpt-5-mini   [● Guards 3/4 active]
# The CSS classes (.hud ...) are in components/styles.py.

import html
import re

import streamlit as st


def hud_bar(path, details, guards):
    """Draw the dark status bar: window dots, a path, some details and the guard status.

    All texts are HTML-escaped, because some of them come from user content
    (e.g. a job title read from a screenshot) and the bar is drawn as HTML.

    Args:
        path: the parts of the path, joined with " // ", e.g.
            ["intervai", "jd-analysis", "QA Engineer"]. Parts after the first two
            are shown as a slug ("qa-engineer").
        details: short facts shown in muted text, e.g. ["source: 2 screenshots",
            "model: gpt-5-mini"].
        guards: the guard status from api_client.get_guard_status(),
            {name: active}. Shown as "Guards 3/4 active", green if all are
            active, amber otherwise; hovering shows the list.
    """
    parts = [path[0], *path[1:2], *(slug(part) for part in path[2:])]
    active = sum(guards.values())
    status_class = "status" if active == len(guards) else "status partial"
    tooltip = " · ".join(f"{name}: {'on' if on else 'not built yet'}" for name, on in guards.items())
    st.markdown(
        f"""
        <div class="hud">
            <div class="dots">
                <span style="background:#ef4444"></span>
                <span style="background:#f59e0b"></span>
                <span style="background:#22c55e"></span>
            </div>
            <span class="path">{html.escape(" // ".join(parts))}</span>
            <span class="details">{html.escape("  ·  ".join(details))}</span>
            <span class="{status_class}" title="{html.escape(tooltip)}">● Guards {active}/{len(guards)} active</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def slug(text):
    """Turn a text into a short, lowercase, dash-separated name, e.g. "QA Engineer (m/f/d)" -> "qa-engineer-m-f-d".

    Args:
        text: any text, e.g. a job title.

    Returns:
        The slug (str), at most 40 characters; "unknown" if nothing is left.
    """
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40].strip("-") or "unknown"
