import os
import json
import pytest
import shutil
from utils.metadata import MetadataManager

TEST_METADATA_PATH = "tests/test_metadata.json"


@pytest.fixture
def manager():
    """Provides a MetadataManager for tests, cleaning up after each use."""
    if os.path.exists(TEST_METADATA_PATH):
        os.remove(TEST_METADATA_PATH)
    
    manager = MetadataManager(metadata_path=TEST_METADATA_PATH)
    yield manager
    
    if os.path.exists(TEST_METADATA_PATH):
        os.remove(TEST_METADATA_PATH)


def test_add_fragment(manager):
    """Verifies fragment metadata can be added and retrieved."""
    fragment_id = "frag-001"
    metadata = {"offset": 1024, "size": 512, "type": "JPEG"}
    
    manager.add_fragment(fragment_id, metadata)
    retrieved = manager.get_fragment(fragment_id)
    
    assert retrieved == metadata
    assert fragment_id in manager.list_fragments()


def test_save_load(manager):
    """Verifies that metadata is correctly saved to and loaded from disk."""
    fragment_id = "frag-002"
    metadata = {"offset": 2048, "size": 1024, "type": "PDF"}
    
    manager.add_fragment(fragment_id, metadata)
    manager.save()
    
    # Create a new manager instance and load from the same path
    new_manager = MetadataManager(metadata_path=TEST_METADATA_PATH)
    new_manager.load()
    
    assert new_manager.get_fragment(fragment_id) == metadata


def test_add_original_file(manager):
    """Verifies original file metadata can be added."""
    file_path = "dataset/original/test.jpg"
    metadata = {"size": 50000, "checksum": "abc12345"}
    
    manager.add_original_file(file_path, metadata)
    assert manager.data["original_files"][file_path] == metadata


def test_add_reconstructed_file(manager):
    """Verifies reconstructed file metadata can be added."""
    file_path = "dataset/reconstructed/rec_test.jpg"
    metadata = {"success": True, "confidence": 0.95}
    
    manager.add_reconstructed_file(file_path, metadata)
    assert manager.data["reconstructed_files"][file_path] == metadata
