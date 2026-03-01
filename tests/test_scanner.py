import pytest
import os
import math
from storage_scan.scanner import DiskScanner


def test_scanner_initialization(dummy_disk_image):
    """Verifies scanner initializes correctly and uses mmap."""
    scanner = DiskScanner(dummy_disk_image, block_size=512)
    assert scanner.disk_image_path == str(dummy_disk_image)
    assert scanner.block_size == 512
    # Check that mmap object exists (unless OS/file constraints)
    assert scanner.mm is not None
    scanner.close()


def test_scanner_read_block(dummy_disk_image):
    """Tests random access block reading."""
    with DiskScanner(dummy_disk_image, block_size=512) as scanner:
        # Read first block
        block = scanner.read_block(0)
        assert len(block) == 512
        # The dummy image starts with 1000 bytes of random garbage (os.urandom)
        # So we just check that we got 512 bytes
        
        # Read second block
        block = scanner.read_block(1)
        assert len(block) == 512
        
        # The JPEG header starts at offset 1000.
        # This is in the middle of block 1 (offset 512 to 1024).
        # Offset 1000 in image is offset (1000 - 512) = 488 in block 1.
        assert block[488:492] == b"\xff\xd8\xff\xe0"


def test_scanner_blocks(dummy_disk_image):
    """Verifies that scanning yields blocks correctly."""
    with DiskScanner(dummy_disk_image, block_size=512) as scanner:
        blocks = list(scanner.scan_blocks())
        # Size = 1000 (garbage) + 20 (JPEG head) + 800 (random) + 2 (JPEG foot) + 1000 (garbage) = 2822
        # 2822 // 512 = 5 full blocks
        assert len(blocks) == 5

        # Check block sizes
        for offset, data in blocks:
            assert len(data) == 512


def test_cluster_mapping(dummy_disk_image):
    """Tests cluster-to-sector mapping."""
    with DiskScanner(dummy_disk_image, block_size=4096) as scanner:
        # 1 cluster = 4096 bytes, data starts at offset 8192
        scanner.set_filesystem_info(cluster_size=4096, data_offset=8192)
        
        # Cluster 0 starts at data_offset
        assert scanner.cluster_to_sector(0) == 8192
        # Cluster 1 starts at data_offset + cluster_size
        assert scanner.cluster_to_sector(1) == 8192 + 4096


def test_entropy_calculation():
    """Verifies Shannon entropy calculation."""
    # Low entropy: all zeros
    data_zeros = b"\x00" * 100
    assert DiskScanner.calculate_entropy(data_zeros) == 0.0
    
    # High entropy: all 256 bytes present equally
    data_full = bytes(range(256))
    assert math.isclose(DiskScanner.calculate_entropy(data_full), 8.0)
    
    # Medium entropy: half 'A', half 'B'
    data_half = b"A" * 50 + b"B" * 50
    # p('A') = 0.5, p('B') = 0.5
    # entropy = -(0.5 * log2(0.5) + 0.5 * log2(0.5)) = -(0.5 * -1 + 0.5 * -1) = 1.0
    assert math.isclose(DiskScanner.calculate_entropy(data_half), 1.0)
    
    # Empty data
    assert DiskScanner.calculate_entropy(b"") == 0.0


def test_scanner_boundary_handling(tmp_path):
    """Tests how scanner handles small files and out-of-bounds reads."""
    # Create a small file (5 bytes)
    small_file = tmp_path / "small.dd"
    small_file.write_bytes(b"HELLO")
    
    with DiskScanner(str(small_file), block_size=512) as scanner:
        # Out of bounds
        assert scanner.read_block(1) == b""
        
        # Partial block read at the end
        # Since it's < 512, read_block(0) should return all 5 bytes if mmap is used
        block = scanner.read_block(0)
        assert block == b"HELLO"
        
        # Scan blocks should return 0 blocks since file_size // block_size is 0
        blocks = list(scanner.scan_blocks())
        assert len(blocks) == 0


def test_scanner_missing_file():
    """Ensures FileNotFoundError is raised for missing images."""
    with pytest.raises(FileNotFoundError):
        DiskScanner("non_existent_file.dd")
