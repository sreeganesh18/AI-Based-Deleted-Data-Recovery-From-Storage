import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import os
from typing import Dict, Any, Optional
from utils.validation import calculate_psnr, calculate_ssim


class Trainer:
    """
    Generic training loop management for classification and autoencoders.
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: optim.Optimizer,
        criterion: nn.Module,
        device: str = "cpu"
    ):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        self.history: Dict[str, list] = {
            "train_loss": [], 
            "val_loss": [], 
            "val_acc": [],
            "val_psnr": [],
            "val_ssim": []
        }

    def train_epoch(self, dataloader: DataLoader) -> float:
        """Runs one epoch of training."""
        self.model.train()
        total_loss = 0.0
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = self.criterion(output, target)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        self.history["train_loss"].append(avg_loss)
        return avg_loss

    def validate_epoch(self, dataloader: DataLoader, noise_gen: Optional[Any] = None) -> Dict[str, float]:
        """Runs one epoch of validation."""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0
        total_psnr = 0.0
        total_ssim = 0.0
        
        with torch.no_grad():
            for data, target in dataloader:
                data = data.to(self.device)
                
                # If we have a noise generator, it's a denoising task
                if noise_gen:
                    # Apply noise to original data for the model to clean
                    clean_data = data
                    noisy_data = noise_gen.add_bit_flip_noise(clean_data, p=0.02)
                    noisy_data = noise_gen.add_masking_noise(noisy_data, length=32)
                    
                    output = self.model(noisy_data)
                    loss = self.criterion(output, clean_data)
                    total_loss += loss.item()
                    
                    # Compute PSNR/SSIM
                    total_psnr += calculate_psnr(clean_data, output)
                    total_ssim += calculate_ssim(clean_data, output)
                else:
                    # Classification task
                    target = target.to(self.device)
                    output = self.model(data)
                    loss = self.criterion(output, target)
                    total_loss += loss.item()
                    
                    # Accuracy only applies to classification tasks
                    if isinstance(self.criterion, nn.CrossEntropyLoss):
                        _, predicted = torch.max(output.data, 1)
                        total += target.size(0)
                        correct += (predicted == target).sum().item()

        avg_loss = total_loss / len(dataloader)
        self.history["val_loss"].append(avg_loss)
        
        metrics = {"loss": avg_loss}
        if total > 0:
            acc = 100 * correct / total
            self.history["val_acc"].append(acc)
            metrics["acc"] = acc
            
        if noise_gen:
            avg_psnr = total_psnr / len(dataloader)
            avg_ssim = total_ssim / len(dataloader)
            self.history["val_psnr"].append(avg_psnr)
            self.history["val_ssim"].append(avg_ssim)
            metrics["psnr"] = avg_psnr
            metrics["ssim"] = avg_ssim
            
        return metrics

    def save_checkpoint(self, path: str, epoch: int) -> None:
        """Saves a model checkpoint."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'history': self.history,
        }, path)

    def load_checkpoint(self, path: str) -> Optional[int]:
        """Loads a model checkpoint."""
        if os.path.exists(path):
            checkpoint = torch.load(path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.history = checkpoint.get('history', self.history)
            return checkpoint['epoch']
        return None
