# Component: a box where the user pastes an image from the clipboard
# (click the box, then Ctrl+V, or right-click -> Paste).
# Streamlit has no paste widget, so this is a small custom component
# (st.components.v2): a bit of HTML + JavaScript that runs in the browser.
#
# Returns {"name": ..., "data": bytes} in the run right after a paste, otherwise None.

import base64

import streamlit as st

HTML = """
<div id="paste-box" contenteditable="true" spellcheck="false">
    <div class="icon">📋</div>
    <div class="title">Click here, then press Ctrl+V</div>
    <div id="hint">Take a screenshot with Win+Shift+S, then paste it here.</div>
</div>
"""

CSS = """
#paste-box {
    border: 2px dashed var(--st-border-color);
    border-radius: 12px;
    padding: 24px 16px;
    text-align: center;
    color: var(--st-text-color);
    background: var(--st-secondary-background-color);
    cursor: pointer;
    caret-color: transparent;  /* no blinking cursor, the box is not for typing */
    outline: none;
}
#paste-box:focus { border-color: var(--st-primary-color); }
.icon { font-size: 28px; }
.title { font-weight: 600; margin: 4px 0; }
#hint { font-size: 14px; opacity: 0.7; }
"""

# Runs in the browser. setTriggerValue sends one event to Python and starts a rerun.
JS = """
export default function (component) {
    const { parentElement, setTriggerValue } = component
    const box = parentElement.querySelector("#paste-box")
    const hint = parentElement.querySelector("#hint")
    if (!box) return

    // The box is "contenteditable" so the browser allows pasting into it,
    // but typing, dropping or deleting must not change it.
    const blockEditing = (event) => event.preventDefault()

    const onPaste = (event) => {
        event.preventDefault()
        const items = Array.from(event.clipboardData?.items ?? [])
        const item = items.find((i) => i.type.startsWith("image/"))
        if (!item) {
            hint.textContent = "No image in the clipboard. Copy a screenshot first."
            return
        }
        const file = item.getAsFile()
        const reader = new FileReader()
        reader.onload = () => {
            hint.textContent = "Screenshot pasted."
            // reader.result is a data URL: "data:image/png;base64,iVBORw0..."
            setTriggerValue("pasted", { name: file.name || "pasted-screenshot.png", data_url: reader.result })
        }
        reader.readAsDataURL(file)
    }

    box.addEventListener("paste", onPaste)
    box.addEventListener("beforeinput", blockEditing)
    box.addEventListener("drop", blockEditing)
    return () => {  // cleanup when Streamlit removes the component
        box.removeEventListener("paste", onPaste)
        box.removeEventListener("beforeinput", blockEditing)
        box.removeEventListener("drop", blockEditing)
    }
}
"""

# Registered once, when the module is first imported.
_paste_box = st.components.v2.component("paste_box", html=HTML, css=CSS, js=JS)


def paste_box(key):
    """Draw the paste box and return the image the user just pasted, if any.

    The paste is a one-time event: the image is returned only in the run right
    after the paste, so the caller must store it (screenshot_input does).

    Args:
        key: a unique name for this paste box on the page.

    Returns:
        {"name": str, "data": bytes} in the run right after a paste, otherwise None.
    """
    result = _paste_box(key=key, on_pasted_change=lambda: None)
    if not result.pasted:
        return None
    # "data:image/png;base64,AAAA" -> the part after the comma, decoded to bytes
    data = base64.b64decode(result.pasted["data_url"].split(",", 1)[1])
    return {"name": result.pasted["name"], "data": data}
