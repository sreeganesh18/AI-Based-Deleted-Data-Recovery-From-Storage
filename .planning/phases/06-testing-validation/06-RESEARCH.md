# Phase 6: Testing & Validation - Research

**Researched:** 2025-03-01
**Domain:** Software Testing, AI Model Validation, Data Recovery Verification
**Confidence:** HIGH

## Summary
This phase establishes the final validation framework for the AI Deleted Data Recovery project. The system requires rigorous testing of binary data handling, AI model accuracy, and the reassembly logic of the integrated pipeline.

**Primary recommendation:** Standardize all tests on `pytest`, ensuring `PYTHONPATH` is correctly configured to allow seamless imports of core modules.

## Standard Stack
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.2+ | Core testing framework | Robust, extensible, and already in use. |
| scikit-image | 0.26.0+ | PSNR/SSIM metrics | Industry standard for image/signal quality. |
| scikit-learn | 1.8.0+ | F1/Precision/Recall | Essential for classification performance evaluation. |
| PyMuPDF | 1.24.0+ | PDF Integrity | Reliable parsing and repair verification for PDFs. |

## Architecture Patterns
### Recommended Project Structure
```
tests/
├── fixtures/            # Static binary samples (headers, footers)
├── test_scanner.py      # Unit tests for storage_scan
├── test_carver.py       # Unit tests for carving logic
├── test_models.py       # Unit tests for torch models
├── test_reconstruction.py # Unit tests for grouping/repair
└── test_e2e_recovery.py # Full pipeline validation
```

## Don't Hand-Roll
| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Signal Metrics | Custom PSNR | `skimage.metrics` | Handles edge cases and normalization correctly. |
| PDF Parsing | Raw byte search | `fitz` (PyMuPDF) | PDF structure is complex; libraries handle XREFs better. |
| Mocking | Custom mock classes | `unittest.mock` | Built-in, handles call counting and side effects. |

## Common Pitfalls
### Pitfall 1: Block Alignment Errors
**What goes wrong:** Fragments are misaligned or padded incorrectly, causing the Classifier to fail.
**How to avoid:** Always use 512-byte blocks and explicit padding (`ljust(512, b"\x00")`) in tests.

### Pitfall 2: Checkpoint Dependency
**What goes wrong:** Tests fail if model weights aren't present in `models/checkpoints/`.
**How to avoid:** Use mock models for unit tests or ensure a "minimal" stable checkpoint is available for integration tests.

## Code Examples
### Quantitative Evaluation (from `utils/validation.py`)
```python
from skimage.metrics import peak_signal_noise_ratio as psnr
def calculate_psnr(original: torch.Tensor, reconstructed: torch.Tensor) -> float:
    orig_np = original.detach().cpu().numpy().astype(np.float32)
    reco_np = reconstructed.detach().cpu().numpy().astype(np.float32)
    return psnr(orig_np, reco_np, data_range=1.0)
```

## Validation Architecture
- **Framework:** `pytest`
- **Quick run command:** `pytest tests/test_scanner.py tests/test_carver.py`
- **Full suite command:** `$env:PYTHONPATH="."; pytest`
- **Estimated feedback latency:** ~10-15 seconds for unit tests, ~60 seconds for E2E.

### Sources
- **Official Docs:** Pytest Documentation, PyTorch Testing API, Scikit-Image Metrics.
- **Internal:** Existing `tests/test_e2e_recovery.py` and `utils/validation.py`.
