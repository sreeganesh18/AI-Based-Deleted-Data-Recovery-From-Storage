from reconstruction.autoencoder import ReassemblyAutoencoder
from reconstruction.grouping import FragmentGrouper
from .fragment_classifier import FragmentClassifier
from typing import List, Dict


class ReassemblyEngine:
    """
    Fragment Reassembly Engine for reconstructing files.
    Utilizes Graph algorithms, LSTM semantic adjacency, and Genetic Search.
    Connected to reconstruction/autoencoder.py for advanced AI-powered data reconstruction.
    """

    def __init__(self, autoencoder_model_path: str = None, classifier_model_path: str = None):
        self.autoencoder = ReassemblyAutoencoder(model_path=autoencoder_model_path)
        
        # Initialize classifier and pass its underlying model to the grouper
        self.classifier_service = FragmentClassifier(model_path=classifier_model_path)
        self.grouper = FragmentGrouper(classifier=self.classifier_service.model)

    def sequence_fragments(self, fragments: List[Dict]) -> List[Dict]:
        """
        Analyzes a list of fragments and sequences them using adjacency metrics.
        Input: list of { 'offset': int, 'data': bytes, 'identification': dict }
        Output: list of { 'id': int, 'type': str, 'fragments': list, 'fragment_offsets': list, 'complete': bool }
        """
        # Uses FragmentGrouper from reconstruction/grouping.py
        results = self.grouper.group_fragments(fragments)
        return results

    def reconstruct_file(self, fragments: List[Dict]) -> bytes:
        """
        Takes an ordered sequence of fragments and reconstructs the file.
        Applies denoising to each 512-byte fragment.
        """
        if not fragments:
            return b""
            
        # Sort by offset to handle gaps
        sorted_fragments = sorted(fragments, key=lambda x: x.get('offset', 0))
        
        reconstructed_data = bytearray()
        current_disk_pos = sorted_fragments[0]['offset']

        for fragment in sorted_fragments:
            offset = fragment.get('offset', current_disk_pos)
            data = fragment.get("data", b"")
            
            # 1. Fill gaps with zeros
            if offset > current_disk_pos:
                gap_size = offset - current_disk_pos
                reconstructed_data.extend(b"\x00" * gap_size)
            
            # 2. Denoise the fragment (FragmentAutoencoder expects 512-byte chunks)
            # If fragment is larger, we chunk it and denoise each part
            chunk_size = 512
            denoised_fragment = bytearray()
            for i in range(0, len(data), chunk_size):
                chunk = data[i : i + chunk_size]
                denoised_chunk = self.autoencoder.denoise(chunk)
                # Keep original length if possible
                if len(chunk) < chunk_size:
                    denoised_chunk = denoised_chunk[:len(chunk)]
                denoised_fragment.extend(denoised_chunk)
            
            # 3. Add to total (handling overlap if any)
            if offset < current_disk_pos:
                overlap = current_disk_pos - offset
                if overlap < len(denoised_fragment):
                    reconstructed_data.extend(denoised_fragment[overlap:])
            else:
                reconstructed_data.extend(denoised_fragment)
                
            current_disk_pos = offset + len(data)

        return bytes(reconstructed_data)
