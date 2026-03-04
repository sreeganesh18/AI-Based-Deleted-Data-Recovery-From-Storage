import torch
import numpy as np
import os
from models.autoencoder import FragmentAutoencoder


class ReassemblyAutoencoder:
    """
    Service layer for applying the FragmentAutoencoder model for reassembly tasks.
    Used for denoising fragments and calculating reconstruction confidence.
    """

    def __init__(self, model_path: str = None):
        if model_path is None:
            # Default to the best model checkpoint in root models/checkpoints/
            current_dir = os.path.abspath(os.path.dirname(__file__))
            # From reconstruction/ to root/ is up 1 level
            root_dir = os.path.abspath(os.path.join(current_dir, ".."))
            model_path = os.path.join(
                root_dir, "models", "checkpoints", "autoencoder_best.pth"
            )

        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = FragmentAutoencoder()

        # Load model weights if they exist (even if uninitialized, the class should be usable)
        if os.path.exists(self.model_path):
            try:
                self.model.load_state_dict(
                    torch.load(self.model_path, map_location=self.device)
                )
                print(f"Loaded autoencoder weights from {self.model_path}")
            except Exception as e:
                print(f"Error loading autoencoder weights: {e}")
        else:
            print(
                f"Warning: Autoencoder weights not found at {self.model_path}. Using uninitialized model."
            )

        self.model.to(self.device)
        self.model.eval()

    def denoise(self, data: bytes) -> bytes:
        """
        Denoises a 512-byte fragment using the autoencoder.
        """
        if not data:
            return b""

        # Preprocessing: Ensure fragment is exactly 512 bytes
        padded = data.ljust(512, b"\x00")[:512]
        # Normalize bytes [0, 255] to [0.0, 1.0]
        fragment_array = (
            np.frombuffer(padded, dtype=np.uint8).astype(np.float32) / 255.0
        )
        fragment_tensor = (
            torch.from_numpy(fragment_array).view(1, 1, 512).to(self.device)
        )

        with torch.no_grad():
            reconstructed = self.model(fragment_tensor)
            # Rescale back to 0-255 and convert to bytes
            denoised_data = reconstructed.squeeze().cpu().numpy() * 255.0
            # Clip to [0, 255] just in case
            denoised_data = np.clip(denoised_data, 0, 255).astype(np.uint8)
            return denoised_data.tobytes()

    def get_confidence_score(self, data: bytes) -> float:
        """
        Computes a confidence score based on reconstruction error (MSE).
        Lower error = Higher confidence.
        """
        if not data:
            return 0.0

        padded = data.ljust(512, b"\x00")[:512]
        fragment_array = (
            np.frombuffer(padded, dtype=np.uint8).astype(np.float32) / 255.0
        )
        fragment_tensor = (
            torch.from_numpy(fragment_array).view(1, 1, 512).to(self.device)
        )

        with torch.no_grad():
            reconstructed = self.model(fragment_tensor)
            mse_error = torch.mean((fragment_tensor - reconstructed) ** 2).item()
            # Convert MSE to a confidence score [0, 1]
            # Assumes MSE for perfect match is 0, and typical errors stay low
            confidence = max(
                0.0, 1.0 - (mse_error * 10.0)
            )  # Scale factor of 10 for sensitivity
            return confidence
