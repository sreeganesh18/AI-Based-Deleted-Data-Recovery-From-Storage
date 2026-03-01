import streamlit as st
import os
import glob
from ui.components.hex_viewer import render_hex_viewer
from ui.components.logger import setup_streamlit_logging

# Setup logger for this page
logger = setup_streamlit_logging(__name__)

def get_checkpoints():
    """Returns a list of full paths to .pth files in models/checkpoints/."""
    checkpoint_dir = "models/checkpoints"
    if not os.path.exists(checkpoint_dir):
        return []
    return sorted(glob.glob(os.path.join(checkpoint_dir, "*.pth")))

def validate_path(path):
    """Checks if a path exists and is a file."""
    if not path:
        return False, "Path is empty."
    if not os.path.exists(path):
        return False, f"Path does not exist: {path}"
    if not os.path.isfile(path):
        return False, f"Path is not a file: {path}"
    return True, "Path is valid."

st.title("⚙️ Recovery Setup")

st.markdown("""
Configure the parameters for the data recovery session. 
Specify the source disk image and select the AI model checkpoints to use.
""")

# Load checkpoints
checkpoint_paths = get_checkpoints()
checkpoint_names = [os.path.basename(p) for p in checkpoint_paths]

with st.form("config_form"):
    st.subheader("Source & Models")
    
    # Disk Image Path
    disk_image_path = st.text_input(
        "Disk Image Path", 
        value=st.session_state.disk_image_path if st.session_state.disk_image_path else "",
        help="Absolute path to the raw disk image (e.g., /path/to/image.dd)"
    )
    
    if not checkpoint_paths:
        st.warning("No model checkpoints found in `models/checkpoints/`. Please ensure models are trained and saved.")
        clf_options = ["None found"]
        ae_options = ["None found"]
        clf_idx = 0
        ae_idx = 0
    else:
        clf_options = checkpoint_names
        ae_options = checkpoint_names
        
        # Try to find the index of currently selected checkpoint
        try:
            current_clf = os.path.basename(st.session_state.clf_checkpoint) if st.session_state.clf_checkpoint else None
            clf_idx = clf_options.index(current_clf) if current_clf in clf_options else 0
        except:
            clf_idx = 0
            
        try:
            current_ae = os.path.basename(st.session_state.ae_checkpoint) if st.session_state.ae_checkpoint else None
            ae_idx = ae_options.index(current_ae) if current_ae in ae_options else 0
        except:
            ae_idx = 0

    col1, col2 = st.columns(2)
    with col1:
        selected_clf_name = st.selectbox(
            "Classifier Checkpoint", 
            options=clf_options,
            index=clf_idx,
            help="Select the trained classifier model (.pth)"
        )
    with col2:
        selected_ae_name = st.selectbox(
            "Autoencoder Checkpoint", 
            options=ae_options,
            index=ae_idx,
            help="Select the trained autoencoder model (.pth)"
        )
    
    submit_button = st.form_submit_button("Initialize Session")

if submit_button:
    valid, msg = validate_path(disk_image_path)
    if not valid:
        st.error(msg)
    else:
        # Update session state with FULL paths
        st.session_state.disk_image_path = disk_image_path
        
        if selected_clf_name != "None found":
            idx = checkpoint_names.index(selected_clf_name)
            st.session_state.clf_checkpoint = checkpoint_paths[idx]
        else:
            st.session_state.clf_checkpoint = None
            
        if selected_ae_name != "None found":
            idx = checkpoint_names.index(selected_ae_name)
            st.session_state.ae_checkpoint = checkpoint_paths[idx]
        else:
            st.session_state.ae_checkpoint = None
            
        st.session_state.recovery_session = True
        
        st.success("Session initialized successfully!")
        logger.info(f"Session initialized with disk image: {disk_image_path}")
        logger.info(f"Classifier: {st.session_state.clf_checkpoint}, Autoencoder: {st.session_state.ae_checkpoint}")

# Data Preview
if st.session_state.disk_image_path:
    st.divider()
    st.subheader("Data Preview")
    
    valid, msg = validate_path(st.session_state.disk_image_path)
    if valid:
        try:
            with open(st.session_state.disk_image_path, "rb") as f:
                preview_data = f.read(512)
            
            st.info(f"Successfully accessed: {os.path.basename(st.session_state.disk_image_path)}")
            render_hex_viewer(preview_data)
            
        except Exception as e:
            st.error(f"Error reading disk image: {str(e)}")
            logger.error(f"Failed to read disk image for preview: {str(e)}")
    else:
        st.warning("Enter a valid disk image path to preview data.")
else:
    st.info("💡 Pro-tip: Once you enter a valid disk image path and initialize the session, a hex preview of the first sector will appear here.")
