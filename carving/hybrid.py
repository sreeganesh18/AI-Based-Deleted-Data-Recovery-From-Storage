import torch
import torch.nn.functional as F
from typing import List, Dict, Optional
from carving.signature import SignatureCarver
from models.classifier import FragmentClassifier
import os

class HybridCarver:
    """
    Combines traditional signature-based carving with AI classification.
    Authority: Signatures (Primary) -> Classifier (Fallback).
    """

    def __init__(self, 
                 checkpoint_path: str = "models/checkpoints/classifier_best.pth",
                 confidence_threshold: float = 0.7,
                 device: str = "cpu"):
        self.signature_carver = SignatureCarver()
        self.confidence_threshold = confidence_threshold
        self.device = device
        
        # Initialize Classifier
        self.classifier = FragmentClassifier(num_classes=3)
        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)
            # Handle both full checkpoint dict and state_dict only
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                self.classifier.load_state_dict(checkpoint['model_state_dict'])
            else:
                self.classifier.load_state_dict(checkpoint)
        
        self.classifier.to(device)
        self.classifier.eval()
        
        self.labels = ["jpeg", "pdf", "other"]

    def identify_fragment(self, fragment: bytes) -> Dict:
        """
        Identifies a single 512-byte fragment.
        Returns: { "type": "jpeg/pdf/other", "confidence": float, "source": "signature/ai" }
        """
        # 0. Fast-path for all-zero blocks (very common in disk images)
        if not any(fragment):
            return {"type": "other", "confidence": 1.0, "source": "zero_block"}

        # 1. Check for Signatures (e.g., JPEG headers)
        if fragment.startswith(b"\xff\xd8"):
            return {"type": "jpeg", "confidence": 1.0, "source": "signature"}
        
        # Add basic PDF header check for authority
        if fragment.startswith(b"%PDF"):
            return {"type": "pdf", "confidence": 1.0, "source": "signature"}

        # 2. Fallback to AI Classifier
        fragment_tensor = torch.tensor(list(fragment), dtype=torch.float32) / 255.0
        fragment_tensor = fragment_tensor.unsqueeze(0).unsqueeze(0).to(self.device) # (1, 1, 512)
        
        with torch.no_grad():
            output = self.classifier(fragment_tensor)
            probabilities = F.softmax(output, dim=1)
            conf, pred = torch.max(probabilities, 1)
            
            label = self.labels[pred.item()]
            confidence = conf.item()
            
            if confidence >= self.confidence_threshold:
                res = {"type": label, "confidence": confidence, "source": "ai"}
            else:
                res = {"type": "other", "confidence": confidence, "source": "ai_low_confidence"}
            
            return res

    def scan_disk(self, scanner_generator) -> List[Dict]:
        """
        Scans a disk yielding (offset, block) pairs and identifies each fragment.
        """
        results = []
        for offset, block in scanner_generator:
            identification = self.identify_fragment(block)
            results.append({
                "offset": offset,
                "identification": identification
            })
        return results
