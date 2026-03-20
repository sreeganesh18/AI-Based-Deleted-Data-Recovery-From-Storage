import math
from collections import Counter


class EntropyProfiler:
    """
    Calculates Shannon Entropy and other statistical profiles for file fragments.
    """

    def calculate_entropy(self, data: bytes) -> float:
        """
        Calculates the Shannon entropy of a byte sequence.
        Returns a value between 0.0 and 8.0.
        """
        if not data:
            return 0.0

        entropy = 0.0
        counts = Counter(data)
        total_len = len(data)
        for count in counts.values():
            p = count / total_len
            entropy -= p * math.log2(p)
            
        return entropy

    def profile_fragment(self, data: bytes) -> dict:
        """
        Returns a rich statistical profile for the fragment.
        """
        return {"entropy": self.calculate_entropy(data), "size": len(data)}
