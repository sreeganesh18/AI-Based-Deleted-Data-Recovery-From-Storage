from reconstruction.autoencoder import ReassemblyAutoencoder
from reconstruction.grouping import FragmentGrouper
from typing import List, Dict


class ReassemblyEngine:
    """
    Fragment Reassembly Engine for reconstructing files.
    Utilizes Graph algorithms, LSTM semantic adjacency, and Genetic Search.
    Connected to reconstruction/autoencoder.py for advanced AI-powered data reconstruction.
    """

    def __init__(self, model_path: str = None):
        self.autoencoder = ReassemblyAutoencoder(model_path=model_path)
        self.grouper = FragmentGrouper()

    def sequence_fragments(self, fragments: List[Dict]) -> List[Dict]:
        """
        Analyzes a list of fragments and sequences them using adjacency metrics.
        Input: list of { 'offset': int, 'data': bytes, 'identification': dict }
        Output: list of { 'id': int, 'type': str, 'data': bytes, 'fragment_offsets': list, 'completed': bool }
        """
        # Uses FragmentGrouper from reconstruction/grouping.py
        results = self.grouper.group_fragments(fragments)
        return results

    def calculate_coherence(self, fragment_a: bytes, fragment_b: bytes) -> float:
        """
        Computes the semantic adjacency or Coherence of Euclidean Distance
        between the tail of fragment_a and the head of fragment_b.
        """
        # In a real scenario, this would involve computing the coherence metric.
        # For now, we use the autoencoder's confidence score as part of the metric.
        score_a = self.autoencoder.get_confidence_score(fragment_a)
        score_b = self.autoencoder.get_confidence_score(fragment_b)

        # Simple coherence: average of confidence scores
        return (score_a + score_b) / 2.0

    def reconstruct_file(self, sequence: List[Dict]) -> bytes:
        """
        Takes an ordered sequence of fragments and reconstructs the file.
        Each fragment contains 'data' (bytes).
        """
        reconstructed_data = bytearray()

        for fragment in sequence:
            data = fragment.get("data", b"")
            # Apply denoising through the autoencoder before reassembly
            denoised = self.autoencoder.denoise(data)
            reconstructed_data.extend(denoised)

        return bytes(reconstructed_data)
