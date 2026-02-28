import struct
from storage_scan.scanner import DiskScanner
from typing import Dict, Any


class NTFSParser:
    """
    Parses NTFS boot sector to find key file system locations.
    Specifically targets the $MFT location and cluster size.
    """

    def __init__(self, scanner: DiskScanner):
        self.scanner = scanner
        self.sector_size: int = 512
        self.cluster_size: int = 4096
        self.mft_cluster: int = 0
        self.mft_offset: int = 0

    def parse_boot_sector(self, sector_data: bytes) -> Dict[str, Any]:
        """
        Parses the first 512 bytes of an NTFS partition.
        Expects sector_data to be at least 512 bytes.
        """
        if len(sector_data) < 512:
            return {"error": "Insufficient data"}

        # OEM ID should be "NTFS    "
        oem_id = sector_data[3:11].decode('ascii', errors='ignore')
        if "NTFS" not in oem_id:
            return {"error": f"Invalid NTFS OEM ID: {oem_id}"}

        # Bytes Per Sector (Offset 0x0B, 2 bytes)
        self.sector_size = struct.unpack("<H", sector_data[0x0B:0x0D])[0]
        # Sectors Per Cluster (Offset 0x0D, 1 byte)
        sectors_per_cluster = struct.unpack("B", sector_data[0x0D:0x0E])[0]
        self.cluster_size = self.sector_size * sectors_per_cluster

        # Logical Cluster Number for the File $MFT (Offset 0x30, 8 bytes)
        self.mft_cluster = struct.unpack("<Q", sector_data[0x30:0x38])[0]
        self.mft_offset = self.mft_cluster * self.cluster_size

        return {
            "oem_id": oem_id,
            "sector_size": self.sector_size,
            "cluster_size": self.cluster_size,
            "mft_cluster": self.mft_cluster,
            "mft_offset": self.mft_offset
        }
