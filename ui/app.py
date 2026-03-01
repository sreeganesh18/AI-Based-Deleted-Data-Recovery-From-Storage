import streamlit as st
from ui.state import init_session_state

st.set_page_config(
    page_title="AI Data Recovery",
    page_icon="🔍",
    layout="wide",
)

# Initialize session state
init_session_state()

# Define pages for navigation
pg = st.navigation([
    st.Page("views/config.py", title="Configuration", icon="⚙️"),
    st.Page("views/scanning.py", title="Scanning & Carving", icon="🔦"),
    st.Page("views/review.py", title="Review & Reassemble", icon="🖼️"),
    st.Page("views/export.py", title="Export Results", icon="💾"),
])

# Execute current page
pg.run()
