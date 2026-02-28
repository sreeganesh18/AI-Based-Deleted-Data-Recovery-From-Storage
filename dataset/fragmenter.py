import os
from typing import List, Dict


class Fragmenter:
    """
    Utility to split source files (JPEG/PDF) into 512-byte blocks.
    Organizes fragments into subdirectories based on file type.
    """

    def __init__(self, block_size: int = 512):
        self.block_size = block_size

    def fragment_file(self, file_path: str, dest_dir: str) -> int:
        """
        Splits a single file into blocks and saves them to dest_dir.
        Returns the number of fragments created.
        """
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
            
        base_name = os.path.basename(file_path)
        fragments_count = 0
        
        with open(file_path, "rb") as f:
            while True:
                data = f.read(self.block_size)
                if not data:
                    break
                    
                # Pad the last block if it's shorter than block_size
                if len(data) < self.block_size:
                    data = data.ljust(self.block_size, b"\x00")
                
                frag_name = f"{base_name}_frag{fragments_count:04d}.bin"
                frag_path = os.path.join(dest_dir, frag_name)
                
                with open(frag_path, "wb") as frag_f:
                    frag_f.write(data)
                
                fragments_count += 1
                
        return fragments_count

    def fragment_directory(self, source_root: str, dest_root: str, file_types: List[str] = ["jpeg", "pdf"]) -> Dict[str, int]:
        """
        Fragments all files in source_root/[type] and saves to dest_root/[type].
        Returns a summary of fragments created per type.
        """
        summary = {}
        for ftype in file_types:
            src_type_dir = os.path.join(source_root, ftype)
            dest_type_dir = os.path.join(dest_root, ftype)
            
            if not os.path.isdir(src_type_dir):
                continue
                
            count = 0
            for filename in os.listdir(src_type_dir):
                # Simple extension check or just take all files in the type dir
                file_path = os.path.join(src_type_dir, filename)
                if os.path.isfile(file_path):
                    count += self.fragment_file(file_path, dest_type_dir)
            
            summary[ftype] = count
            
        return summary
