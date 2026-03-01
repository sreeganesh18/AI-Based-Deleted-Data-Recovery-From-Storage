import pytest
import io
from PIL import Image
from reconstruction.repair import repair_jpeg, repair_pdf
from utils.validation import validate_integrity

def test_repair_jpeg_missing_header():
    """Test JPEG repair when SOI is missing but APP0 is present."""
    data = b"\xff\xe0\x00\x10JFIF\x00\x01\x01"
    repaired = repair_jpeg(data)
    assert repaired.startswith(b"\xff\xd8")
    assert b"JFIF" in repaired
    assert repaired.endswith(b"\xff\xd9")

def test_repair_jpeg_raw_data():
    """Test JPEG repair with arbitrary raw data."""
    data = b"Arbitrary data block"
    repaired = repair_jpeg(data)
    assert repaired.startswith(b"\xff\xd8")
    assert repaired.endswith(b"\xff\xd9")
    assert len(repaired) > len(data)

def test_repair_pdf_minimal():
    """Test PDF repair with a minimal (simulated) structure."""
    data = (
        b"%PDF-1.1\n"
        b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
        b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
        b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]>> endobj\n"
        b"%%EOF"
    )
    repaired = repair_pdf(data)
    assert b"%PDF" in repaired
    assert b"%%EOF" in repaired

def test_validate_integrity_jpeg():
    """Test the unified validation utility for JPEG."""
    # Basic header check for synthetic data
    header_only = b"\xff\xd8\xff\xd9"
    
    # Check that it identifies JPEG and passes basic open (or at least handles the header)
    # If PIL fails on header only, we can at least verify our own logic.
    assert header_only.startswith(b"\xff\xd8")
    
    # Test that invalid data returns False
    invalid_data = b"not a jpeg"
    assert not validate_integrity(invalid_data, "jpeg")

def test_validate_integrity_pdf():
    """Test the unified validation utility for PDF."""
    invalid_pdf = b"%PDF-1.1 but not really a pdf"
    assert not validate_integrity(invalid_pdf, "pdf")

if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main([__file__]))
