import os
import torch
from torch.utils.data import Dataset
from typing import List, Tuple


class FragmentDataset(Dataset):
    """
    Loads 512-byte fragments from a directory structure.
    Expected structure: root_dir/[label_dir]/[fragment_files].bin
    """

    def __init__(self, root_dir: str, labels: List[str] = ["jpeg", "pdf", "other"]):
        self.root_dir = root_dir
        self.labels = labels
        self.label_to_idx = {label: i for i, label in enumerate(labels)}
        self.samples: List[Tuple[str, int]] = []
        self._load_samples()

    def _load_samples(self) -> None:
        """Discovers all fragments in the root directory and assigns labels."""
        if not os.path.exists(self.root_dir):
            return

        for label in self.labels:
            label_dir = os.path.join(self.root_dir, label)
            if os.path.isdir(label_dir):
                for filename in os.listdir(label_dir):
                    if filename.endswith(".bin"):
                        self.samples.append((os.path.join(label_dir, filename), self.label_to_idx[label]))

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """Returns normalized 512-byte fragment tensor and its label index."""
        file_path, label_idx = self.samples[idx]
        with open(file_path, "rb") as f:
            data = f.read(512)
            # Handle short reads if necessary (though fragmenter should pad)
            if len(data) < 512:
                data = data.ljust(512, b"\x00")
        
        # Normalize 0-255 to 0.0-1.0
        fragment_tensor = torch.tensor(list(data), dtype=torch.float32) / 255.0
        # Shape: (1, 512) for Conv1D compatibility
        fragment_tensor = fragment_tensor.unsqueeze(0)
        
        return fragment_tensor, label_idx
