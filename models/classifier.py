import torch
import torch.nn as nn
import torch.nn.functional as F


class FragmentClassifierCNN(nn.Module):
    """
    CNN model to classify if a 512-byte block is an image_fragment or non-image.
    Input: 1x32x16 (which is 512 bytes)
    """

    def __init__(self):
        super(FragmentClassifierCNN, self).__init__()
        # 1 channel input (bytes), 16 output channels, 3x3 kernel
        self.conv1 = nn.Conv2d(1, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        # after two pools of 2x2: (32/4) x (16/4) = 8 x 4
        self.fc1 = nn.Linear(32 * 8 * 4, 128)
        self.fc2 = nn.Linear(128, 2)  # 2 classes: image_fragment, non_image

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = self.pool(F.relu(self.conv2(x)))
        x = x.view(-1, 32 * 8 * 4)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def classify_block(block: bytes, model: nn.Module) -> bool:
    """
    Returns True if the block is predicted as an image fragment.
    """
    if len(block) < 512:
        block = block.ljust(512, b"\x00")
    tensor = torch.tensor(list(block), dtype=torch.float32).view(1, 1, 32, 16) / 255.0
    with torch.no_grad():
        output = model(tensor)
        _, predicted = torch.max(output.data, 1)
        return predicted.item() == 0  # Assuming 0 is image_fragment
