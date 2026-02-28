import os
import torch
import pytest
import shutil
from dataset.loader import FragmentDataset

TEST_DATA_DIR = "tests/test_fragments"


@pytest.fixture
def dummy_dataset():
    """Provides a dummy dataset with some JPEG and PDF fragments."""
    # Setup
    os.makedirs(os.path.join(TEST_DATA_DIR, "jpeg"), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, "pdf"), exist_ok=True)
    
    # Write dummy JPEG fragment
    with open(os.path.join(TEST_DATA_DIR, "jpeg", "test1.bin"), "wb") as f:
        f.write(b"\xff\xd8" + b"\x00" * 510)
        
    # Write dummy PDF fragment
    with open(os.path.join(TEST_DATA_DIR, "pdf", "test2.bin"), "wb") as f:
        f.write(b"%PDF-1.4" + b"\x00" * 504)
        
    dataset = FragmentDataset(root_dir=TEST_DATA_DIR, labels=["jpeg", "pdf", "other"])
    yield dataset
    
    # Teardown
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)


def test_dataset_len(dummy_dataset):
    """Verifies dataset correctly discovers samples."""
    assert len(dummy_dataset) == 2


def test_dataset_getitem(dummy_dataset):
    """Verifies data loading and normalization."""
    # Test first sample (JPEG)
    tensor, label = dummy_dataset[0]
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (1, 512)
    assert label == 0  # jpeg index
    assert torch.all(tensor >= 0.0) and torch.all(tensor <= 1.0)
    assert tensor[0, 0] == pytest.approx(255/255.0)  # \xff
    assert tensor[0, 1] == pytest.approx(216/255.0)  # \xd8
