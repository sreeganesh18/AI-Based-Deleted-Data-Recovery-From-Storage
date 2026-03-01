# PHASE 3 CONTEXT: File Carving & Denoising

## Decisions

### 1. Model Evaluation Metrics & Thresholds
- **Classifier Performance Targets:**
  - Minimum accuracy: **90% for JPEG**, **85% for PDF**.
  - Target false-positive rate: **< 5%**.
  - Preference: It is better to **miss a fragment** (unidentified) than to **misclassify** it.
- **Autoencoder Performance Targets:**
  - Success will be measured using **PSNR (Peak Signal-to-Noise Ratio)** and **SSIM (Structural Similarity Index)**.
- **Validation Strategy:**
  - A **20% split** of the training data will be used for validation, stored in a **separate folder** to ensure independence.

### 2. Classifier Integration
- **Low Confidence Handling:** Fragments with low classification confidence (e.g., < 0.7) should be **skipped** or flagged rather than being processed by a specific carver.
- **Multiple Carver Attempts:** If classification is ambiguous (e.g., high scores for multiple types), the system **is allowed to attempt carving with multiple relevant carvers**.
- **Noise/Other Handling:** Fragments predicted as "noise" or "other" should be **logged and stored separately** for potential future review.
- **Conflict Resolution:** Traditional **header/footer signatures** take precedence over the Classifier's prediction if they conflict.

### 3. Autoencoder Integration
- **Denoising Timing:** Denoising will be applied to **all fragments** during the reconstruction phase.
- **Denoising Scope:** The **entire block** (fragment) will be processed by the Autoencoder.
- **Output Storage:** Denoised fragments must be stored in a **separate location**; the original "raw" fragments must not be overwritten.
- **Quality Threshold:** **All denoised output will be kept**, regardless of the PSNR/SSIM score (no automatic discarding based on quality).

### 4. Reporting & Feedback
- **Training Logs:** Metrics (accuracy, loss, etc.) will be logged **every epoch**.
- **Carving Summary:** The final report for a carving run must include the **total number of fragments** processed and their classification status.
- **Visual Comparison:** During evaluation and potentially in the UI, a **visual "before vs. after" comparison** should be provided for all denoised fragments.

## Deferred Ideas
- (None at this time)
