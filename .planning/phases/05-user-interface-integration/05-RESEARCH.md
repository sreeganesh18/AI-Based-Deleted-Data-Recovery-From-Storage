# Phase 5: User Interface & Integration - Research

**Researched:** 2025-03-01
**Domain:** User Interface, Streamlit, Systems Integration
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

#### 1. UI Layout & Navigation
- **Structure:** The application will be implemented as a **Multi-page Streamlit App** to cleanly separate different stages of the recovery process.
- **Configuration:** Primary controls (Disk Image selection, Model Checkpoints loading) will be located in the **Main View** of the configuration page rather than the sidebar.
- **Feedback Loop:**
    - Scanning and carving results will be updated in **Real-time** as fragments are identified.
    - A **Live Log Feed** will be provided to show the detailed execution status of the backend modules.

#### 2. Forensic Visualization
- **Mapping:** Identified fragments will be presented in a **List/Grid format** for clarity and searchability.
- **Reassembly Tracking:** Fragments within a reconstructed file will be shown as a **Sequential List**, providing a clear audit trail of the reassembly order.
- **Confidence Representation:** AI confidence scores for fragment classification will be displayed using **Numerical Labels** (e.g., "94.5%").
- **Progress Tracking:** The UI will focus on **Macro-level (File-level) progress**, showing the overall status of the recovery session rather than per-block scanning details.

#### 3. Review Interaction
- **Quality Comparison:** The application will use an **Interactive Image Slider** to allow users to visually compare the Original, Denoised, and Enhanced versions of recovered files.
- **File Metadata:** Clicking a recovered file will show **Detailed Metadata**, including fragmentation count, disk offsets, MD5 hashes, and reassembly strategy.
- **Technical Inspection:** A **Hex-viewer component** will be integrated to allow the raw inspection of fragments.
- **Orphan Management:** Fragments that cannot be linked to a header will be managed in a **Dedicated Orphan Tab** for manual review and potential linking.

#### 4. Export Workflow
- **Selection:** Users must perform **Manual Selection** of files they wish to recover and export.
- **Conflict Management:** File naming collisions at the destination will be handled via **Auto-Suffixing** (e.g., `file_1.recovered`, `file_2.recovered`).
- **Reporting:** The export process will focus on the **Files Only**, without generating additional forensic summary reports for this phase.
- **Storage Structure:** All exported files will be saved into a **Flat Folder** at the chosen destination.

### Claude's Discretion
- Selection of specific Streamlit components for hex viewing and image comparison.
- Implementation patterns for background processing and state synchronization.

### Deferred Ideas (OUT OF SCOPE)
- (None at this time)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| UI-01 | Build basic Streamlit UI for storage scanning | `st.navigation` pattern identified for multi-page structure. |
| UI-02 | Implement UI components for fragment visualization and reconstruction progress | `st.dataframe` and `st.status` patterns researched. |
| UI-03 | Integrate backend modules into the UI | Background threading pattern with `Queue` and `add_script_run_ctx` verified. |
| UI-04 | Finalize UI design and user experience | Modern layout features (Top Nav, `st.html`) identified in Streamlit 1.54.0. |
</phase_requirements>

## Summary

