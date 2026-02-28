import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from models.classifier import FragmentClassifier
from dataset.loader import FragmentDataset
from utils.training import Trainer
import os


def main():
    parser = argparse.ArgumentParser(description="Train Fragment Classifier (1D-CNN)")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs to train")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for training")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--data-dir", type=str, default="dataset/fragments", help="Root directory for fragment data")
    parser.add_argument("--model-out", type=str, default="models/checkpoints/classifier_best.pth", help="Model checkpoint path")
    
    args = parser.parse_args()
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Initialize Dataset and DataLoader
    # Note: We assume the directory exists or is created by Fragmenter
    if not os.path.exists(args.data_dir):
        print(f"Warning: data directory {args.data_dir} not found. Ensure fragmenter has been run.")
        os.makedirs(args.data_dir, exist_ok=True)
        # Create subdirs for testing if they don't exist
        for d in ["jpeg", "pdf", "other"]:
            os.makedirs(os.path.join(args.data_dir, d), exist_ok=True)
    
    dataset = FragmentDataset(root_dir=args.data_dir)
    if len(dataset) == 0:
        print("No data found to train. Please run fragmenter first or use a valid dataset directory.")
        return
        
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)
    
    # Initialize Model, Optimizer, Criterion
    model = FragmentClassifier(num_classes=3)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()
    
    # Initialize Trainer
    trainer = Trainer(model, optimizer, criterion, device=device)
    
    # Training Loop
    best_loss = float('inf')
    for epoch in range(1, args.epochs + 1):
        train_loss = trainer.train_epoch(dataloader)
        print(f"Epoch {epoch}/{args.epochs} - Loss: {train_loss:.4f}")
        
        # Save best model
        if train_loss < best_loss:
            best_loss = train_loss
            trainer.save_checkpoint(args.model_out, epoch)
            print(f"Saved best model with loss {best_loss:.4f} to {args.model_out}")

    print("Training complete.")


if __name__ == "__main__":
    main()
