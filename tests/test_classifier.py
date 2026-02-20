import torch
from models.classifier import FragmentClassifierCNN, classify_block


def test_classifier_output_shape():
    model = FragmentClassifierCNN()
    # Dummy block
    tensor = torch.randn(1, 1, 32, 16)
    output = model(tensor)

    assert output.shape == (1, 2)  # Batch 1, 2 classes


def test_classify_block():
    model = FragmentClassifierCNN()
    # Just checking execution without crash
    block = b"\x00" * 512
    is_image = classify_block(block, model)
    assert isinstance(is_image, bool)
