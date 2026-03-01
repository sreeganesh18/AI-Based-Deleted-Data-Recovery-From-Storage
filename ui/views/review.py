import streamlit as st
import pandas as pd
import io
import os
from PIL import Image
import numpy as np
from streamlit_image_comparison import image_comparison

from reconstruction.grouping import FragmentGrouper
from reconstruction.denoise import DenoisingPipeline
from reconstruction.repair import repair_jpeg, repair_pdf
from reconstruction.enhancement import apply_super_resolution, denoise_image
from ui.components.hex_viewer import render_hex_viewer
from models.classifier import FragmentClassifier
from models.autoencoder import FragmentAutoencoder

def run_reassembly():
    """Runs the full reassembly pipeline on carved fragments."""
    if not st.session_state.carved_fragments:
        st.warning("No fragments available for reassembly. Please run a scan first.")
        return

    with st.status("Reassembling files...", expanded=True) as status:
        st.write("Initializing models...")
        # Load classifier for sequence scoring if available
        classifier = None
        if st.session_state.clf_checkpoint:
            try:
                classifier = FragmentClassifier()
                import torch
                checkpoint = torch.load(st.session_state.clf_checkpoint, map_location="cpu", weights_only=False)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    classifier.load_state_dict(checkpoint['model_state_dict'])
                else:
                    classifier.load_state_dict(checkpoint)
                classifier.eval()
            except Exception as e:
                st.error(f"Failed to load classifier: {e}")

        st.write("Grouping fragments...")
        grouper = FragmentGrouper(classifier=classifier)
        # The fragments in session state need to have 'offset' and 'data'
        # Scanning page should ensure this.
        reconstructed = grouper.group_fragments(st.session_state.carved_fragments)
        
        st.write(f"Found {len(reconstructed)} potential files. Refining...")
        
        final_files = []
        for i, file_info in enumerate(reconstructed):
            file_data = file_info['data']
            file_type = file_info['type']
            
            # Repair
            if file_type == 'jpeg':
                repaired_data = repair_jpeg(file_data)
            elif file_type == 'pdf':
                repaired_data = repair_pdf(file_data)
            else:
                repaired_data = file_data
                
            # Denoise/Enhance (Best effort for preview)
            # We store the original (repaired) and a "processed" version for comparison
            processed_data = repaired_data
            if file_type == 'jpeg':
                try:
                    # Convert to CV2/PIL for enhancement
                    nparr = np.frombuffer(repaired_data, np.uint8)
                    img = Image.open(io.BytesIO(repaired_data))
                    img_cv = np.array(img.convert('RGB'))
                    
                    # Apply enhancement
                    enhanced_cv = apply_super_resolution(img_cv)
                    enhanced_cv = denoise_image(enhanced_cv)
                    
                    # Convert back to bytes for storage
                    enhanced_img = Image.fromarray(enhanced_cv)
                    buf = io.BytesIO()
                    enhanced_img.save(buf, format="JPEG")
                    processed_data = buf.getvalue()
                except Exception as e:
                    st.write(f"Enhancement failed for file {i}: {e}")

            final_files.append({
                'id': file_info['id'],
                'type': file_type,
                'original_data': repaired_data,
                'processed_data': processed_data,
                'fragment_offsets': file_info['fragment_offsets'],
                'completed': file_info['completed'],
                'size': len(repaired_data)
            })
            
        st.session_state.reconstructed_files = final_files
        status.update(label="Reassembly complete!", state="complete", expanded=False)

