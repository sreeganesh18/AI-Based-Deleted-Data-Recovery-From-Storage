import torch
import pytest
from models.autoencoder import FragmentAutoencoder


def test_autoencoder_shape():
    """Verifies that the autoencoder maintains input-output shape."""
    model = FragmentAutoencoder()
    x = torch.randn(4, 1, 512)
    output = model(x)
    
    assert output.shape == (4, 1, 512)
    # Check output range due to Sigmoid
    assert torch.all(output >= 0.0) and torch.all(output <= 1.0)
