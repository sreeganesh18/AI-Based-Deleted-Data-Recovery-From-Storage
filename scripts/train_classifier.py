import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
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
    
    # Initialize Dataset
    if not os.path.exists(args.data_dir):
        print(f"Warning: data directory {args.data_dir} not found. Ensure fragmenter has been run.")
        os.makedirs(args.data_dir, exist_ok=True)
        for d in ["jpeg", "pdf", "other"]:
            os.makedirs(os.path.join(args.data_dir, d), exist_ok=True)
    
    full_dataset = FragmentDataset(root_dir=args.data_dir)
    if len(full_dataset) == 0:
        print("No data found to train. Please run fragmenter first or use a valid dataset directory.")
        return

    # 80/20 Train/Val Split
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])
    
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    print(f"Dataset sizes: Train={len(train_dataset)}, Val={len(val_dataset)}")
    
    # Initialize Model, Optimizer, Criterion
    model = FragmentClassifier(num_classes=3)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.CrossEntropyLoss()
    
    # Initialize Trainer
    trainer = Trainer(model, optimizer, criterion, device=device)
    
    # Training Loop
    best_val_acc = 0.0
    for epoch in range(1, args.epochs + 1):
        train_loss = trainer.train_epoch(train_loader)
        val_metrics = trainer.validate_epoch(val_loader)
        
        val_loss = val_metrics["loss"]
        val_acc = val_metrics.get("acc", 0.0)
        
        print(f"Epoch {epoch}/{args.epochs}:")
        print(f"  Train Loss: {train_loss:.4f}")
        print(f"  Val Loss:   {val_loss:.4f}")
        print(f"  Val Acc:    {val_acc:.2f}%")
        
        # Save best model based on validation accuracy
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            trainer.save_checkpoint(args.model_out, epoch)
            print(f"Saved best model with Val Acc {best_val_acc:.2f}% to {args.model_out}")

    print("Training complete.")


if __name__ == "__main__":
    main()
