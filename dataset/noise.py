import torch


class NoiseGenerator:
    """
    Provides noise injection methods for 512-byte fragment tensors.
    Used for training Denoising Autoencoders.
    """

    @staticmethod
    def add_bit_flip_noise(tensor: torch.Tensor, p: float = 0.01) -> torch.Tensor:
        """
        Randomly flips bits in the fragment.
        Expects normalized tensor [0.0, 1.0].
        """
        # Since these are normalized floats, "flipping a bit" is complex.
        # We simulate this by replacing bytes with random values with probability p.
        noisy_tensor = tensor.clone()
        mask = torch.rand(tensor.shape) < p
        # Replace with random normalized byte values
        noisy_tensor[mask] = torch.rand(noisy_tensor[mask].shape)
        return noisy_tensor

    @staticmethod
    def add_masking_noise(tensor: torch.Tensor, length: int = 32) -> torch.Tensor:
        """
        Zeroes out a random contiguous segment of the fragment.
        """
        noisy_tensor = tensor.clone()
        # tensor shape is (1, 512)
        total_len = tensor.shape[-1]
        if length >= total_len:
            return torch.zeros_like(tensor)
            
        start = torch.randint(0, total_len - length + 1, (1,)).item()
        noisy_tensor[..., start : start + length] = 0.0
        return noisy_tensor
