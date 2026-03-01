# PHASE 4 CONTEXT: Reconstruction & Enhancement

## Decisions

### 1. Grouping Logic & Ordering
- **Search Radius:** For fragmented or non-contiguous files, the system will search for the next relevant block within a radius of **1MB (or approximately 100 clusters)** from the current block offset.
- **Ordering Priority:** A **mixed approach** will be used, prioritizing both sequential disk offsets and AI-predicted sequence scores to determine the correct order of fragments.
- **End-of-File Detection:** When no explicit footer is found, the system will perform a **"best effort" reconstruction** until the end of the disk image or until a definitive conflict occurs.
- **Orphaned Fragments:** Fragments identified by the classifier but not linked to a known header will be **kept for later linking** (stored in a dedicated "orphaned" category for potential manual review).

### 2. Success Criteria
- **Minimum Recovery Threshold:** A file is considered "successfully reconstructed" if at least **90%** of its expected data is recovered.
- **Validation Scope:** Checksum validation (MD5/SHA1) will be performed on **all recovered files that have a detected header**, regardless of whether a footer was found.
- **Integrity Failures:** Files that fail structural integrity checks (e.g., corrupted JPEG/PDF) will be **kept** and flagged for further review rather than being discarded.
- **Partial Recovery Policy:** The system will provide a **user-configurable option** to determine whether to present partial files or only those that meet strict "clean" criteria.

### 3. Enhancement Policy
- **Automated Denoising:** Denoising (via the Phase 3 Autoencoder) will be applied to **all reconstructed files by default** to maximize visual/data quality.
- **Structural Repair:** The system **is encouraged to attempt structural repairs**, such as synthesizing missing headers or footers, if enough metadata is present to facilitate it.
- **Naming Convention:** Recovered files should follow the format: **`original_name.recovered`**.
- **Enhancement Depth:** Beyond basic denoising, the system will explore **advanced visual enhancement** techniques (e.g., super-resolution) where applicable for the recovered media.

### 4. Conflict Handling
- **Fragment Prioritization:** When multiple fragments match the same "slot," the system will use a **"best effort" prioritization** (e.g., balancing AI confidence and disk proximity).
- **Overlapping Headers:** If a new header is discovered mid-reconstruction, the system will attempt **parallel reconstruction**, effectively treating both potential files as active paths.
- **Missing Data Gaps:** Any gaps in the reconstructed file structure will be **filled with zeros** to maintain the correct structural alignment of the remaining fragments.
- **Conflict Resolution:** The system will **allow for manual user review** in cases where automated logic cannot definitively resolve a fragment conflict.

## Deferred Ideas
- (None at this time)