def show_review_page():
    st.title("🔍 Review & Reassemble")
    
    if not st.session_state.recovery_session:
        st.info("Please initialize a recovery session in the Configuration page first.")
        return

    if not st.session_state.carved_fragments:
        st.warning("No fragments found yet. Go to the Scanning & Carving page to start.")
        return

    # Sidebar for file list
    with st.sidebar:
        st.subheader("Recovered Files")
        if st.button("🔄 Run/Refresh Reassembly", use_container_width=True):
            run_reassembly()
            
        if not st.session_state.reconstructed_files:
            st.write("No files reassembled yet.")
            selected_file_index = None
        else:
            file_labels = [f"File {f['id']} ({f['type'].upper()}, {f['size']/1024:.1f} KB)" 
                           for f in st.session_state.reconstructed_files]
            selected_file_label = st.radio("Select a file to review:", file_labels)
            selected_file_index = file_labels.index(selected_file_label)

    # Main content area
    if selected_file_index is not None:
        file_info = st.session_state.reconstructed_files[selected_file_index]
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader(f"File {file_info['id']} Details")
        with col2:
            st.markdown(f"**Type:** `{file_info['type'].upper()}`")
            st.markdown(f"**Status:** {'✅ Complete' if file_info['completed'] else '⚠️ Incomplete'}")

        tabs = st.tabs(["🖼️ Quality Comparison", "📋 Metadata", "🧩 Fragment Sequence", "🔢 Raw Data (Hex)"])
        
        with tabs[0]:
            if file_info['type'] == 'jpeg':
                try:
                    img_orig = Image.open(io.BytesIO(file_info['original_data']))
                    img_proc = Image.open(io.BytesIO(file_info['processed_data']))
                    
                    st.write("Compare Original Reassembly (Left) with AI Enhanced (Right):")
                    image_comparison(
                        img1=img_orig,
                        img2=img_proc,
                        label1="Original",
                        label2="Enhanced"
                    )
                except Exception as e:
                    st.error(f"Could not render image preview: {e}")
            else:
                st.info(f"Visual comparison not available for {file_info['type']} files.")
                st.write("Original Size:", file_info['size'], "bytes")

        with tabs[1]:
            st.write("### File Metadata")
            metadata = {
                "File ID": file_info['id'],
                "Type": file_info['type'],
                "Size (Bytes)": file_info['size'],
                "Fragment Count": len(file_info['fragment_offsets']),
                "Reassembly": "Sequential + AI Scoring",
                "Status": "Complete (Footer found)" if file_info['completed'] else "Partial (End of radius reached)"
            }
            st.table(pd.DataFrame(metadata.items(), columns=["Property", "Value"]))

        with tabs[2]:
            st.write("### Fragment Sequence")
            df_frags = pd.DataFrame({
                "Sequence": range(1, len(file_info['fragment_offsets']) + 1),
                "Disk Offset": file_info['fragment_offsets']
            })
            st.dataframe(df_frags, use_container_width=True)

        with tabs[3]:
            st.write("### Hex Inspection")
            # Show first 4KB for performance, or full if small
            preview_data = file_info['original_data'][:4096]
            if len(file_info['original_data']) > 4096:
                st.caption("Showing first 4096 bytes...")
            render_hex_viewer(preview_data)

    else:
        st.info("Select a file from the sidebar to review its details.")
        
        # Summary of orphan fragments
        if st.session_state.carved_fragments:
            total_frags = len(st.session_state.carved_fragments)
            used_offsets = set()
            for f in st.session_state.reconstructed_files:
                used_offsets.update(f['fragment_offsets'])
            
            orphan_count = total_frags - len(used_offsets)
            st.metric("Total Fragments Found", total_frags)
            st.metric("Fragments Reassembled", len(used_offsets))
            st.metric("Orphan Fragments", orphan_count)
            
            if orphan_count > 0:
                st.write("### Orphan Fragments")
                st.caption("These fragments were not attached to any reassembled file.")
                orphans = [f for f in st.session_state.carved_fragments if f['offset'] not in used_offsets]
                df_orphans = pd.DataFrame([
                    {"Offset": o['offset'], "Type": o['identification'].get('type', 'other'), "Confidence": o['identification'].get('confidence', 0.0)}
                    for o in orphans
                ])
                st.dataframe(df_orphans, use_container_width=True)

if __name__ == "__main__":
    show_review_page()
else:
    show_review_page()
