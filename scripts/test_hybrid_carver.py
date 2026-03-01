from carving.hybrid import HybridCarver
import os

def test_hybrid_carver():
    # 1. Initialize carver
    carver = HybridCarver(checkpoint_path="models/checkpoints/classifier_best.pth")
    
    # 2. Test JPEG signature detection
    jpeg_header = b"\xff\xd8\xff\xe0" + b"\x00" * 508
    id_jpeg = carver.identify_fragment(jpeg_header)
    print(f"JPEG Signature Result: {id_jpeg}")
    
    # 3. Test PDF signature detection
    pdf_header = b"%PDF-1.5" + b"\x00" * 504
    id_pdf = carver.identify_fragment(pdf_header)
    print(f"PDF Signature Result: {id_pdf}")
    
    # 4. Test AI classification (using dummy random data)
    import numpy as np
    random_frag = np.random.randint(0, 256, 512, dtype=np.uint8).tobytes()
    id_ai = carver.identify_fragment(random_frag)
    print(f"AI Fallback Result: {id_ai}")

if __name__ == "__main__":
    test_hybrid_carver()
