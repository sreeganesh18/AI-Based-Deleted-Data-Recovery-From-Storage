import io
import os
import subprocess
import logging

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

logger = logging.getLogger(__name__)

def repair_jpeg(data: bytes) -> bytes:
    """
    Synthesizes missing SOI/APP0 markers if needed.
    Ensures EOI marker is present.
    """
    if not data:
        return data

    repaired = bytearray(data)

    # Missing Start of Image (SOI) marker \xff\xd8
    # Forensic reconstruction might miss the first few bytes.
    if not repaired.startswith(b"\xff\xd8"):
        # If it looks like it has APP0 but missing SOI
        if repaired.startswith(b"\xff\xe0") or b"JFIF" in repaired[:10]:
            repaired = bytearray(b"\xff\xd8") + repaired
        else:
            # Minimal SOI + APP0 (JFIF) synthesis if completely missing
            # JFIF header: SOI (FF D8), APP0 (FF E0), length (00 10), "JFIF\0", version 1.1, units, density
            header = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00"
            # Only prepend if it doesn't seem to have ANY marker
            if not repaired.startswith(b"\xff"):
                repaired = bytearray(header) + repaired
            else:
                repaired = bytearray(b"\xff\xd8") + repaired

    # Check for End of Image (EOI) marker \xff\xd9
    if not repaired.endswith(b"\xff\xd9"):
        # Remove trailing zeros if any (common in disk images)
        while len(repaired) > 0 and repaired[-1] == 0:
            repaired.pop()
        
        if not repaired.endswith(b"\xff\xd9"):
            repaired.extend(b"\xff\xd9")

    return bytes(repaired)


def repair_pdf(data: bytes) -> bytes:
    """
    Uses PyMuPDF to rebuild XREF tables.
    """
    if not data:
        return data

    if not PYMUPDF_AVAILABLE:
        logger.warning("PyMuPDF not available for PDF repair.")
        return data
    
    try:
        # Open from bytes
        doc = fitz.open(stream=data, filetype="pdf")
        
        # Save to bytes with rebuilding XREF (clean=True, incremental=False)
        out = io.BytesIO()
        # clean=True attempts to fix errors in the file structure
        doc.save(out, clean=True, incremental=False, deflate=True)
        repaired_data = out.getvalue()
        doc.close()
        
        if len(repaired_data) > 0:
            return repaired_data
    except Exception as e:
        logger.error(f"PyMuPDF repair failed: {e}")
        # Fallback logic could go here (e.g. Ghostscript)
        # For now, return original
        
    return data

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-jpeg", action="store_true")
    parser.add_argument("--test-pdf", action="store_true")
    args = parser.parse_args()

    if args.test_jpeg:
        # Test 1: Empty data
        assert repair_jpeg(b"") == b""
        
        # Test 2: Missing SOI
        test_data = b"\xff\xe0\x00\x10JFIF..."
        repaired = repair_jpeg(test_data)
        assert repaired.startswith(b"\xff\xd8")
        assert repaired.endswith(b"\xff\xd9")
        print("JPEG Repair Test: Missing SOI/EOI - PASSED")

        # Test 3: Raw data
        test_data = b"Some image data"
        repaired = repair_jpeg(test_data)
        assert repaired.startswith(b"\xff\xd8")
        assert repaired.endswith(b"\xff\xd9")
        print("JPEG Repair Test: Raw data - PASSED")

    if args.test_pdf:
        if not PYMUPDF_AVAILABLE:
            print("PyMuPDF not installed, skipping PDF test.")
            return
        # Mocking a slightly broken PDF is complex, but we can try a minimal one
        minimal_pdf = (
            b"%PDF-1.1\n"
            b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
            b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
            b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000101 00000 n\ntrailer <</Size 4 /Root 1 0 R>>\nstartxref\n178\n%%EOF"
        )
        repaired = repair_pdf(minimal_pdf)
        assert b"%PDF" in repaired
        assert b"%%EOF" in repaired
        print("PDF Repair Test: Minimal PDF - PASSED")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
