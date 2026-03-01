# AI-Driven Deleted Data Recovery

An advanced system for recovering deleted and fragmented data from storage devices using a hybrid approach of traditional signature-based carving and modern deep learning models.

## Overview
This project addresses the challenge of recovering files when file system metadata (like FAT or MFT) is corrupted or missing. It combines:
- **Block-level Storage Scanning**: Efficiently reads raw disk images and identifies candidate fragments.
- **Hybrid Fragment Identification**: Uses a rule-based engine (signatures) and a 1D-CNN Classifier to identify file fragments (JPEG, PDF, etc.) even without headers.
- **Deep Learning Denoising**: Employs a Denoising Autoencoder to clean corrupted fragments before reassembly.
- **Intelligent Reassembly**: Groups fragments based on spatial and content analysis to reconstruct files.
- **Generative Repair**: Uses format-specific logic to fix broken headers and structures.
- **Streamlit UI**: Provides a user-friendly interface for scanning, reviewing, and recovering data.

## Features
- **High Accuracy**: Over 90% recall for JPEG and 85% for PDF fragments.
- **Robust Recovery**: Handles fragmented files and bit-level corruption.
- **Modern Tech Stack**: Built with Python, PyTorch, Streamlit, and Sphinx.
- **Forensic Ready**: Designed for bit-for-bit raw disk images.

## Project Status: PHASE 6 COMPLETE
The project has successfully completed all development phases:
1. **Foundation**: Core infrastructure and data loader.
2. **Models**: Deep learning classifier and autoencoder development.
3. **Carving & Denoising**: Hybrid carver and denoising pipeline integration.
4. **Reconstruction & Enhancement**: Reassembly engine and repair modules.
5. **UI & Integration**: End-to-end user interface and system integration.
6. **Testing & Validation**: Comprehensive unit/E2E testing and performance quantification.

## Quick Start
### 1. Installation
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the UI
```bash
streamlit run main.py
```

### 3. Run Evaluation
```bash
python scripts/evaluate_models.py
```

## Documentation
For detailed instructions, see:
- [User Guide](USER_GUIDE.md)
- [API Reference](docs/index.rst) (Generate using `sphinx-build docs docs/_build`)

## License
MIT License
