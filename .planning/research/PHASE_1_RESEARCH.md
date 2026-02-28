# RESEARCH: Phase 1 - Foundation & Data Management

## Dataset Management
- **Structure:**
  - `dataset/fragments/`: Stores extracted or generated file fragments for training/testing.
  - `dataset/original/`: Stores original source files for creating fragments.
  - `dataset/reconstructed/`: Stores files recovered by the system.
- **Metadata:** A `metadata.json` or SQLite database should track fragment origins, types, and corruption levels.

## Storage Scanning (Python)
- **Methods:**
  - `open(image, 'rb')`: Basic binary read.
  - `mmap`: Memory-mapped file access for faster random access to large images.
  - `struct`: For parsing binary structures (Boot Sectors, MFT records).
- **Libraries:**
  - `pytsk3`: Python bindings for The Sleuth Kit (TSK). High-level FS analysis.
  - `bitarray`: For managing cluster/sector bitmaps efficiently.

## File System Parsing (NTFS/FAT32)
- **NTFS:**
  - Locate `$Boot` to find the `$MFT` location.
  - Parse `$MFT` records to identify allocated/unallocated clusters.
- **FAT32:**
  - Parse the BIOS Parameter Block (BPB) in the Boot Sector.
  - Traverse the File Allocation Table (FAT) to identify free clusters.

## Implementation Strategy
1. **Environment:** Use `uv` for dependency management.
2. **Scanner:** Implement a class that abstracts raw access and sector-to-cluster mapping.
3. **Carver Base:** Focus on identifying unallocated space as the primary source for carving.
