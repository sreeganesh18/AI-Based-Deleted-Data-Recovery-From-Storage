import io
import hashlib
from PIL import Image


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
