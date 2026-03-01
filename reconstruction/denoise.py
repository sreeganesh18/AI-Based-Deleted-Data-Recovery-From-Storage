import torch
from models.autoencoder import FragmentAutoencoder
import os
import numpy as np

class DenoisingPipeline:
    """
    Applies the trained Autoencoder to clean fragment data.
    Ensures denoised versions are stored separately from originals.
    """

    def __init__(self, 
                 checkpoint_path: str = "models/checkpoints/autoencoder_best.pth",
                 output_dir: str = "dataset/fragments/denoised/",
                 device: str = "cpu"):
        self.output_dir = output_dir
        self.device = device
        
        # Ensure output dir exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Autoencoder
        self.model = FragmentAutoencoder()
        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
            # Handle both full checkpoint dict and state_dict only
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                self.model.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.model.load_state_dict(checkpoint)
        
        self.model.to(device)
        self.model.eval()

    def denoise_fragment(self, fragment: bytes) -> bytes:
        """
        Denoises a single 512-byte fragment.
        Returns cleaned bytes.
        """
        # 1. Prepare fragment tensor
        fragment_tensor = torch.tensor(list(fragment), dtype=torch.float32) / 255.0
        fragment_tensor = fragment_tensor.unsqueeze(0).unsqueeze(0).to(self.device) # (1, 1, 512)
        
        # 2. Forward pass through Autoencoder
        with torch.no_grad():
            reconstructed = self.model(fragment_tensor)
            
            # Rescale back to 0-255 and convert to bytes
            denoised_data = reconstructed.squeeze().cpu().numpy() * 255.0
            # Clip to [0, 255] just in case
            denoised_data = np.clip(denoised_data, 0, 255).astype(np.uint8)
            
            return denoised_data.tobytes()

    def process_batch(self, fragments: list) -> list:
        """
        Process multiple fragments in a batch for efficiency.
        `fragments` is a list of (id, bytes).
        Returns a list of (id, denoised_bytes).
        """
        results = []
        for frag_id, frag_bytes in fragments:
            denoised = self.denoise_fragment(frag_bytes)
            results.append((frag_id, denoised))
        return results

    def save_denoised(self, frag_id: str, denoised_bytes: bytes) -> str:
        """Saves a denoised fragment and returns its new path."""
        file_path = os.path.join(self.output_dir, f"denoised_{frag_id}")
        # Ensure subdirectories match (optional, for organization)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(denoised_bytes)
        return file_path
