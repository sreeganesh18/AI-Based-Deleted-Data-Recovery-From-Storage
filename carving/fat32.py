import struct
from storage_scan.scanner import DiskScanner
from typing import Dict, Any


class FAT32Parser:
    """
    Parses FAT32 boot sector to find key file system locations.
    Specifically targets the FAT location and cluster size.
    """

    def __init__(self, scanner: DiskScanner):
        self.scanner = scanner
        self.sector_size: int = 512
        self.cluster_size: int = 4096
        self.fat_offset: int = 0
        self.data_offset: int = 0

    def parse_boot_sector(self, sector_data: bytes) -> Dict[str, Any]:
        """
        Parses the BIOS Parameter Block (BPB) of a FAT32 partition.
        Expects sector_data to be at least 512 bytes.
        """
        if len(sector_data) < 512:
            return {"error": "Insufficient data"}

        # OEM ID (Offset 0x03, 8 bytes)
        oem_id = sector_data[3:11].decode('ascii', errors='ignore')

        # Bytes Per Sector (Offset 0x0B, 2 bytes)
        self.sector_size = struct.unpack("<H", sector_data[0x0B:0x0D])[0]
        # Sectors Per Cluster (Offset 0x0D, 1 byte)
        sectors_per_cluster = struct.unpack("B", sector_data[0x0D:0x0E])[0]
        self.cluster_size = self.sector_size * sectors_per_cluster

        # Reserved Sectors (Offset 0x0E, 2 bytes)
        reserved_sectors = struct.unpack("<H", sector_data[0x0E:0x10])[0]
        # Number of FATs (Offset 0x10, 1 byte)
        num_fats = struct.unpack("B", sector_data[0x10:0x11])[0]
        # Sectors Per FAT (Offset 0x24, 4 bytes for FAT32)
        sectors_per_fat = struct.unpack("<I", sector_data[0x24:0x28])[0]

        # Calculate FAT and Data offsets
        self.fat_offset = reserved_sectors * self.sector_size
        self.data_offset = (reserved_sectors + (num_fats * sectors_per_fat)) * self.sector_size

        return {
            "oem_id": oem_id,
            "sector_size": self.sector_size,
            "cluster_size": self.cluster_size,
            "fat_offset": self.fat_offset,
            "data_offset": self.data_offset
        }
