import streamlit as st
import os
import time

def handle_collision(directory, filename):
    """Handles filename collisions by adding a numeric suffix."""
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    return new_filename

def show_export_page():
    st.title("💾 Export Results")

    if not st.session_state.reconstructed_files:
        st.info("No files available for export. Please run reassembly in the Review page first.")
        return

    st.write("### Select Files to Export")
    
    # Create a list of options for the multiselect
    file_options = [
        f"File {f['id']} ({f['type'].upper()}, {f['size']/1024:.1f} KB)"
        for f in st.session_state.reconstructed_files
    ]
    
    selected_options = st.multiselect(
        "Choose files to save:",
        options=file_options,
        default=file_options # Select all by default
    )

    if not selected_options:
        st.warning("Please select at least one file to export.")
        return

    st.write("---")
    st.write("### Export Destination")
    
    export_dir = st.text_input("Destination Directory:", value=os.path.join(os.getcwd(), "recovered_data"))
    
    if st.button("🚀 Export Selected Files", use_container_width=True):
        if not export_dir:
            st.error("Please specify a destination directory.")
            return
            
        try:
            os.makedirs(export_dir, exist_ok=True)
        except Exception as e:
            st.error(f"Could not create directory: {e}")
            return

        # Map labels back to indices
        indices = [file_options.index(opt) for opt in selected_options]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        success_count = 0
        for i, idx in enumerate(indices):
            file_info = st.session_state.reconstructed_files[idx]
            
            # Construct filename
            ext = f".{file_info['type']}" if file_info['type'] != 'other' else ".bin"
            base_filename = f"recovered_file_{file_info['id']}{ext}"
            
            # Handle collision
            final_filename = handle_collision(export_dir, base_filename)
            final_path = os.path.join(export_dir, final_filename)
            
            try:
                # Save both versions if they differ? 
                # For simplicity, we save the processed (enhanced) one if it's different/better
                # or maybe provide a checkbox to save both.
                # Standard requirement usually implies saving the "best" version.
                with open(final_path, "wb") as f:
                    f.write(file_info['processed_data'])
                
                success_count += 1
                status_text.text(f"Saved {final_filename}...")
            except Exception as e:
                st.error(f"Failed to save {final_filename}: {e}")
            
            progress_bar.progress((i + 1) / len(indices))
            time.sleep(0.05) # Small delay for visual feedback

        status_text.success(f"Successfully exported {success_count} files to `{export_dir}`")
        st.balloons()

if __name__ == "__main__":
    show_export_page()
else:
    show_export_page()
