import cv2
import numpy as np
import os
import urllib.request
from skimage.metrics import structural_similarity as ssim

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
FSRCNN_MODEL_URL = "https://github.com/Saafke/FSRCNN_Tensorflow/raw/master/models/FSRCNN_x2.pb"
FSRCNN_MODEL_PATH = os.path.join(MODEL_DIR, "FSRCNN_x2.pb")


def download_model():
    """Downloads the FSRCNN x2 model if not already present."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    if not os.path.exists(FSRCNN_MODEL_PATH):
        print(f"Downloading FSRCNN model from {FSRCNN_MODEL_URL}...")
        try:
            urllib.request.urlretrieve(FSRCNN_MODEL_URL, FSRCNN_MODEL_PATH)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download FSRCNN model: {e}")
            return False
    return True


def apply_super_resolution(image: np.ndarray) -> np.ndarray:
    """
    Enhances resolution of an image using AI Super-Resolution (FSRCNN x2).
    Falls back to INTER_CUBIC if the model is unavailable.
    """
    if download_model() and os.path.exists(FSRCNN_MODEL_PATH):
        try:
            sr = cv2.dnn_superres.DnnSuperResImpl_create()
            sr.readModel(FSRCNN_MODEL_PATH)
            sr.setModel("fsrcnn", 2)  # Scale factor is 2
            
            # Perform SR
            enhanced = sr.upsample(image)
            return enhanced
        except Exception as e:
            print(f"AI Super-Resolution failed: {e}. Falling back to cubic interpolation.")
    
    # Fallback to classical interpolation
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


if __name__ == "__main__":
    import sys
    if "--test-sr" in sys.argv:
        # Create a dummy image for testing
        test_img = np.zeros((64, 64, 3), dtype=np.uint8)
        cv2.putText(test_img, "AI", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        print("Testing Super-Resolution...")
        enhanced = apply_super_resolution(test_img)
        print(f"Original shape: {test_img.shape}")
        print(f"Enhanced shape: {enhanced.shape}")
        
        if enhanced.shape == (test_img.shape[0] * 2, test_img.shape[1] * 2, 3):
            print("Super-Resolution test PASSED.")
        else:
            print("Super-Resolution test FAILED (incorrect shape).")
            sys.exit(1)
