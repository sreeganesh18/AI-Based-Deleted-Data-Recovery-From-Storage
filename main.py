import argparse
import os
import sys

from storage_scan.scanner import DiskScanner
from carving.signature import SignatureCarver
from utils.validation import assign_confidence_score, check_file_integrity


def run_pipeline(image_path: str):
    print(f"[*] Starting full recovery pipeline on: {image_path}")
    if not os.path.exists(image_path):
        print(f"Error: Virtual disk {image_path} not found.")
        return

    # 1. Scanner & Extractor
    print("[*] Initializing Raw Sector Scanner...")
    scanner = DiskScanner(image_path, block_size=512)

    # 2. Carver
    print("[*] Initializing Signature Carver for JPEG...")
    carver = SignatureCarver(block_size=512)

    # Scanning loop
    print("[*] Scanning starting. This may take a while depending on image size...")
    total_blocks = 0
    try:
        for offset, block in scanner.scan_blocks():
            carver.process_block(offset, block)
            total_blocks += 1
            if total_blocks % 100000 == 0:
                print(f"  -> Scanned {total_blocks} blocks...")
    except Exception as e:
        print(f"Scanner exception: {e}")

    print(f"[*] Scanning complete. Total blocks read: {total_blocks}")
    carved_files = carver.get_carved_files()
    print(f"\n[*] Found {len(carved_files)} carved JPEG stream fragments.")

    valid_count = 0
    for idx, fobj in enumerate(carved_files):
        data = fobj["data"]
        offset = fobj["start_offset"]
        confidence = assign_confidence_score(data)

        status = "CORRUPT/FRAGMENTED"
        if check_file_integrity(data):
            status = "VALID"
            valid_count += 1

        print(
            f"  [{idx + 1}] Offset: {offset} | Size: {len(data)} bytes | Status: {status} | Confidence: {confidence:0.1f}%"
        )

    print(
        f"[*] Pipeline summary: {valid_count}/{len(carved_files)} files fully working."
    )
    print(
        "[*] Run the streamit app with 'streamlit run ui/app.py' to use the graphical interface."
    )


def main():
    parser = argparse.ArgumentParser(
        description="AI-Based Deleted Image Recovery and Reconstruction System"
    )
    parser.add_argument("--image", type=str, help="Path to raw disk image (.img, .dd)")
    args = parser.parse_args()

    if args.image:
        run_pipeline(args.image)
    else:
        print("Backend scaffold complete and ready.")
        print("Run `python main.py --image <path_to_img_file>` to scan an image.")
        print("Run `streamlit run ui/app.py` for the web UI.")


if __name__ == "__main__":
    main()
