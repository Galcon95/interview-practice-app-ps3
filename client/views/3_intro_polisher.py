# Page — Feature 4: Self-introduction polisher.
# The user writes a short "tell me about yourself" answer and gets an
# improved version back.

# TODO: text area -> api_client.polish_introduction -> show before / after

import streamlit as st

from components.section_header import section_header

section_header(
    "Self-Introduction Polisher",
    'Turn your "tell me about yourself" into a clear, confident pitch for the interview.',
)
st.info("This tool is coming soon. Meanwhile, try the **JD Analyzer** or **Role Q&A**.", icon=":material/schedule:")
