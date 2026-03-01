# ROADMAP: AI Deleted Data Recovery

## Phase 1: Foundation & Data Management
**Requirements:** [ENV-01, DATA-01, SCAN-01, SCAN-02, CARVE-01, CARVE-02]
- [x] Initialize project environment (uv, dependencies). [ENV-01]
- [x] Implement dataset management for fragments, original data, and reconstructed files. [DATA-01]
- [x] Develop basic storage scanner for raw disk image reading. [SCAN-01, SCAN-02]
- [x] Implement file carving base for NTFS and FAT32. [CARVE-01, CARVE-02]

## Phase 2: Core AI Models
**Requirements:** [CLF-01, AE-01, TRAIN-01, DATA-02]
- [x] Implement Classifier model architecture for file type identification. [CLF-01]
- [x] Implement Autoencoder model architecture for data denoising. [AE-01]
- [x] Develop training scripts for both Classifier and Autoencoder models. [TRAIN-01]
- [x] Collect and preprocess training data (JPEG, PDF fragments). [DATA-02]

## Phase 3: File Carving & Denoising
**Requirements:** [PH3-01, PH3-02, PH3-03, PH3-04, PH3-05, PH3-06]
- [x] Update training scripts with 80/20 splits and PSNR/SSIM metrics. [PH3-01]
- [x] Train and evaluate both models (targets: 90% JPEG, 85% PDF). [PH3-02, PH3-03]
- [x] Implement HybridCarver (Signatures + Classifier). [PH3-04]
- [x] Implement Denoising Pipeline (Autoencoder integration). [PH3-05]
- [x] Comprehensive logging, reporting, and validation of the integrated pipeline. [PH3-06]

## Phase 4: Reconstruction & Enhancement
**Requirements:** [RECON-01, RECON-02, RECON-03, ENHANCE-01, VAL-01, REPORT-01]
- [x] Re-implement FragmentGrouper with sequential offsets and AI sequence scoring (mixed approach) within a 1MB search radius. [RECON-01]
- [x] Implement parallel reconstruction logic for overlapping headers and gap handling (fill with zeros). [RECON-02]
- [x] Implement structural repair for JPEG (header synthesis) and PDF (xref repair using PyMuPDF/Ghostscript). [RECON-03]
- [x] Implement advanced AI enhancement (Super-resolution) to replace basic interpolation. [ENHANCE-01]
- [x] Implement 90% recovery success validation and integrated flow testing on fragmented dummy images. [VAL-01]
- [x] Comprehensive reporting including visual "before vs. after" comparison for enhanced files. [REPORT-01]

## Phase 5: User Interface & Integration
**Requirements:** [UI-01, UI-02, UI-03, UI-04]
**Goal:** Build a functional multi-page Streamlit dashboard for end-to-end data recovery.
**Plans:** 3 plans
- [x] 05-01-PLAN.md — Application setup and configuration page.
- [x] 05-02-PLAN.md — Real-time scanning and carving integration.
- [x] 05-03-PLAN.md — File review, interactive comparison, and export logic.

## Phase 6: Testing & Validation
**Requirements:** [TEST-01, TEST-02, TEST-03, DOC-01, DOC-02, VAL-01]
**Goal:** Finalize and validate the system with comprehensive testing and documentation.
- [x] 06-01-PLAN.md — Core logic and integration testing. [TEST-01, TEST-02]
- [x] 06-02-PLAN.md — Performance, documentation, and finalization. [TEST-03, DOC-01, DOC-02, VAL-01]
