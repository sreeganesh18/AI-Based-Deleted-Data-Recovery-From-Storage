import os
import mmap
from typing import Generator, Tuple, Optional


class DiskScanner:
    """
    Scans a raw storage media at sector/block level.
    Uses mmap for efficient random access to large images.
    Operates in a strictly read-only mode.
    """

    def __init__(self, disk_image_path: str, block_size: int = 512):
        self.disk_image_path = disk_image_path
        self.block_size = block_size
        self.cluster_size: int = block_size  # Default: 1 block per cluster
        self.data_offset: int = 0             # Offset to data area (sectors)
        
        if not os.path.exists(disk_image_path):
            raise FileNotFoundError(f"Storage image not found: {disk_image_path}")
        
        self.file_size = os.path.getsize(disk_image_path)
        self._file_obj = open(self.disk_image_path, "rb")
        self.mm: Optional[mmap.mmap] = None
        
        try:
            # Create a read-only memory map
            self.mm = mmap.mmap(self._file_obj.fileno(), 0, access=mmap.ACCESS_READ)
        except (OSError, ValueError):
            # Fallback if mmap fails (e.g., zero-length file or OS constraints)
            self.mm = None

    def close(self) -> None:
        """Closes the memory map and file handle."""
        if self.mm:
            self.mm.close()
        self._file_obj.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def read_block(self, block_index: int) -> bytes:
        """Reads a specific block from the image."""
        offset = block_index * self.block_size
        if offset >= self.file_size:
            return b""
        
        if self.mm:
            return self.mm[offset : offset + self.block_size]
        else:
            self._file_obj.seek(offset)
            return self._file_obj.read(self.block_size)

    def scan_blocks(self) -> Generator[Tuple[int, bytes], None, None]:
        """
        Reads the disk image sector by sector and yields 512-byte blocks.
        """
        num_blocks = self.file_size // self.block_size
        for i in range(num_blocks):
            yield i * self.block_size, self.read_block(i)

    def set_filesystem_info(self, cluster_size: int, data_offset: int) -> None:
        """Configures file system specific parameters for mapping."""
        self.cluster_size = cluster_size
        self.data_offset = data_offset

    def cluster_to_sector(self, cluster_index: int) -> int:
        """Translates a cluster index to its starting sector offset."""
        # clusters are relative to data_offset
        # returns byte offset
        cluster_bytes = cluster_index * self.cluster_size
        return self.data_offset + cluster_bytes
