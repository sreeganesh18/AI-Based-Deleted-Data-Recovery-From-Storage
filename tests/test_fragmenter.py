import os
import shutil
import pytest
from dataset.fragmenter import Fragmenter

TEST_SRC_DIR = "tests/test_sources"
TEST_DST_DIR = "tests/test_output_fragments"


@pytest.fixture
def setup_dirs():
    """Setup and teardown for fragmenter tests."""
    if os.path.exists(TEST_SRC_DIR):
        shutil.rmtree(TEST_SRC_DIR)
    if os.path.exists(TEST_DST_DIR):
        shutil.rmtree(TEST_DST_DIR)
        
    os.makedirs(os.path.join(TEST_SRC_DIR, "jpeg"), exist_ok=True)
    yield
    
    if os.path.exists(TEST_SRC_DIR):
        shutil.rmtree(TEST_SRC_DIR)
    if os.path.exists(TEST_DST_DIR):
        shutil.rmtree(TEST_DST_DIR)


def test_fragment_file(setup_dirs):
    """Verifies that a file is correctly split into padded blocks."""
    fragmenter = Fragmenter(block_size=512)
    test_file = os.path.join(TEST_SRC_DIR, "jpeg", "test.jpg")
    
    # 512 + 100 bytes = 612 bytes total -> 2 fragments expected
    with open(test_file, "wb") as f:
        f.write(b"A" * 512 + b"B" * 100)
        
    count = fragmenter.fragment_file(test_file, TEST_DST_DIR)
    
    assert count == 2
    # Verify fragment contents
    frag0 = os.path.join(TEST_DST_DIR, "test.jpg_frag0000.bin")
    frag1 = os.path.join(TEST_DST_DIR, "test.jpg_frag0001.bin")
    
    assert os.path.exists(frag0)
    assert os.path.exists(frag1)
    
    with open(frag0, "rb") as f:
        assert f.read() == b"A" * 512
        
    with open(frag1, "rb") as f:
        data = f.read()
        assert data.startswith(b"B" * 100)
        assert data.endswith(b"\x00" * 412)  # Padded
