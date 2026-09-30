# Component: one screenshot of a job posting, pasted (Ctrl+V) or uploaded as a file.
# Both ways lead to the same place: st.session_state[key], shown as a preview
# with a "Remove" button. The newest paste or upload replaces the old screenshot.
#
#   key        where the screenshot is kept: st.session_state[key] = {"name", "data"}
#   validate   function(data) -> error message or None (guard 1, runs before any paid call)
#   max_mb     size limit shown to the user and used by the uploader
#
# Returns the screenshot dict, or None if there is none.

import streamlit as st

from components.paste_box import paste_box


def screenshot_input(key, validate, max_mb):
    # The uploader keeps its file until its key changes, so "Remove" gives it a new key.
    st.session_state.setdefault(f"{key}_uploader_id", 0)
    uploader_key = f"{key}_uploader_{st.session_state[f'{key}_uploader_id']}"

    def store(name, data):
        error = validate(data)
        if error:
            st.session_state[f"{key}_error"] = error
        else:
            st.session_state[key] = {"name": name, "data": data}
            st.session_state.pop(f"{key}_error", None)

    def on_upload():
        # Runs before the rerun, when the user picks a new file (or clears it).
        file = st.session_state[uploader_key]
        if file is not None:
            store(file.name, file.getvalue())

    def remove():
        st.session_state.pop(key, None)
        st.session_state.pop(f"{key}_error", None)
        st.session_state[f"{key}_uploader_id"] += 1  # a fresh, empty uploader

    col_paste, col_upload = st.columns(2, gap="medium")
    with col_paste:
        pasted = paste_box(key=f"{key}_paste")
        if pasted:
            store(pasted["name"], pasted["data"])
    with col_upload:
        st.file_uploader(
            "Or upload a file",
            type=["png", "jpg", "jpeg", "webp"],
            max_upload_size=max_mb,
            key=uploader_key,
            on_change=on_upload,
            label_visibility="collapsed",
        )  # the uploader shows the allowed types and max_mb itself

    if f"{key}_error" in st.session_state:
        st.error(st.session_state[f"{key}_error"])

    screenshot = st.session_state.get(key)
    if screenshot:
        size_kb = len(screenshot["data"]) / 1024
        # Name and button above the image, so they stay in view for a long screenshot.
        col_name, col_remove = st.columns([3, 1], vertical_alignment="center")
        col_name.markdown(
            f'<span class="mono">Screenshot: {screenshot["name"]} · {size_kb:.0f} KB</span>',
            unsafe_allow_html=True,
        )
        col_remove.button("Remove", icon=":material/delete:", key=f"{key}_remove", on_click=remove)
        # A fixed width, so a long screenshot of a whole job posting does not fill the page.
        st.image(screenshot["data"], width=420)
    return screenshot
