# ROADMAP: AI Deleted Data Recovery

## Phase 1: Foundation & Data Management
**Requirements:** [ENV-01, DATA-01, SCAN-01, SCAN-02, CARVE-01, CARVE-02]
- [ ] Initialize project environment (uv, dependencies). [ENV-01]
- [ ] Implement dataset management for fragments, original data, and reconstructed files. [DATA-01]
- [ ] Develop basic storage scanner for raw disk image reading. [SCAN-01, SCAN-02]
- [ ] Implement file carving base for NTFS and FAT32. [CARVE-01, CARVE-02]

## Phase 2: Core AI Models
**Requirements:** [CLF-01, AE-01, TRAIN-01, DATA-02]
- [ ] Implement Classifier model architecture for file type identification. [CLF-01]
- [ ] Implement Autoencoder model architecture for data denoising. [AE-01]
- [ ] Develop training scripts for both Classifier and Autoencoder models. [TRAIN-01]
- [ ] Collect and preprocess training data (JPEG, PDF fragments). [DATA-02]

## Phase 3: File Carving & Denoising
- [ ] Train and evaluate the Classifier for fragment-level file identification.
- [ ] Train and evaluate the Autoencoder for fragment denoising and repair.
- [ ] Integrate Classifier into the carving process.
- [ ] Integrate Autoencoder into the reconstruction process.

## Phase 4: Reconstruction & Enhancement
- [ ] Develop grouping logic for reassembling file fragments.
- [ ] Implement enhancement techniques for recovered data (visual/integrity).
- [ ] Validate reconstructed files (checksum, file header integrity).
- [ ] Handle complex fragmentation (non-contiguous files).

## Phase 5: User Interface & Integration
- [ ] Build basic Streamlit UI for storage scanning.
- [ ] Implement UI components for fragment visualization and reconstruction progress.
- [ ] Integrate backend modules (scanner, models, reconstruction) into the UI.
- [ ] Finalize UI design and user experience (Streamlit).

## Phase 6: Testing & Validation
- [ ] Implement unit and integration tests for all modules.
- [ ] Perform E2E tests with real-world scenarios (accidental deletion, damaged storage).
- [ ] Evaluate model performance (accuracy, precision, denoising quality).
- [ ] Document project usage and API.
