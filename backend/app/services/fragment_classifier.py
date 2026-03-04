import torch
import numpy as np
import os
from models.classifier import FragmentClassifier as AIModel


class FragmentClassifier:
    """
    Predicts the file type of a binary fragment using deep learning models
    (1D-CNN).
    """

    def __init__(self, model_path: str = None):
        if model_path is None:
            # Default to the best model checkpoint in projects root models/checkpoints/
            # Assuming the service is run from a location where models/ is visible
            current_dir = os.path.abspath(os.path.dirname(__file__))
            # From backend/app/services/ we go up 3 levels to reach root
            root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
            model_path = os.path.join(
                root_dir, "models", "checkpoints", "classifier_best.pth"
            )

        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Initialize the AI Model (1D-CNN)
        # Based on models/classifier.py, default num_classes is 3 (JPEG, PDF, OTHER)
        self.model = AIModel(num_classes=3)

        # Load model weights if they exist
        if os.path.exists(self.model_path):
            try:
                self.model.load_state_dict(
                    torch.load(self.model_path, map_location=self.device)
                )
                print(f"Loaded classifier weights from {self.model_path}")
            except Exception as e:
                print(f"Error loading classifier weights: {e}")
        else:
            print(
                f"Warning: Classifier weights not found at {self.model_path}. Using uninitialized model."
            )

        self.model.to(self.device)
        self.model.eval()

        # Class names mapping
        self.classes = {0: "JPEG", 1: "PDF", 2: "OTHER"}

    def classify_fragment(self, data: bytes) -> dict:
        """
        Takes raw fragment bytes and returns classification probabilities.
        The model expects a 512-byte input (1, 1, 512).
        """
        fragment_size = 512

        # 1. Preprocessing: Ensure fragment is exactly 512 bytes
        if len(data) > fragment_size:
            # Use the first 512 bytes
            data = data[:fragment_size]
        elif len(data) < fragment_size:
            # Pad with zeros if fragment is too small
            data = data.ljust(fragment_size, b"\x00")

        # 2. Convert to tensor: (1, 1, 512)
        # Normalize bytes [0, 255] to [0.0, 1.0]
        fragment_array = np.frombuffer(data, dtype=np.uint8).astype(np.float32) / 255.0
        fragment_tensor = (
            torch.from_numpy(fragment_array).view(1, 1, fragment_size).to(self.device)
        )

        # 3. Inference
        with torch.no_grad():
            output = self.model(fragment_tensor)
            # Apply softmax to get probabilities
            probabilities = (
                torch.softmax(output, dim=1).squeeze().cpu().numpy().tolist()
            )

        # 4. Extract results
        predicted_idx = np.argmax(probabilities)
        confidence = float(probabilities[predicted_idx])
        predicted_type = self.classes.get(predicted_idx, "unknown")

        return {
            "predicted_type": predicted_type,
            "confidence": confidence,
            "probabilities": {
                self.classes[i]: float(probabilities[i])
                for i in range(len(self.classes))
            },
        }

    def classify_fragments(self, fragments: list) -> list:
        """
        Classifies multiple fragments.
        Each item in 'fragments' list should be a tuple (offset, data).
        """
        results = []
        for offset, data in fragments:
            result = self.classify_fragment(data)
            result["offset"] = offset
            results.append(result)
        return results
