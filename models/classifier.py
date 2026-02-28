import torch
import torch.nn as nn
import torch.nn.functional as F


class FragmentClassifier(nn.Module):
    """
    1D-CNN for fragment classification (JPEG, PDF, OTHER).
    Input: (batch, 1, 512) tensor
    Output: (batch, 3) logits
    """

    def __init__(self, num_classes: int = 3):
        super(FragmentClassifier, self).__init__()
        
        # Input: (batch, 1, 512)
        self.conv1 = nn.Conv1d(1, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm1d(32)
        # Shape: (batch, 32, 512)
        
        self.conv2 = nn.Conv1d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(64)
        # Shape: (batch, 64, 512)
        
        self.pool = nn.MaxPool1d(2)
        # Shape: (batch, 64, 256) after pooling
        
        self.conv3 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(128)
        # Shape: (batch, 128, 256)
        
        self.fc1 = nn.Linear(128 * 128, 256)
        # MaxPooling 256 / 2 = 128 (assuming we pool twice)
        # Wait, I only pooled once above.
        
        self.fc2 = nn.Linear(256, num_classes)
        self.dropout = nn.Dropout(0.3)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Layer 1
        x = F.relu(self.bn1(self.conv1(x)))
        # Layer 2
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        
        # Layer 3
        x = F.relu(self.bn3(self.conv3(x)))
        x = self.pool(x)
        
        # Flatten
        # After two pools, length is 512 / 2 / 2 = 128
        x = x.view(x.size(0), -1)
        
        x = self.dropout(F.relu(self.fc1(x)))
        x = self.fc2(x)
        
        return x
