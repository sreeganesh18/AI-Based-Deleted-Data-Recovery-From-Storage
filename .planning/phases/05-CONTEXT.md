# PHASE 5 CONTEXT: User Interface & Integration

## Decisions

### 1. UI Layout & Navigation
- **Structure:** The application will be implemented as a **Multi-page Streamlit App** to cleanly separate different stages of the recovery process.
- **Configuration:** Primary controls (Disk Image selection, Model Checkpoints loading) will be located in the **Main View** of the configuration page rather than the sidebar.
- **Feedback Loop:**
    - Scanning and carving results will be updated in **Real-time** as fragments are identified.
    - A **Live Log Feed** will be provided to show the detailed execution status of the backend modules.

### 2. Forensic Visualization
- **Mapping:** Identified fragments will be presented in a **List/Grid format** for clarity and searchability.
- **Reassembly Tracking:** Fragments within a reconstructed file will be shown as a **Sequential List**, providing a clear audit trail of the reassembly order.
- **Confidence Representation:** AI confidence scores for fragment classification will be displayed using **Numerical Labels** (e.g., "94.5%").
- **Progress Tracking:** The UI will focus on **Macro-level (File-level) progress**, showing the overall status of the recovery session rather than per-block scanning details.

### 3. Review Interaction
- **Quality Comparison:** The application will use an **Interactive Image Slider** to allow users to visually compare the Original, Denoised, and Enhanced versions of recovered files.
- **File Metadata:** Clicking a recovered file will show **Detailed Metadata**, including fragmentation count, disk offsets, MD5 hashes, and reassembly strategy.
- **Technical Inspection:** A **Hex-viewer component** will be integrated to allow the raw inspection of fragments.
- **Orphan Management:** Fragments that cannot be linked to a header will be managed in a **Dedicated Orphan Tab** for manual review and potential linking.

### 4. Export Workflow
- **Selection:** Users must perform **Manual Selection** of files they wish to recover and export.
- **Conflict Management:** File naming collisions at the destination will be handled via **Auto-Suffixing** (e.g., `file_1.recovered`, `file_2.recovered`).
- **Reporting:** The export process will focus on the **Files Only**, without generating additional forensic summary reports for this phase.
- **Storage Structure:** All exported files will be saved into a **Flat Folder** at the chosen destination.

## Deferred Ideas
- (None at this time)
