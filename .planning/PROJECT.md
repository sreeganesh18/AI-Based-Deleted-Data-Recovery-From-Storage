# PROJECT: AI Deleted Data Recovery

## Overview
AI-powered system for recovering deleted data and reconstructing damaged storage. The project uses Deep Learning (Autoencoders) for data denoising and Classifiers for file carving across various file systems and formats.

## Goals
- Accidental file deletion recovery.
- Damaged storage reconstruction.
- Denoising corrupted file fragments using Autoencoders.
- File carving with Classifiers.

## Context
- **Language:** Python 3.12+
- **Deep Learning Framework:** PyTorch
- **UI Framework:** Streamlit
- **Target File Types:** JPEG, PDF
- **Target File Systems:** NTFS, FAT32

## Constraints
- Must handle fragmented and corrupted data.
- Must provide a user-friendly Streamlit UI.
- Must support efficient storage scanning.
