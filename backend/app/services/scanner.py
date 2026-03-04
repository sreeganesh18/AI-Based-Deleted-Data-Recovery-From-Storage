from storage_scan.scanner import DiskScanner
from typing import List, Tuple


class BlockScanner:
    """
    Scans forensic disk images and extracts file fragments.
    """

    def __init__(self, block_size: int = 4096):
        self.block_size = block_size

    def scan_image(self, file_path: str) -> List[Tuple[int, bytes]]:
        """
        Scans a disk image and returns tuples of (offset, data).
        Uses DiskScanner for efficient reading.
        """
        with DiskScanner(file_path, block_size=self.block_size) as scanner:
            return list(scanner.scan_blocks())
