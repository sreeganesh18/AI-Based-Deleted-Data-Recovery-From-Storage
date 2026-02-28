import pytest
from carving.ntfs import NTFSParser
from carving.fat32 import FAT32Parser
from carving.signature import SignatureCarver
from storage_scan.scanner import DiskScanner


def test_signature_carving(dummy_disk_image):
    """Verifies existing signature carver functionality."""
    with DiskScanner(dummy_disk_image, block_size=512) as scanner:
        carver = SignatureCarver(block_size=512)
        for offset, block in scanner.scan_blocks():
            carver.process_block(offset, block)
            
        carved_files = carver.get_carved_files()
        assert len(carved_files) == 1
        carved_data = carved_files[0]["data"]
        assert carved_data.startswith(b"\xff\xd8")
        assert carved_data.endswith(b"\xff\xd9")


def test_ntfs_parser():
    """Verifies NTFS boot sector parsing with mock data."""
    # Create a minimal NTFS boot sector mock (512 bytes)
    boot_sector = bytearray(512)
    boot_sector[3:11] = b"NTFS    "  # OEM ID
    boot_sector[0x0B:0x0D] = (512).to_bytes(2, "little")  # 512 Bytes Per Sector
    boot_sector[0x0D] = 8  # 8 Sectors Per Cluster (8 * 512 = 4096 bytes)
    boot_sector[0x30:0x38] = (100).to_bytes(8, "little")  # MFT starts at cluster 100
    
    # We don't need a real scanner for this unit test
    parser = NTFSParser(scanner=None)
    result = parser.parse_boot_sector(boot_sector)
    
    assert result["oem_id"] == "NTFS    "
    assert result["sector_size"] == 512
    assert result["cluster_size"] == 4096
    assert result["mft_cluster"] == 100
    assert result["mft_offset"] == 100 * 4096


def test_fat32_parser():
    """Verifies FAT32 BPB parsing with mock data."""
    # Create a minimal FAT32 boot sector mock (512 bytes)
    boot_sector = bytearray(512)
    boot_sector[3:11] = b"MSDOS5.0"  # Example OEM ID
    boot_sector[0x0B:0x0D] = (512).to_bytes(2, "little")  # 512 Bytes Per Sector
    boot_sector[0x0D] = 8  # 8 Sectors Per Cluster
    boot_sector[0x0E:0x10] = (32).to_bytes(2, "little")  # 32 Reserved Sectors
    boot_sector[0x10] = 2  # 2 FATs
    boot_sector[0x24:0x28] = (1024).to_bytes(4, "little")  # 1024 Sectors per FAT
    
    parser = FAT32Parser(scanner=None)
    result = parser.parse_boot_sector(boot_sector)
    
    assert result["sector_size"] == 512
    assert result["cluster_size"] == 4096
    assert result["fat_offset"] == 32 * 512
    # data_offset = (reserved + (num_fats * sectors_per_fat)) * sector_size
    # data_offset = (32 + (2 * 1024)) * 512 = 2080 * 512 = 1,064,960
    assert result["data_offset"] == 1064960
