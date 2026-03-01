# AI Deleted Data Recovery: User Guide

This guide provides instructions for installing, configuring, and using the AI-based deleted data recovery system.

## 1. Installation

### Requirements
- OS: Windows 10/11 (Optimized for AMD Ryzen 9)
- Python: 3.10+
- Hardware: At least 16GB RAM, modern CPU (AVX-512 support recommended)

### Setup
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd AI_Deleted_Data_Recovery
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Download pre-trained models (if not already present):
   Ensure `models/checkpoints/classifier_best.pth` and `models/checkpoints/autoencoder_best.pth` are in place.

## 2. Configuration

### Model Loading
The system automatically loads the best available models from the `models/checkpoints/` directory.

### Directory Structure
- `dataset/original`: Place your raw disk images or files here for scanning.
- `dataset/fragments`: Temporary storage for carved fragments.
- `dataset/reconstructed`: Output directory for recovered files.

## 3. Recovery Process (Using the UI)

### Start the Application
Run the Streamlit application:
```bash
streamlit run main.py
```
*Note: Depending on the entry point, it might be `streamlit run ui/app.py` if not redirected in `main.py`.*

### Step-by-Step Recovery
1. **Scanning**: Use the "Scanning" view to select a disk image or folder. The system will perform block-level scanning and entropy profiling.
2. **Reviewing**: In the "Review" view, you can see identified fragments, their predicted file types, and confidence scores.
3. **Recovery**: Select the fragments or files you want to recover. The system will use the reassembly engine and generative repair module to reconstruct the files.
4. **Export**: Use the "Export" view to save the recovered files to the `dataset/reconstructed` directory.

## 4. Interpreting Results and Logs

### Confidence Scores
- **> 90%**: High confidence. The fragment strongly matches the predicted file type.
- **70% - 90%**: Moderate confidence. Reassembly may require manual verification.
- **< 70%**: Low confidence. Fragment might be corrupted or of an unsupported type.

### Metrics
- **PSNR (Peak Signal-to-Noise Ratio)**: Measures the quality of denoised/reconstructed images. Higher is better (Target: > 30 dB).
- **SSIM (Structural Similarity Index)**: Measures visual fidelity. Ranges from 0 to 1, with 1 being perfect (Target: > 0.90).

### Logs
Logs are saved in the `logs/` directory (if configured) or printed to the console. They contain detailed information about offset locations, classification results, and any errors encountered during reassembly.

## 5. Troubleshooting
- **Model not found**: Check the `models/checkpoints/` directory.
- **Out of memory**: Reduce the batch size in the configuration if processing very large disk images.
- **Low recovery rate**: Ensure the disk image is raw (bit-for-bit) and not a proprietary forensic format like .E01 unless supported.
