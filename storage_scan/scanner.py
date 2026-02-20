import os
from typing import Generator, Tuple


class DiskScanner:
    """
    Scans a raw storage media at sector/block level.
    Operates in a strictly read-only mode.
    """

    def __init__(self, disk_image_path: str, block_size: int = 512):
        self.disk_image_path = disk_image_path
        self.block_size = block_size
        if not os.path.exists(disk_image_path):
            raise FileNotFoundError(f"Storage image not found: {disk_image_path}")

    def scan_blocks(self) -> Generator[Tuple[int, bytes], None, None]:
        """
        Reads the disk image sector by sector and yields 512-byte blocks.
        """
        with open(self.disk_image_path, "rb") as f:
            offset = 0
            while True:
                block = f.read(self.block_size)
                if not block:
                    break
                yield offset, block
                offset += self.block_size
