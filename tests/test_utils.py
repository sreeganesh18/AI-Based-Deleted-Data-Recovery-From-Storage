import os
import json
import pytest
import torch
import numpy as np
import hashlib
from utils.metadata import MetadataManager
from utils.validation import (
    calculate_md5,
    check_file_integrity,
    validate_integrity,
    assign_confidence_score,
    calculate_psnr,
    calculate_ssim
)
from utils.reporting import (
    generate_carving_summary,
    get_visual_comparison,
    save_visual_report
)


@pytest.fixture
def temp_metadata_path(tmp_path):
    return str(tmp_path / "metadata.json")


def test_metadata_manager_initialization(temp_metadata_path):
    manager = MetadataManager(temp_metadata_path)
    assert manager.metadata_path == temp_metadata_path
    assert "fragments" in manager.data
    assert "original_files" in manager.data
    assert "reconstructed_files" in manager.data


def test_metadata_manager_save_load(temp_metadata_path):
    manager = MetadataManager(temp_metadata_path)
    fragment_id = "frag_001"
    metadata = {"offset": 1024, "size": 512, "type": "jpeg"}
    manager.add_fragment(fragment_id, metadata)

    # Verify saving
    assert os.path.exists(temp_metadata_path)

    # New manager instance to test loading
    new_manager = MetadataManager(temp_metadata_path)
    loaded_metadata = new_manager.get_fragment(fragment_id)
    assert loaded_metadata == metadata


def test_metadata_manager_list_fragments(temp_metadata_path):
    manager = MetadataManager(temp_metadata_path)
    manager.add_fragment("f1", {})
    manager.add_fragment("f2", {})
    fragments = manager.list_fragments()
    assert "f1" in fragments
    assert "f2" in fragments
    assert len(fragments) == 2


def test_calculate_md5():
    data = b"hello world"
    expected = hashlib.md5(data).hexdigest()
    assert calculate_md5(data) == expected


def test_validate_integrity_jpeg():
    # Valid 1x1 black JPEG in hex
    jpeg_hex = (
        "ffd8ffe000104a46494600010101006000600000ffdb00430008060607060508070707"
        "0909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c1c"
        "2837292c30313434341f27393d38323c2e333432ffc0001108000100010301220002"
        "1101031101ffc40015000101000000000000000000000000000008ffc40014100100"
        "00000000000000000000000000000000ffda000c03010002110311003f00140affd9"
    )
    jpeg_data = bytes.fromhex(jpeg_hex)
    assert validate_integrity(jpeg_data, "jpeg") is True
    assert validate_integrity(jpeg_data) is True # Auto-detect


def test_validate_integrity_invalid():
    assert validate_integrity(b"not a file", "jpeg") is False
    assert validate_integrity(None) is False
    assert validate_integrity(b"") is False


def test_assign_confidence_score():
    # Data with JPEG header
    jpeg_header_only = b"\xff\xd8" + b"A" * 100
    # This won't pass PIL's verify, so score should be low
    score = assign_confidence_score(jpeg_header_only)
    assert score == 15.0 # Just header


def test_calculate_psnr():
    original = torch.ones((1, 1, 512))
    reconstructed = torch.ones((1, 1, 512))
    # Perfect match should have high PSNR
    val = calculate_psnr(original, reconstructed)
    assert val > 40


def test_calculate_ssim():
    original = torch.ones((1, 1, 512))
    reconstructed = torch.ones((1, 1, 512))
    # Perfect match should have SSIM = 1.0
    val = calculate_ssim(original, reconstructed)
    assert pytest.approx(val, 0.01) == 1.0


def test_calculate_ssim_batch():
    original = torch.ones((2, 1, 512))
    reconstructed = torch.ones((2, 1, 512))
    val = calculate_ssim(original, reconstructed)
    assert pytest.approx(val, 0.01) == 1.0


def test_generate_carving_summary():
    results = [
        {"offset": 0, "identification": {"type": "jpeg", "source": "signature"}},
        {"offset": 512, "identification": {"type": "jpeg", "source": "ai"}},
        {"offset": 1024, "identification": {"type": "other", "source": "ai_low_confidence"}},
        {"offset": 1536, "identification": {"type": "pdf", "source": "signature"}}
    ]
    summary = generate_carving_summary(results)
    assert summary["total_fragments"] == 4
    assert summary["jpeg"]["total"] == 2
    assert summary["jpeg"]["signature"] == 1
    assert summary["jpeg"]["ai"] == 1
    assert summary["pdf"]["total"] == 1
    assert summary["other"] == 1


def test_get_visual_comparison():
    orig = b"\x00" * 512
    denoised = b"\xff" * 512
    orig_np, denoised_np = get_visual_comparison(orig, denoised)
    assert orig_np.shape == (512,)
    assert denoised_np.shape == (512,)
    assert np.all(orig_np == 0.0)
    assert np.all(denoised_np == 1.0)


def test_save_visual_report(tmp_path):
    orig = np.zeros((10, 10, 3), dtype=np.uint8)
    denoised = np.zeros((10, 10, 3), dtype=np.uint8)
    enhanced = np.zeros((20, 20, 3), dtype=np.uint8)
    report_path = str(tmp_path / "report.html")
    
    save_visual_report(orig, denoised, enhanced, report_path, {"PSNR": 30.0})
    
    assert os.path.exists(report_path)
    # Check if comparison image exists
    img_filename = "report.html.comparison.jpg"
    img_path = os.path.join(str(tmp_path), img_filename)
    assert os.path.exists(img_path)
