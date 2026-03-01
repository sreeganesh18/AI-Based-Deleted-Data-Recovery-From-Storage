import torch
import pytest
from models.autoencoder import FragmentAutoencoder
from models.classifier import FragmentClassifier


def test_autoencoder_shape():
    """Verifies that the autoencoder maintains input-output shape."""
    model = FragmentAutoencoder()
    # Batch of 4, 1 channel, 512 length
    x = torch.randn(4, 1, 512)
    output = model(x)
    
    assert output.shape == (4, 1, 512)
    # Check output range due to Sigmoid
    assert torch.all(output >= 0.0) and torch.all(output <= 1.0)


def test_autoencoder_denoising_effect():
    """Check if autoencoder can reduce simple noise (with random weights, just checking flow)."""
    model = FragmentAutoencoder()
    model.eval()
    
    # Create a simple signal (e.g., all 0.5)
    clean = torch.full((1, 1, 512), 0.5)
    # Add noise
    noisy = clean + torch.randn((1, 1, 512)) * 0.1
    noisy = torch.clamp(noisy, 0, 1)
    
    with torch.no_grad():
        denoised = model(noisy)
    
    assert denoised.shape == (1, 1, 512)
    # We don't expect it to actually denoise well with random weights,
    # but it should produce a valid output.


def test_classifier_output_shape():
    """Verifies that the classifier produces the correct output shape."""
    num_classes = 3
    model = FragmentClassifier(num_classes=num_classes)
    
    # Batch of 4, 1 channel, 512 length
    x = torch.randn(4, 1, 512)
    output = model(x)
    
    assert output.shape == (4, num_classes)


def test_classifier_parameter_count():
    """Simple check to ensure model has parameters."""
    model = FragmentClassifier()
    params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    assert params > 1_000_000  # Should be around 4M with fc layer 128*128


def test_classifier_inference():
    """Verifies basic inference flow."""
    model = FragmentClassifier(num_classes=3)
    model.eval()
    
    x = torch.randn(1, 1, 512)
    with torch.no_grad():
        output = model(x)
        probabilities = torch.softmax(output, dim=1)
        
    assert probabilities.shape == (1, 3)
    assert torch.isclose(torch.sum(probabilities), torch.tensor(1.0))
