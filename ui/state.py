import streamlit as st

def init_session_state():
    """Initializes all necessary session state keys for the application."""
    if "disk_image_path" not in st.session_state:
        st.session_state.disk_image_path = ""
    if "clf_checkpoint" not in st.session_state:
        st.session_state.clf_checkpoint = None
    if "ae_checkpoint" not in st.session_state:
        st.session_state.ae_checkpoint = None
    if "recovery_session" not in st.session_state:
        st.session_state.recovery_session = False
    if "carved_fragments" not in st.session_state:
        st.session_state.carved_fragments = []
    if "reconstructed_files" not in st.session_state:
        st.session_state.reconstructed_files = []
    if "logs" not in st.session_state:
        st.session_state.logs = []
    if "scanning_active" not in st.session_state:
        st.session_state.scanning_active = False
