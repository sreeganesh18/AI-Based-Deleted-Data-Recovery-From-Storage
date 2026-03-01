import pytest
import os
from reconstruction.grouping import FragmentGrouper
from reconstruction.repair import repair_jpeg, repair_pdf, PYMUPDF_AVAILABLE


def test_grouping_basic():
    """Test basic grouping without fragmentation or gaps."""
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"HEADER" + b"\x00"*506,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 512,
            'data': b"DATA" + b"\x00"*508,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert results[0]['type'] == 'jpeg'
    assert len(results[0]['data']) == 1024
    assert results[0]['data'].startswith(b"HEADER")


def test_grouping_with_gaps():
    """Test that gaps are zero-filled."""
    grouper = FragmentGrouper()
    
    fragments = [
        {
            'offset': 0,
            'data': b"H" * 512,
            'identification': {'type': 'jpeg', 'source': 'signature'}
        },
        {
            'offset': 1024, # Gap of 512 bytes at 512
            'data': b"D" * 512,
            'identification': {'type': 'jpeg', 'source': 'ai'}
        }
    ]
    
    results = grouper.group_fragments(fragments)
    assert len(results) == 1
    assert len(results[0]['data']) == 1536
    # Check gap is zero-filled
    assert results[0]['data'][512:1024] == b"\x00" * 512
    # Check data after gap is present
    assert results[0]['data'][1024:] == b"D" * 512


def test_repair_jpeg_valid():
    """Tests repair_jpeg with valid data."""
    # Valid 1x1 black JPEG in hex
    jpeg_hex = (
        "ffd8ffe000104a46494600010101006000600000ffdb00430008060607060508070707"
        "0909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c"
        "2837292c30313434341f27393d38323c2e333432ffc0001108000100010301220002"
        "1101031101ffc40015000101000000000000000000000000000008ffc40014100100"
        "00000000000000000000000000000000ffda000c03010002110311003f00140affd9"
    )
    data = bytes.fromhex(jpeg_hex)
    repaired = repair_jpeg(data)
    assert repaired == data
    assert repaired.startswith(b"\xff\xd8")
    assert repaired.endswith(b"\xff\xd9")


def test_repair_jpeg_missing_soi():
    """Tests repair_jpeg adding a missing SOI."""
    data = b"\xff\xe0\x00\x10JFIF" + b"\x00" * 10 + b"\xff\xd9"
    repaired = repair_jpeg(data)
    assert repaired.startswith(b"\xff\xd8")
    assert repaired.endswith(b"\xff\xd9")
    assert b"JFIF" in repaired


def test_repair_jpeg_missing_eoi():
    """Tests repair_jpeg adding a missing EOI."""
    data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 10
    repaired = repair_jpeg(data)
    assert repaired.startswith(b"\xff\xd8")
    assert repaired.endswith(b"\xff\xd9")


def test_repair_jpeg_with_trailing_zeros():
    """Tests repair_jpeg removing trailing zeros before adding EOI."""
    data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 10 + b"\xff\xd9" + b"\x00" * 5
    # The current implementation of repair_jpeg ONLY removes trailing zeros if EOI is NOT present at the very end.
    # Wait, let's check repair.py again.
    # if not repaired.endswith(b"\xff\xd9"):
    #     while len(repaired) > 0 and repaired[-1] == 0:
    #         repaired.pop()
    #     if not repaired.endswith(b"\xff\xd9"):
    #         repaired.extend(b"\xff\xd9")
    
    # In my case, it doesn't end with \xff\xd9 because of trailing zeros.
    # So it should remove them and then see it ends with \xff\xd9.
    
    repaired = repair_jpeg(data)
    assert repaired.endswith(b"\xff\xd9")
    assert not repaired.endswith(b"\x00")


@pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF not installed")
def test_repair_pdf_basic():
    """Tests basic repair_pdf."""
    # Minimal valid PDF
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
