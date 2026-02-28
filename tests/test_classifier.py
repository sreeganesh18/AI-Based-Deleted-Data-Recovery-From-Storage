import torch
import pytest
from models.classifier import FragmentClassifier


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
