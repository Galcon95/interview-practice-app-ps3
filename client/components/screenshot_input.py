# Component: the screenshots of one job posting, pasted (Ctrl+V) or uploaded as files.
# A posting can be split over several screenshots, e.g. the title at the top and the
# tasks further down. Every paste or upload adds screenshots to one list in
# st.session_state[key], shown as numbered thumbnails: the order is the reading order.
# Parameters and return value: see the docstring of screenshot_input().

import streamlit as st

from components.paste_box import paste_box


def screenshot_input(key, validate, limits):
    """Draw the screenshot input: a paste box and an uploader, then the screenshots as numbered thumbnails.

    Each paste or upload adds screenshots at the end of the list; the same
    image is never added twice. If the list with the new image fails
    `validate` (e.g. one too many), the image is not added and the error is
    shown instead. Each thumbnail has a remove button, and "Remove all"
    clears the list.

    Args:
        key: where the screenshots are kept: st.session_state[key] = a list of
            {"name", "data"}. Also the start of the names of the widgets inside.
        validate: a function validate(images) that gets the list of image
            bytes and returns an error message or None (guard 1, e.g.
            api_client.validate_screenshots). It runs before an image is
            added, so before any paid call.
        limits: {"max_mb", "max_count", "max_total_mb"}, from
            api_client.get_screenshot_limits(); used by the uploader and shown
            to the user.

    Returns:
        The screenshots as a list of {"name": str, "data": bytes} in reading
        order; empty if there are none.
    """
    st.session_state.setdefault(key, [])
    # The uploader keeps its files until its key changes, so after each upload it gets a
    # new key: it is empty again, and the thumbnails below are the only list to look at.
    st.session_state.setdefault(f"{key}_uploader_id", 0)
    uploader_key = f"{key}_uploader_{st.session_state[f'{key}_uploader_id']}"

    def add(name, data):
        """Add one image at the end of the list, if the list is still valid with it.

        Args:
            name: the file name, e.g. "image.png".
            data: the image as bytes.
        """
        screenshots = st.session_state[key]
        if any(shot["data"] == data for shot in screenshots):
            return  # the same image again (e.g. pasted twice): nothing to add
        error = validate([shot["data"] for shot in screenshots] + [data])
        if error:
            st.session_state[f"{key}_error"] = error
        else:
            st.session_state[key] = screenshots + [{"name": name, "data": data}]
            st.session_state.pop(f"{key}_error", None)

    def on_upload():
        """Add the uploaded files in their order, then empty the uploader (its on_change callback).

        Runs before the page reruns, when the user picks one or more files.
        """
        for file in st.session_state[uploader_key] or []:
            add(file.name, file.getvalue())
        st.session_state[f"{key}_uploader_id"] += 1

    def remove(index):
        """Remove one screenshot; the ones after it move up one place.

        Args:
            index: the position in the list, starting at 0.
        """
        st.session_state[key] = [shot for i, shot in enumerate(st.session_state[key]) if i != index]
        st.session_state.pop(f"{key}_error", None)

    def remove_all():
        """Remove all screenshots and the error message."""
        st.session_state[key] = []
        st.session_state.pop(f"{key}_error", None)

    col_paste, col_upload = st.columns(2, gap="medium")
    with col_paste:
        pasted = paste_box(key=f"{key}_paste")
        if pasted:
            add(pasted["name"], pasted["data"])
    with col_upload:
        st.file_uploader(
            "Or upload files",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            max_upload_size=limits["max_mb"],
            key=uploader_key,
            on_change=on_upload,
            label_visibility="collapsed",
        )  # the uploader shows the allowed types and max_mb itself

    if f"{key}_error" in st.session_state:
        st.error(st.session_state[f"{key}_error"])

    screenshots = st.session_state[key]
    if not screenshots:
        st.caption(
            f"A long posting can be split into up to {limits['max_count']} screenshots, "
            "e.g. the title and the tasks. Add them in reading order."
        )
        return screenshots

    total_mb = sum(len(shot["data"]) for shot in screenshots) / (1024 * 1024)
    col_info, col_clear = st.columns([3, 1], vertical_alignment="center")
    col_info.markdown(
        f'<span class="mono">{len(screenshots)} of {limits["max_count"]} screenshots · '
        f'{total_mb:.1f} of {limits["max_total_mb"]} MB · read in this order</span>',
        unsafe_allow_html=True,
    )
    col_clear.button("Remove all", icon=":material/delete:", key=f"{key}_remove_all", on_click=remove_all)

    # One column per possible screenshot, so the thumbnails keep the same size.
    # The buttons come first, so they stay in one row although the images differ in height.
    columns = st.columns(limits["max_count"])
    for index, (column, shot) in enumerate(zip(columns, screenshots)):
        with column:
            st.button(
                f"Remove {index + 1}",
                icon=":material/close:",
                key=f"{key}_remove_{index}",
                on_click=remove,
                args=(index,),
                width="stretch",
            )
            st.image(shot["data"], caption=f"{index + 1} · {len(shot['data']) / 1024:.0f} KB")
    return screenshots
