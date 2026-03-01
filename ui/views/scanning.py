import streamlit as st
import time
import pandas as pd
import threading
import queue
import os
from streamlit.runtime.scriptrunner import add_script_run_ctx
from ui.components.logger import setup_streamlit_logging
from storage_scan.scanner import DiskScanner
from carving.hybrid import HybridCarver

# Setup streamlit-specific logging for this view
logger = setup_streamlit_logging(__name__)

def scanning_worker(disk_path, clf_path, result_queue, stop_event):
    """
    Background worker that runs the HybridCarver.
    Emits results to the queue.
    """
    try:
        logger.info(f"Starting scan on {disk_path}")
        scanner = DiskScanner(disk_path)
        carver = HybridCarver(checkpoint_path=clf_path)
        
        total_size = scanner.file_size
        block_size = scanner.block_size
        num_blocks = total_size // block_size
        
        for i, (offset, block) in enumerate(scanner.scan_blocks()):
            if stop_event.is_set():
                logger.info("Scan stopped by user.")
                break
                
            identification = carver.identify_fragment(block)
            
            # Only report non-other fragments to the UI to avoid flooding
            if identification["type"] != "other":
                result_queue.put({
                    "type": "fragment",
                    "data": {
                        "Offset": hex(offset),
                        "Type": identification["type"],
                        "Confidence": f"{identification['confidence']:.2f}",
                        "Source": identification["source"],
                        "Size": f"{block_size} B",
                        "data": block,
                        "identification": identification
                    }
                })
            
            # Periodically report progress
            if i % 100 == 0 or i == num_blocks - 1:
                progress = (i + 1) / num_blocks
                result_queue.put({
                    "type": "progress",
                    "data": {
                        "value": progress,
                        "text": f"Scanning sector {i}/{num_blocks} ({int(progress*100)}%)"
                    }
                })
        
        result_queue.put({"type": "done", "data": None})
        scanner.close()
        
    except Exception as e:
        logger.error(f"Error in scanning worker: {str(e)}")
        result_queue.put({"type": "error", "data": str(e)})

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

    # Initialize session state for scanning if not present
    if "scanning_active" not in st.session_state:
        st.session_state.scanning_active = False
    if "scan_progress" not in st.session_state:
        st.session_state.scan_progress = 0.0
    if "scan_status_text" not in st.session_state:
        st.session_state.scan_status_text = "Ready"

    # Layout for controls
    col1, col2 = st.columns([1, 4])
    with col1:
        start_disabled = st.session_state.scanning_active or not st.session_state.disk_image_path
        if st.button("Start Scan", type="primary", use_container_width=True, disabled=start_disabled):
            st.session_state.scanning_active = True
            st.session_state.carved_fragments = []
            st.session_state.scan_progress = 0.0
            st.session_state.scan_status_text = "Initializing..."
            
            # Setup background thread
            result_queue = queue.Queue()
            stop_event = threading.Event()
            st.session_state.scan_queue = result_queue
            st.session_state.scan_stop_event = stop_event
            
            # Get paths from session state
            disk_path = st.session_state.disk_image_path
            clf_path = st.session_state.clf_checkpoint or "models/checkpoints/classifier_best.pth"
            
            thread = threading.Thread(
                target=scanning_worker,
                args=(disk_path, clf_path, result_queue, stop_event)
            )
            add_script_run_ctx(thread)
            thread.start()
            st.rerun()
        
        if st.button("Stop Scan", type="secondary", use_container_width=True, disabled=not st.session_state.scanning_active):
            if "scan_stop_event" in st.session_state:
                st.session_state.scan_stop_event.set()
            st.session_state.scanning_active = False
            st.rerun()

    # Progress section
    st.subheader("Progress")
    progress_bar = st.progress(st.session_state.scan_progress, text=st.session_state.scan_status_text)
    
    # Main layout for logs and fragments
    tab1, tab2 = st.tabs(["Fragments Found", "Live Log Feed"])

    with tab1:
        st.subheader("Identified Fragments")
        fragment_placeholder = st.empty()
        if st.session_state.carved_fragments:
            df = pd.DataFrame(st.session_state.carved_fragments)
            if "data" in df.columns:
                df = df.drop(columns=["data"])
            if "identification" in df.columns:
                df = df.drop(columns=["identification"])
            fragment_placeholder.dataframe(df, use_container_width=True)
        else:
            fragment_placeholder.info("No fragments found yet.")

    with tab2:
        st.subheader("Activity Logs")
        log_placeholder = st.empty()
        with log_placeholder.container(height=400):
            for log in reversed(st.session_state.logs):
                st.text(log)

    # Handle queue polling if scanning is active
    if st.session_state.scanning_active:
        if "scan_queue" in st.session_state:
            q = st.session_state.scan_queue
            processed_any = False
            
            # Poll all available messages
            try:
                while True:
                    msg = q.get_nowait()
                    processed_any = True
                    
                    if msg["type"] == "fragment":
                        st.session_state.carved_fragments.append(msg["data"])
                    elif msg["type"] == "progress":
                        st.session_state.scan_progress = msg["data"]["value"]
                        st.session_state.scan_status_text = msg["data"]["text"]
                    elif msg["type"] == "done":
                        st.session_state.scanning_active = False
                        st.success("Scan completed!")
                        break
                    elif msg["type"] == "error":
                        st.session_state.scanning_active = False
                        st.error(f"Scan failed: {msg['data']}")
                        break
            except queue.Empty:
                pass
            
            if processed_any:
                # Update the display immediately
                with tab1:
                    if st.session_state.carved_fragments:
                        df = pd.DataFrame(st.session_state.carved_fragments)
                        fragment_placeholder.dataframe(df, use_container_width=True)
                
                with tab2:
                    with log_placeholder.container(height=400):
                        for log in reversed(st.session_state.logs):
                            st.text(log)
                
                progress_bar.progress(st.session_state.scan_progress, text=st.session_state.scan_status_text)
                
                # If still active, schedule a rerun to keep polling
                if st.session_state.scanning_active:
                    time.sleep(0.1)
                    st.rerun()
            else:
                # No new messages, but scan still active. Wait a bit then rerun.
                time.sleep(0.5)
                st.rerun()

# Execute the page
if __name__ == "__main__":
    render_scanning_page()
