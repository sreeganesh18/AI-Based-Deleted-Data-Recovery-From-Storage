# RESEARCH: Phase 2 - Core AI Models

## Model Architectures

### 1. Fragment Classifier (File Type Identification)
- **Goal:** Identify if a 512-byte fragment is JPEG, PDF, or other.
- **Architecture:** 1D-CNN.
  - Input: (1, 512) tensor, normalized byte values (0-255 -> 0-1).
  - Convolutional Layers: 3x Conv1D layers with ReLU and BatchNorm.
  - Pooling: MaxPool1D to reduce dimensionality.
  - Fully Connected: Linear layers with Dropout to prevent overfitting.
  - Output: Softmax for multi-class classification (3 classes: JPEG, PDF, OTHER).
- **Training Loss:** CrossEntropyLoss.

### 2. Denoising Autoencoder (Data Repair)
- **Goal:** Reconstruct corrupted or noisy 512-byte fragments.
- **Architecture:** 1D Convolutional Autoencoder.
  - **Encoder:** 3x Conv1D layers with stride 2 to compress into a latent representation.
  - **Decoder:** 3x ConvTranspose1D layers to reconstruct the 512-byte sequence.
  - Activation: ReLU for hidden layers, Sigmoid for the output (to map back to 0-1).
- **Training Loss:** Mean Squared Error (MSE) or Binary Cross Entropy (BCE).

## Data Collection & Preprocessing
- **Source Data:** Collect 100-500 diverse JPEG and PDF files.
- **Fragmenting:** Split files into contiguous 512-byte blocks.
- **Noise Strategy (for DAE):**
  - Randomly flip bits/bytes in fragments.
  - Zero-out segments of the fragment.
  - Use original fragments as targets and corrupted ones as inputs.
- **Dataset Splitting:** 80% Train, 10% Val, 10% Test.

## Technical Stack
- **Library:** PyTorch (specified in project context).
- **Hardware:** CPU-compatible for development, GPU-ready via `.to(device)`.
