import torch
import torch.nn as nn


class FragmentAutoencoder(nn.Module):
    """
    1D-Convolutional Denoising Autoencoder for 512-byte fragments.
    Input/Output: (batch, 1, 512) tensor
    """

    def __init__(self):
        super(FragmentAutoencoder, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=3, stride=2, padding=1),  # -> (batch, 32, 256)
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.Conv1d(32, 64, kernel_size=3, stride=2, padding=1), # -> (batch, 64, 128)
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Conv1d(64, 128, kernel_size=3, stride=2, padding=1), # -> (batch, 128, 64)
            nn.ReLU(),
            nn.BatchNorm1d(128)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.ConvTranspose1d(128, 64, kernel_size=3, stride=2, padding=1, output_padding=1), # -> (batch, 64, 128)
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.ConvTranspose1d(64, 32, kernel_size=3, stride=2, padding=1, output_padding=1),  # -> (batch, 32, 256)
            nn.ReLU(),
            nn.BatchNorm1d(32),
            nn.ConvTranspose1d(32, 1, kernel_size=3, stride=2, padding=1, output_padding=1),   # -> (batch, 1, 512)
            nn.Sigmoid() # Sigmoid for [0, 1] output
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.encoder(x)
        x = self.decoder(x)
        return x
