# =============================================================================
# AI-Based Deleted Data Recovery — Dockerfile
# Base: Python 3.12 slim (Debian Bookworm)
# Purpose: Runs Streamlit web UI + CLI pipeline tools
# Architecture: Single-container, CPU-only inference
# =============================================================================

FROM python:3.12-slim-bookworm

# ---------------------------------------------------------------------------
# OS-level system dependencies
# ---------------------------------------------------------------------------
# libGL1 + libglib2.0-0       : Required by opencv-python headless alternative
# libgomp1                     : OpenMP runtime for PyTorch CPU kernels
# libglib2.0-0                 : Required for GLib (used by cv2)
# libsm6 libxext6 libxrender1  : X11 stubs required by some OpenCV operations
# curl                         : For healthcheck / debugging
# ---------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
# Create a non-root user for security
# ---------------------------------------------------------------------------
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# ---------------------------------------------------------------------------
# Set working directory
# ---------------------------------------------------------------------------
WORKDIR /app

# ---------------------------------------------------------------------------
# Install Python dependencies
# ---------------------------------------------------------------------------
# Copy dependency files first for Docker layer caching
COPY requirements.txt pyproject.toml ./

# Upgrade pip
RUN pip install --upgrade pip --no-cache-dir

# Install declared dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install streamlit-image-comparison — used in ui/views/review.py
# NOTE: This package is missing from requirements.txt / pyproject.toml
#       It MUST be added by the developer to avoid environment drift.
RUN pip install --no-cache-dir streamlit-image-comparison

# ---------------------------------------------------------------------------
# Copy application source code
# ---------------------------------------------------------------------------
COPY --chown=appuser:appuser . .

# ---------------------------------------------------------------------------
# Install the project itself in editable mode (respects pyproject.toml)
# This enables `from carving.xxx import ...`, `from models.xxx import ...` etc.
# ---------------------------------------------------------------------------
RUN pip install --no-cache-dir -e .

# ---------------------------------------------------------------------------
# Create runtime directories expected by the application
# ---------------------------------------------------------------------------
RUN mkdir -p \
    models/checkpoints \
    dataset/fragments/denoised \
    dataset/original \
    dataset/reconstructed \
    reconstruction/models \
    recovered_data \
    && chown -R appuser:appuser /app

# ---------------------------------------------------------------------------
# Switch to non-root user
# ---------------------------------------------------------------------------
USER appuser

# ---------------------------------------------------------------------------
# Expose Streamlit default port
# ---------------------------------------------------------------------------
EXPOSE 8501

# ---------------------------------------------------------------------------
# Healthcheck — verifies Streamlit is responding
# ---------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# ---------------------------------------------------------------------------
# Default command — run Streamlit UI
# Override with: docker compose run app python main.py --image /data/image.img
# ---------------------------------------------------------------------------
CMD ["streamlit", "run", "ui/app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
