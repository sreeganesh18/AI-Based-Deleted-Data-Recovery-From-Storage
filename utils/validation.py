import io
import hashlib
import torch
import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim


def calculate_md5(data: bytes) -> str:
    """Computes MD5 hash of recovered file."""
    md5_hash = hashlib.md5()
    md5_hash.update(data)
    return md5_hash.hexdigest()


def check_file_integrity(data: bytes) -> bool:
    """
    Attempt to parse the bytes as a valid image file.
    """
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()  # verifies using PIL
        return True
    except Exception:
        return False


def validate_integrity(data: bytes, file_type: str = None) -> bool:
    """
    Unified integrity check for images and PDFs.
    """
    if not data:
        return False
        
    # Auto-detect if not provided
    if not file_type:
        if data.startswith(b"\xff\xd8"):
            file_type = "jpeg"
        elif data.startswith(b"%PDF"):
            file_type = "pdf"
        elif data.startswith(b"\x89PNG"):
            file_type = "png"

    if file_type in ["jpeg", "jpg", "png", "bmp", "image"]:
        try:
            img = Image.open(io.BytesIO(data))
            # Just opening it validates the header and basic structure
            return True
        except Exception:
            return False
            
    if file_type == "pdf":
        try:
            import fitz
            doc = fitz.open(stream=data, filetype="pdf")
            is_valid = doc.is_pdf and not doc.is_closed
            doc.close()
            return is_valid
        except Exception:
            return False
            
    # Default to existing image check if type unknown
    return check_file_integrity(data)


def assign_confidence_score(data: bytes) -> float:
    """
    Assigns a confidence score to the reconstructed file.
    Max 100.0%.
    """
    score = 0.0
    if check_file_integrity(data):
        score += 85.0
    if data.startswith(b"\xff\xd8"):
        score += 15.0  # True JPEG indicator
    return score


def calculate_psnr(original: torch.Tensor, reconstructed: torch.Tensor) -> float:
    """
    Computes Peak Signal-to-Noise Ratio (PSNR) between original and reconstructed fragments.
    Input: Tensors (batch, 1, 512) or (1, 512).
    """
    # Convert to numpy and flatten for skimage
    orig_np = original.detach().cpu().numpy().astype(np.float32)
    reco_np = reconstructed.detach().cpu().numpy().astype(np.float32)
    
    # PSNR needs a data_range if input is normalized [0, 1]
    return psnr(orig_np, reco_np, data_range=1.0)


def calculate_ssim(original: torch.Tensor, reconstructed: torch.Tensor) -> float:
    """
    Computes Structural Similarity Index (SSIM) between original and reconstructed fragments.
    Input: Tensors (batch, 1, 512) or (1, 512).
    """
    orig_np = original.detach().cpu().numpy()
    reco_np = reconstructed.detach().cpu().numpy()
    
    # Handle batch dimension
    if orig_np.ndim == 3: # (batch, 1, 512)
        ssims = []
        for i in range(orig_np.shape[0]):
            o = orig_np[i, 0, :]
            r = reco_np[i, 0, :]
            ssims.append(ssim(o, r, data_range=1.0, win_size=7))
        return np.mean(ssims)
    
    # Single sample
    orig_np = orig_np.squeeze()
    reco_np = reco_np.squeeze()
    return ssim(orig_np, reco_np, data_range=1.0, win_size=7)
