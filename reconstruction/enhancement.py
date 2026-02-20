import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim


def apply_super_resolution(image: np.ndarray) -> np.ndarray:
    """
    Enhances resolution of an image using classical interpolation.
    In a fully advanced mode, you'd replace this with ESRGAN/SRCNN loading logic.
    """
    h, w = image.shape[:2]
    return cv2.resize(image, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)


def denoise_image(image: np.ndarray) -> np.ndarray:
    """
    Applies Non-Local Means Denoising to the reconstructed image.
    """
    if len(image.shape) == 3 and image.shape[2] == 3:
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)


def compute_metrics(original: np.ndarray, enhanced: np.ndarray) -> dict:
    """
    Computes PSNR and SSIM for evaluation.
    """
    h, w = enhanced.shape[:2]
    original_resized = cv2.resize(original, (w, h), interpolation=cv2.INTER_CUBIC)

    psnr_score = cv2.PSNR(original_resized, enhanced)

    # Convert to grayscale for SSIM
    if len(original_resized.shape) == 3:
        orig_gray = cv2.cvtColor(original_resized, cv2.COLOR_BGR2GRAY)
        enh_gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    else:
        orig_gray = original_resized
        enh_gray = enhanced

    ssim_score = ssim(orig_gray, enh_gray, data_range=enh_gray.max() - enh_gray.min())
    return {"PSNR": psnr_score, "SSIM": ssim_score}
