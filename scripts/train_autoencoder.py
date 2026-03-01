import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from models.autoencoder import FragmentAutoencoder
from dataset.loader import FragmentDataset
from dataset.noise import NoiseGenerator
from utils.training import Trainer
import os


def main():
    parser = argparse.ArgumentParser(description="Train Denoising Autoencoder")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--data-dir", type=str, default="dataset/fragments", help="Root directory for fragment data")
    parser.add_argument("--model-out", type=str, default="models/checkpoints/autoencoder_best.pth", help="Model checkpoint path")
    
    args = parser.parse_args()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    if not os.path.exists(args.data_dir):
        print(f"Error: data directory {args.data_dir} not found.")
        return
        
    full_dataset = FragmentDataset(root_dir=args.data_dir)
    if len(full_dataset) == 0:
        print("No data found to train.")
        return

    # 80/20 Train/Val Split
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    print(f"Dataset sizes: Train={len(train_dataset)}, Val={len(val_dataset)}")
    
    # Initialize Model, Optimizer, Criterion
    model = FragmentAutoencoder()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()
    
    # Initialize Noise Generator for Training/Validation
    noise_gen = NoiseGenerator()
    
    # Initialize Trainer
    trainer = Trainer(model, optimizer, criterion, device=device)
    
    # Training Loop
    best_val_psnr = -1.0
    for epoch in range(1, args.epochs + 1):
        # Training
        model.train()
        epoch_loss = 0.0
        for data, _ in train_loader:
            clean_data = data.to(device)
            noisy_data = noise_gen.add_bit_flip_noise(clean_data, p=0.02)
            noisy_data = noise_gen.add_masking_noise(noisy_data, length=32)
            
            optimizer.zero_grad()
            reconstructed = model(noisy_data)
            loss = criterion(reconstructed, clean_data)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        avg_train_loss = epoch_loss / len(train_loader)
        trainer.history["train_loss"].append(avg_train_loss)
        
        # Validation using Trainer's specialized method
        val_metrics = trainer.validate_epoch(val_loader, noise_gen=noise_gen)
        
        val_loss = val_metrics["loss"]
        val_psnr = val_metrics.get("psnr", 0.0)
        val_ssim = val_metrics.get("ssim", 0.0)
        
        print(f"Epoch {epoch}/{args.epochs}:")
        print(f"  Train Loss: {avg_train_loss:.6f}")
        print(f"  Val Loss:   {val_loss:.6f}")
        print(f"  Val PSNR:   {val_psnr:.2f} dB")
        print(f"  Val SSIM:   {val_ssim:.4f}")
        
        # Save best model based on PSNR
        if val_psnr > best_val_psnr:
            best_val_psnr = val_psnr
            trainer.save_checkpoint(args.model_out, epoch)
            print(f"Saved best model with Val PSNR {best_val_psnr:.2f} to {args.model_out}")

    print("Training complete.")


if __name__ == "__main__":
    main()
