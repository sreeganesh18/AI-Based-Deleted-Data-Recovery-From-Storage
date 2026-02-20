from storage_scan.scanner import DiskScanner


def test_scanner_initialization(dummy_disk_image):
    scanner = DiskScanner(dummy_disk_image, block_size=512)
    assert scanner.disk_image_path == dummy_disk_image
    assert scanner.block_size == 512


def test_scanner_blocks(dummy_disk_image):
    scanner = DiskScanner(dummy_disk_image, block_size=512)
    blocks = list(scanner.scan_blocks())

    # 1000 + 20 + 800 + 2 + 1000 = 2822 bytes total
    # 2822 / 512 = 5 blocks completely filled, 6th block partially filled
    assert len(blocks) == 6

    # Check that all except the last block are 512 bytes
    for i in range(5):
        assert len(blocks[i][1]) == 512

    # Last block size
    assert len(blocks[5][1]) == 2822 % 512
