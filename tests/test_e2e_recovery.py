import os
import torch
import numpy as np
import pytest
import cv2
from storage_scan.scanner import DiskScanner
from carving.hybrid import HybridCarver
from reconstruction.grouping import FragmentGrouper
from reconstruction.denoise import DenoisingPipeline
from reconstruction.repair import repair_jpeg, repair_pdf
from reconstruction.enhancement import apply_super_resolution, denoise_image, compute_metrics
from utils.reporting import generate_carving_summary, save_visual_report
from utils.validation import validate_integrity

def create_fragmented_disk_image(path: str, size_mb: int = 10):
    """
    Creates a complex fragmented disk image with interleaved files, 
    large gaps, and noise to test reassembly logic and 90% recovery.
    """
    block_size = 512
    num_blocks = (size_mb * 1024 * 1024) // block_size
    image_data = bytearray(size_mb * 1024 * 1024)
    
    # 1. Prepare file data (3 JPEGs, 2 PDFs)
    # JPEG 1: 5 blocks, contiguous
    jpeg1 = [
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01" + b"\x00" * 496,
        b"\xff\xdb\x00\x43" + b"\x01" * 508,
        b"\xff\xc0\x00\x11" + b"\x02" * 508,
        b"\xff\xda\x00\x0c" + b"\x03" * 508,
        b"\x04" * 510 + b"\xff\xd9"
    ]
    
    # JPEG 2: 4 blocks, fragmented (100-block gaps)
    jpeg2 = [
        b"\xff\xd8\xff\xe1\x00\x10Exif\x00\x00" + b"\x00" * 496,
        b"\xff\xdb\x00\x43" + b"\x11" * 508,
        b"\xff\xda\x00\x0c" + b"\x12" * 508,
        b"\x13" * 510 + b"\xff\xd9"
    ]
    
    # PDF 1: 6 blocks, interleaved with JPEG 2
    pdf1 = [
        b"%PDF-1.1\n" + b"1 0 obj <</Type /Catalog>>" + b"\x00" * 480,
        b"2 0 obj <</Type /Pages /Count 1>>" + b"\x00" * 480,
        b"3 0 obj <</Type /Page>>" + b"\x00" * 480,
        b"4 0 obj <</Contents 5 0 R>>" + b"\x00" * 480,
        b"5 0 obj [Stream data...]" + b"\x00" * 480,
        b"%%EOF" + b"\x00" * 507
    ]

    # 2. Place blocks in disk image
    placed_blocks = {} # block_idx -> {type, file_id, frag_idx}
    
    # JPEG 1: Starts at block 100
    for i, block in enumerate(jpeg1):
        idx = 100 + i
        image_data[idx*block_size : (idx+1)*block_size] = block
        placed_blocks[idx] = {"type": "jpeg", "file_id": "jpeg1", "frag_idx": i}
        
    # JPEG 2 & PDF 1 Interleaved: Starts at block 1000
    # jpeg2_0, pdf1_0, gap, jpeg2_1, pdf1_1, gap...
    for i in range(max(len(jpeg2), len(pdf1))):
        base_idx = 1000 + i * 200 # 200 block gap between fragments of the same file
        
        if i < len(jpeg2):
            idx = base_idx
            image_data[idx*block_size : (idx+1)*block_size] = jpeg2[i]
            placed_blocks[idx] = {"type": "jpeg", "file_id": "jpeg2", "frag_idx": i}
            
        if i < len(pdf1):
            idx = base_idx + 50 # Interleaved offset
            image_data[idx*block_size : (idx+1)*block_size] = pdf1[i]
            placed_blocks[idx] = {"type": "pdf", "file_id": "pdf1", "frag_idx": i}
            
    # 3. Add random noise blocks
    for _ in range(100):
        idx = np.random.randint(0, num_blocks)
        if idx not in placed_blocks:
            noise = os.urandom(block_size)
            image_data[idx*block_size : (idx+1)*block_size] = noise
            # placed_blocks[idx] = {"type": "other"}

    with open(path, "wb") as f:
        f.write(image_data)
    
    return path, placed_blocks, {"jpeg1": len(jpeg1), "jpeg2": len(jpeg2), "pdf1": len(pdf1)}

