import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
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
        
    dataset = FragmentDataset(root_dir=args.data_dir)
    if len(dataset) == 0:
        print("No data found to train.")
        return
        
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Initialize Model, Optimizer, Criterion
    model = FragmentAutoencoder()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()
    
    # Initialize Noise Generator
    noise_gen = NoiseGenerator()
    
    # Training Loop
    best_loss = float('inf')
    for epoch in range(1, args.epochs + 1):
        model.train()
        epoch_loss = 0.0
        
        for data, _ in dataloader:
            # We ignore labels for autoencoder (unsupervised reconstruction)
            clean_data = data.to(device)
            
            # Apply Noise (e.g., mix of bit-flip and masking)
            noisy_data = noise_gen.add_bit_flip_noise(clean_data, p=0.02)
            noisy_data = noise_gen.add_masking_noise(noisy_data, length=32)
            
            optimizer.zero_grad()
            reconstructed = model(noisy_data)
            loss = criterion(reconstructed, clean_data)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
            
        avg_loss = epoch_loss / len(dataloader)
        print(f"Epoch {epoch}/{args.epochs} - Reconstruction Loss: {avg_loss:.6f}")
        
        # Save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            os.makedirs(os.path.dirname(args.model_out), exist_ok=True)
            torch.save(model.state_dict(), args.model_out)
            print(f"Saved best model with reconstruction loss {best_loss:.6f} to {args.model_out}")

    print("Training complete.")


if __name__ == "__main__":
    main()
