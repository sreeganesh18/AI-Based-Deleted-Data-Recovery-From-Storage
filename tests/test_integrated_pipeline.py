import os
import torch
import numpy as np
import pytest
from storage_scan.scanner import DiskScanner
from carving.hybrid import HybridCarver
from reconstruction.denoise import DenoisingPipeline
from utils.reporting import generate_carving_summary

def create_dummy_disk_image(path: str, size_mb: int = 1):
    """Creates a 1MB dummy disk image with embedded JPEG and PDF headers."""
    block_size = 512
    num_blocks = (size_mb * 1024 * 1024) // block_size
    
    with open(path, "wb") as f:
        for i in range(num_blocks):
            if i == 10:
                # Insert JPEG header
                block = b"\xff\xd8\xff\xe0" + b"\x00" * (block_size - 4)
            elif i == 50:
                # Insert PDF header
                block = b"%PDF-1.5" + b"\x00" * (block_size - 8)
            elif i == 100:
                # Random noise block (simulating corrupted fragment)
                block = np.random.randint(0, 256, block_size, dtype=np.uint8).tobytes()
            else:
                # Empty/Other block
                block = b"\x00" * block_size
            f.write(block)
    return path

def test_recovery_flow():
    disk_path = "test_disk_image.bin"
    create_dummy_disk_image(disk_path)
    
    try:
        # 1. Initialize Components
        with DiskScanner(disk_path) as scanner:
            carver = HybridCarver(checkpoint_path="models/checkpoints/classifier_best.pth")
            denoiser = DenoisingPipeline(checkpoint_path="models/checkpoints/autoencoder_best.pth",
                                         output_dir="dataset/fragments/denoised_test_e2e/")
            
            # 2. Run Integrated Pipeline
            scan_results = []
            identified_fragments = [] # (id, bytes) for denoising
            
            for offset, block in scanner.scan_blocks():
                ident = carver.identify_fragment(block)
                scan_results.append({"offset": offset, "identification": ident})
                
                # If it's identified as jpeg or pdf, we want to denoise it
                if ident["type"] in ["jpeg", "pdf"]:
                    frag_id = f"offset_{offset}.bin"
                    identified_fragments.append((frag_id, block))
            
            # 3. Denoising
            denoised_results = denoiser.process_batch(identified_fragments)
            for frag_id, denoised_bytes in denoised_results:
                denoiser.save_denoised(frag_id, denoised_bytes)
                
            # 4. Reporting
            summary = generate_carving_summary(scan_results)
            print(f"Carving Summary: {summary}")
            
            # 5. Assertions
            assert summary["total_fragments"] > 0
            assert summary["jpeg"]["signature"] == 1 # Block 10
            assert summary["pdf"]["signature"] == 1 # Block 50
            
            # Check if denoised files exist
            assert os.path.isdir("dataset/fragments/denoised_test_e2e/")
            assert len(os.listdir("dataset/fragments/denoised_test_e2e/")) >= 2
        
    finally:
        # Cleanup
        if os.path.exists(disk_path):
            os.remove(disk_path)

if __name__ == "__main__":
    # Allow running directly or via pytest
    test_recovery_flow()
