from sklearn.cluster import KMeans
import numpy as np


class FragmentGrouper:
    """
    Groups fragmented image blocks that belong to the same original file.
    Extracts simulated embeddings and uses K-Means to cluster.
    """

    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)

    def extract_features(self, blocks: list[bytes]) -> np.ndarray:
        """
        Simple feature extraction logic for blocks.
        In a real scenario, this uses an AI encoder's feature space.
        Here we compute basic statistical features.
        """
        features = []
        for b in blocks:
            padded = b.ljust(512, b"\x00")
            arr = np.frombuffer(padded, dtype=np.uint8)
            mean = np.mean(arr)
            std = np.std(arr)
            # Add basic histogram features
            hist, _ = np.histogram(arr, bins=8, range=(0, 256))
            features.append(np.concatenate(([mean, std], hist)))
        return np.array(features)

    def group_fragments(self, blocks: list[bytes]) -> dict:
        if not blocks:
            return {}

        features = self.extract_features(blocks)

        # Determine number of clusters dynamically if needed, here we use fixed
        n_samples = len(blocks)
        n_clusters = min(self.n_clusters, n_samples)

        if n_clusters < 1:
            return {}

        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(features)

        grouped = {}
        for idx, label in enumerate(labels):
            if label not in grouped:
                grouped[label] = []
            grouped[label].append(blocks[idx])

        return grouped
