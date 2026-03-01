from reconstruction.denoise import DenoisingPipeline
import os

def test_denoise():
    # 1. Initialize pipeline
    pipeline = DenoisingPipeline(checkpoint_path="models/checkpoints/autoencoder_best.pth",
                                output_dir="dataset/fragments/denoised_test/")
    
    # 2. Create a dummy noisy fragment
    import numpy as np
    noisy_fragment = np.random.randint(0, 256, 512, dtype=np.uint8).tobytes()
    
    # 3. Denoise
    denoised_fragment = pipeline.denoise_fragment(noisy_fragment)
    
    # 4. Save and verify
    path = pipeline.save_denoised("test_frag_001.bin", denoised_fragment)
    
    if os.path.exists(path):
        print(f"SUCCESS: Denoised fragment saved to {path}")
        print(f"Denoised fragment size: {len(denoised_fragment)} bytes")
    else:
        print("FAILURE: Denoised fragment not saved")

if __name__ == "__main__":
    test_denoise()
