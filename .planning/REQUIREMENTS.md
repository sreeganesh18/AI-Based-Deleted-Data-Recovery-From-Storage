# REQUIREMENTS: AI Deleted Data Recovery

## Functional Requirements
1.  **Storage Scanning:**
    - Scan physical storage devices or raw disk images (NTFS, FAT32).
    - Identify and extract file fragments.
2.  **File Carving:**
    - Use AI-based Classifiers to identify file types from fragments.
    - Specifically support JPEG and PDF.
3.  **Data Denoising:**
    - Use Autoencoder models to repair corrupted fragments.
    - Support fragment reconstruction for damaged storage scenarios.
4.  **Reconstruction:**
    - Reassemble fragments into functional files.
    - Enhance recovered data for visual or document integrity.
5.  **User Interface:**
    - Streamlit-based GUI for scanning, viewing fragments, and initiating recovery.
    - Progress visualization for scanning and reconstruction.
6.  **Dataset Management:**
    - Manage fragments, original data, and reconstructed files.

## Non-Functional Requirements
1.  **Performance:** Efficiently handle large disk images.
2.  **Accuracy:** High precision in identifying file fragments and reconstructing data.
3.  **Extensibility:** Easy addition of new file types and model architectures.
4.  **Reliability:** Robust handling of heavily corrupted storage environments.
5.  **Maintainability:** Clean, modular code structure following Python best practices.

## Scope
- Initially focus on JPEG and PDF file formats.
- Support NTFS and FAT32 file systems.
- Deep Learning based approach for both carving and denoising.
