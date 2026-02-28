import torch
import pytest
from dataset.noise import NoiseGenerator


def test_bit_flip_noise():
    """Verifies bit-flip noise modifies the tensor."""
    # Start with all ones
    tensor = torch.ones((1, 512))
    # High probability to ensure change
    noisy = NoiseGenerator.add_bit_flip_noise(tensor, p=0.5)
    
    assert noisy.shape == (1, 512)
    # Check that some values have changed
    assert not torch.equal(tensor, noisy)
    # Check that values are still in [0, 1]
    assert torch.all(noisy >= 0.0) and torch.all(noisy <= 1.0)


def test_masking_noise():
    """Verifies masking noise zeroes out a segment."""
    tensor = torch.ones((1, 512))
    length = 64
    noisy = NoiseGenerator.add_masking_noise(tensor, length=length)
    
    assert noisy.shape == (1, 512)
    # Count zeros (there should be exactly 'length' zeros since we started with ones)
    num_zeros = (noisy == 0.0).sum().item()
    assert num_zeros == length
