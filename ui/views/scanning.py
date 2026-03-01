import streamlit as st
import time
import pandas as pd
from ui.components.logger import setup_streamlit_logging

# Setup streamlit-specific logging for this view
logger = setup_streamlit_logging(__name__)

def render_scanning_page():
    st.title("Disk Scanning & Data Carving")
    st.markdown("""
        Scan the selected disk image to identify and extract file fragments using signature-based and AI-powered carving.
    """)

    if not st.session_state.get("recovery_session"):
        st.warning("⚠️ Please configure the recovery session first.")
        if st.button("Go to Configuration"):
            st.switch_page("views/config.py")
        return

    # Layout for controls
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Start Scan", type="primary", use_container_width=True):
            st.session_state.scanning_active = True
            st.rerun()
        
        if st.button("Stop Scan", type="secondary", use_container_width=True, disabled=not st.session_state.get("scanning_active", False)):
            st.session_state.scanning_active = False
            st.rerun()

    # Progress section
    st.subheader("Progress")
    progress_bar = st.progress(0, text="Ready to scan")
    
    status_container = st.container()
    with status_container:
        with st.status("Scanning status", expanded=True) as status:
            st.write("Idle...")
            # This will be updated dynamically during scan

    # Main layout for logs and fragments
    tab1, tab2 = st.tabs(["Fragments Found", "Live Log Feed"])

    with tab1:
        st.subheader("Identified Fragments")
        if st.session_state.carved_fragments:
            df = pd.DataFrame(st.session_state.carved_fragments)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No fragments found yet.")

    with tab2:
        st.subheader("Activity Logs")
        # Display logs in a scrollable area
        log_container = st.empty()
        with log_container.container(height=400):
            for log in reversed(st.session_state.logs):
                st.text(log)

# Execute the page
if __name__ == "__main__":
    render_scanning_page()