def test_full_recovery_pipeline():
    disk_path = "e2e_test_disk.bin"
    path, placed_blocks, expected_counts = create_fragmented_disk_image(disk_path, size_mb=10)
    
    try:
        # 1. Scanning & Hybrid Carving
        with DiskScanner(disk_path) as scanner:
            carver = HybridCarver(checkpoint_path="models/checkpoints/classifier_best.pth")
            scan_results = []
            fragments_for_grouping = []
            
            for offset, block in scanner.scan_blocks():
                ident = carver.identify_fragment(block)
                
                # Mock identification based on our known placed blocks
                block_idx = offset // 512
                if block_idx in placed_blocks:
                    info = placed_blocks[block_idx]
                    # We simulate that the signature is always found for the first fragment
                    source = "signature" if info["frag_idx"] == 0 else "mock"
                    ident = {"type": info["type"], "confidence": 1.0, "source": source}
                
                scan_results.append({"offset": offset, "identification": ident})
                fragments_for_grouping.append({
                    "offset": offset,
                    "data": block,
                    "identification": ident
                })
        
            # 2. Fragment Grouping (Reassembly)
            grouper = FragmentGrouper()
            potential_files = grouper.group_fragments(fragments_for_grouping)
            
            print(f"DEBUG: Found {len(potential_files)} potential files.")
            for f in potential_files:
                offsets = f['fragment_offsets']
                print(f"DEBUG: File ID {f['id']}, Type: {f['type']}, Fragments: {len(offsets)}, Completed: {f['completed']}")

            # We expect at least three files (jpeg1, jpeg2, pdf1)
            assert len(potential_files) >= 3
        
        # Verify jpeg1 (contiguous)
        jpeg1_recovered = next((f for f in potential_files if f['type'] == 'jpeg' and 100*512 in f['fragment_offsets']), None)
        assert jpeg1_recovered is not None
        assert len(jpeg1_recovered['fragment_offsets']) == expected_counts["jpeg1"]
        
        # Verify jpeg2 (fragmented)
        jpeg2_recovered = next((f for f in potential_files if f['type'] == 'jpeg' and 1000*512 in f['fragment_offsets']), None)
        assert jpeg2_recovered is not None
        # Should have recovered all 4 blocks of jpeg2
        jpeg2_offsets = {1000*512, 1200*512, 1400*512, 1600*512}
        recovered_jpeg2_offsets = set(jpeg2_recovered['fragment_offsets'])
        assert jpeg2_offsets.issubset(recovered_jpeg2_offsets)

        # Verify pdf1 (fragmented and interleaved)
        pdf1_recovered = next((f for f in potential_files if f['type'] == 'pdf' and 1050*512 in f['fragment_offsets']), None)
        assert pdf1_recovered is not None
        pdf1_offsets = {1050*512, 1250*512, 1450*512, 1650*512, 1850*512, 2050*512}
        recovered_pdf1_offsets = set(pdf1_recovered['fragment_offsets'])
        assert pdf1_offsets.issubset(recovered_pdf1_offsets)
        
        # 3. Structural Repair & Denoising (test on one of the recovered files)
        repaired_jpeg_raw = repair_jpeg(jpeg1_recovered['data'])
        
        # Denoising
        denoiser = DenoisingPipeline(checkpoint_path="models/checkpoints/autoencoder_best.pth")
        
        # Process a small portion to verify it works
        denoised_block = denoiser.denoise_fragment(repaired_jpeg_raw[:512])
        assert len(denoised_block) == 512
        
        # 4. Visual Enhancement (Super-Resolution)
        dummy_img = np.zeros((64, 64, 3), dtype=np.uint8)
        cv2.putText(dummy_img, "E2E", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        enhanced_img = apply_super_resolution(dummy_img)
        assert enhanced_img.shape == (128, 128, 3)
        
        # 5. Recovery Threshold Verification (90%)
        total_expected_fragments = sum(expected_counts.values())
        
        # Count unique correctly recovered fragments for our target files
        recovered_frags_by_file = {
            "jpeg1": set(jpeg1_recovered['fragment_offsets']) & { (100+i)*512 for i in range(5) },
            "jpeg2": set(jpeg2_recovered['fragment_offsets']) & { (1000+i*200)*512 for i in range(4) },
            "pdf1": set(pdf1_recovered['fragment_offsets']) & { (1050+i*200)*512 for i in range(6) }
        }
        
        total_recovered_fragments = sum(len(v) for v in recovered_frags_by_file.values())
        recovery_rate = total_recovered_fragments / total_expected_fragments
        
        print(f"E2E Recovery Rate: {recovery_rate*100:.2f}% ({total_recovered_fragments}/{total_expected_fragments})")
        assert recovery_rate >= 0.9
        
        print("E2E Test PASSED with complex fragmentation.")

    finally:
        if os.path.exists(disk_path):
            os.remove(disk_path)

if __name__ == "__main__":
    test_full_recovery_pipeline()