Phase 5 focuses on transforming the backend recovery pipeline into a usable forensic tool. Research confirms that **Streamlit 1.54.0** (the project's current version) provides all necessary primitives for real-time feedback, multi-page navigation, and advanced layout control. The core architecture will transition from simple script execution to a state-driven multi-page application using **`st.navigation`**.

**Primary recommendation:** Use the **Programmatic Navigation Pattern** (`st.navigation`) instead of the traditional `pages/` directory to allow dynamic state-based page visibility and a cleaner top-level entry point (`main.py`).

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Streamlit | 1.54.0+ | UI Framework | Project standard; recently added `st.navigation` and `st.html`. |
| streamlit-image-comparison | 0.0.4 | Interactive comparison | Standard component for side-by-side image analysis. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| threading | Standard Lib | Async Backend | Running HybridCarver/Denoising without blocking UI. |
| queue | Standard Lib | State Sync | Passing logs and results from worker threads to main loop. |

**Installation:**
```bash
uv pip install streamlit-image-comparison
```

## Architecture Patterns

### Recommended Project Structure
```
ui/
├── app.py              # Entry point (st.navigation)
├── state.py            # Global session state management
├── components/         # Reusable UI widgets
│   ├── hex_viewer.py   # Custom hex dump component
│   └── logger.py       # Custom logging handler for Streamlit
└── views/              # Page definitions
    ├── config.py       # Configuration & Setup
    ├── scanning.py     # Real-time scan & Carve progress
    ├── review.py       # File reconstruction review
    └── export.py       # Final selection & Export
```

### Pattern 1: Programmatic Navigation
**What:** Using `st.navigation` to define the app structure in code.
**When to use:** Always for Phase 5 to support the multi-stage recovery workflow.
**Example:**
```python
import streamlit as st

# Defined in ui/app.py
pages = {
    "Setup": [
        st.Page("views/config.py", title="Configuration", icon="⚙️"),
    ],
    "Process": [
        st.Page("views/scanning.py", title="Scanning & Carving", icon="🔍"),
        st.Page("views/review.py", title="Review & Reassemble", icon="🖼️"),
    ],
    "Finish": [
        st.Page("views/export.py", title="Export Results", icon="💾"),
    ]
}

pg = st.navigation(pages)
pg.run()
```

### Pattern 2: Background Worker Thread
**What:** Running the `HybridCarver` or `DenoisingPipeline` in a separate thread to keep the UI responsive.
**When to use:** For any process lasting > 1 second.
**Example:**
```python
import threading
from queue import Queue
from streamlit.runtime.scriptrunner import add_script_run_ctx

def run_background_task(target_fn, args_dict):
    result_queue = Queue()
    thread = threading.Thread(target=target_fn, args=(result_queue, *args_dict.values()))
    add_script_run_ctx(thread)  # Ensures thread can interact with St context
    thread.start()
    return thread, result_queue
```

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image Comparison | Custom slider | `streamlit-image-comparison` | Battle-tested slider powered by JuxtaposeJS. |
| Progress Bars | Manual HTML/CSS | `st.progress` / `st.status` | Native support for state-driven updates. |
| Table Management | Manual HTML tables | `st.dataframe` | Supports JSON columns, pinning, and Excel-like features. |

## Common Pitfalls

### Pitfall 1: Duplicate Log Handlers
**What goes wrong:** Log messages appear multiple times or multiply on each rerun.
**Why it happens:** Adding a handler to a logger without checking if it exists or removing it.
**How to avoid:** Always use `logger.removeHandler(handler)` in a `finally` block or check `logger.hasHandlers()`.

### Pitfall 2: Fragment State Collision
**What goes wrong:** Removing a fragment from the "Sequential List" causes other fragments to lose their data.
**Why it happens:** Using list indices as keys for Streamlit widgets.
**How to avoid:** Always use stable unique IDs (like the fragment's MD5 hash or a UUID) as widget keys.

## Code Examples

### Custom Hex Viewer Widget
Verified pattern using `st.html` for clean layout:
```python
def format_hexdump(data, length=16):
    lines = []
    for i in range(0, len(data), length):
        chunk = data[i:i + length]
        offset = f"{i:08x}"
        hex_vals = " ".join(f"{b:02x}" for b in chunk).ljust(length * 3 - 1)
        ascii_vals = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        lines.append(f"<code>{offset}  {hex_vals}  |{ascii_vals}|</code>")
    return "<br>".join(lines)

# Usage in Streamlit
st.markdown(f"**Raw Fragment Data**")
st.html(f"<div style='font-family: monospace; background-color: #f0f2f6; padding: 10px; border-radius: 5px;'>{format_hexdump(fragment_bytes)}</div>")
```

### Real-Time Log Handler
```python
import logging

class StreamlitLogHandler(logging.Handler):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.buffer = []

    def emit(self, record):
        self.buffer.append(self.format(record))
        # Show last 15 lines
        self.placeholder.code("
".join(self.buffer[-15:]))

# In the UI
log_box = st.empty()
handler = StreamlitLogHandler(log_box)
# Attach to backend loggers...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `pages/` dir | `st.navigation` | v1.31.0 (2024) | Better control, dynamic pages, top-nav. |
| `st.write(df)` | `st.dataframe` | v1.50.0+ (2025) | JSON support, better density, column pinning. |
| Custom CSS for logs | `st.status` | v1.24.0+ (2023) | Native grouped progress visualization. |

## Open Questions

1. **Memory Pressure with Large Disk Images**
   - What we know: Disk images are read via raw scanner.
   - What's unclear: How Streamlit handles `st.session_state` size if many fragments are cached in memory for review.
   - Recommendation: Use `dataset/` directory as a persistent cache and only load metadata into `session_state`.

2. **Image Slider with 3 Images**
   - What we know: `streamlit-image-comparison` usually handles 2 images.
   - What's unclear: Best UX for comparing Original vs Denoised vs Enhanced (3 states).
   - Recommendation: Use a radio button/tabs to select the "base" and "target" for the slider, or use two sliders side-by-side.

## Sources

### Primary (HIGH confidence)
- [Streamlit Docs] - `st.navigation` and `st.Page` APIs.
- [Streamlit Release Notes 2025] - Features of version 1.54.0.
- [Official PyPI] - `streamlit-image-comparison` usage and installation.

### Secondary (MEDIUM confidence)
- [Streamlit Community Forums] - Pattern for background threading with `add_script_run_ctx`.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Libraries are stable and project-standard.
- Architecture: HIGH - Multi-page pattern is well-documented.
- Pitfalls: MEDIUM - Based on common Streamlit development patterns.

**Research date:** 2025-03-01
**Valid until:** 2025-04-01 (Streamlit moves fast)
