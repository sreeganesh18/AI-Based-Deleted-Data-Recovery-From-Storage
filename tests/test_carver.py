from carving.signature import SignatureCarver
from storage_scan.scanner import DiskScanner


def test_signature_carving(dummy_disk_image):
    scanner = DiskScanner(dummy_disk_image, block_size=512)
    carver = SignatureCarver(block_size=512)

    for offset, block in scanner.scan_blocks():
        carver.process_block(offset, block)

    carved_files = carver.get_carved_files()

    assert len(carved_files) == 1

    carved_data = carved_files[0]["data"]
    assert carved_data.startswith(b"\xff\xd8")
    assert carved_data.endswith(b"\xff\xd9")
    assert len(carved_data) == 16 + 800 + 2  # Header + Body + Footer
