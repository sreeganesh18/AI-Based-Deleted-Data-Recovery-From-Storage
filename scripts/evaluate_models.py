import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
import numpy as np
import json
import os
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from models.classifier import FragmentClassifier
from models.autoencoder import FragmentAutoencoder
from dataset.loader import FragmentDataset
from dataset.noise import NoiseGenerator
from utils.validation import calculate_psnr, calculate_ssim

def evaluate_classifier(model, dataloader, device):
    model.eval()
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for data, target in dataloader:
            data = data.to(device)
            target = target.to(device)
            output = model(data)
            _, predicted = torch.max(output.data, 1)
            all_preds.extend(predicted.cpu().numpy())
            all_targets.extend(target.cpu().numpy())
            
    accuracy = accuracy_score(all_targets, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_targets, all_preds, average='weighted')
    
    # Class-wise metrics
    # Classes: 0: jpeg, 1: pdf, 2: other (based on FragmentDataset)
    class_metrics = precision_recall_fscore_support(all_targets, all_preds, average=None)
    
    results = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "class_wise": {
            "jpeg": {
                "precision": float(class_metrics[0][0]),
                "recall": float(class_metrics[1][0]),
                "f1": float(class_metrics[2][0])
            },
            "pdf": {
                "precision": float(class_metrics[0][1]),
                "recall": float(class_metrics[1][1]),
                "f1": float(class_metrics[2][1])
            },
            "other": {
                "precision": float(class_metrics[0][2]),
                "recall": float(class_metrics[1][2]),
                "f1": float(class_metrics[2][2])
            }
        }
    }
    return results

def evaluate_autoencoder(model, dataloader, device):
    model.eval()
    noise_gen = NoiseGenerator()
    total_psnr = 0.0
    total_ssim = 0.0
    count = 0
    
    with torch.no_grad():
        for data, _ in dataloader:
            clean_data = data.to(device)
            # Apply same noise as during training
            noisy_data = noise_gen.add_bit_flip_noise(clean_data, p=0.02)
            noisy_data = noise_gen.add_masking_noise(noisy_data, length=32)
            
            output = model(noisy_data)
            
            total_psnr += calculate_psnr(clean_data, output)
            total_ssim += calculate_ssim(clean_data, output)
            count += 1
            
    results = {
        "psnr": float(total_psnr / count),
        "ssim": float(total_ssim / count)
    }
    return results

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Paths
    classifier_ckpt = "models/checkpoints/classifier_best.pth"
    autoencoder_ckpt = "models/checkpoints/autoencoder_best.pth"
    data_dir = "dataset/fragments"
    report_json = "evaluation_report.json"
    report_md = "evaluation_report.md"
    
    # Load Dataset
    if not os.path.exists(data_dir):
        print(f"Error: Data directory {data_dir} not found.")
        return

    full_dataset = FragmentDataset(root_dir=data_dir)
    if len(full_dataset) == 0:
        print("Error: No data found.")
        return

    # Use 20% validation split for evaluation
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    _, val_dataset = random_split(full_dataset, [train_size, val_size])
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
    
    # Evaluate Classifier
    classifier_results = {}
    if os.path.exists(classifier_ckpt):
        classifier = FragmentClassifier(num_classes=3)
        checkpoint = torch.load(classifier_ckpt, map_location=device)
        classifier.load_state_dict(checkpoint['model_state_dict'])
        classifier.to(device)
        print("Evaluating Classifier...")
        classifier_results = evaluate_classifier(classifier, val_loader, device)
    else:
        print(f"Warning: Classifier checkpoint not found at {classifier_ckpt}")

    # Evaluate Autoencoder
    autoencoder_results = {}
    if os.path.exists(autoencoder_ckpt):
        autoencoder = FragmentAutoencoder()
        checkpoint = torch.load(autoencoder_ckpt, map_location=device)
        autoencoder.load_state_dict(checkpoint['model_state_dict'])
        autoencoder.to(device)
        print("Evaluating Autoencoder...")
        autoencoder_results = evaluate_autoencoder(autoencoder, val_loader, device)
    else:
        print(f"Warning: Autoencoder checkpoint not found at {autoencoder_ckpt}")
        
    # Combine results
    report = {
        "classifier": classifier_results,
        "autoencoder": autoencoder_results
    }
    
    # Save JSON
    with open(report_json, 'w') as f:
        json.dump(report, f, indent=4)
    print(f"Report saved to {report_json}")
    
    # Generate Markdown Report
    md_content = f"""# Quantitative Model Performance Report

## Fragment Classifier (1D-CNN)
- **Overall Accuracy:** {classifier_results.get('accuracy', 0)*100:.2f}%
- **Precision (Weighted):** {classifier_results.get('precision', 0):.4f}
- **Recall (Weighted):** {classifier_results.get('recall', 0):.4f}
- **F1-Score (Weighted):** {classifier_results.get('f1', 0):.4f}

### Class-wise Performance
| Class | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| JPEG  | {classifier_results.get('class_wise', {}).get('jpeg', {}).get('precision', 0):.4f} | {classifier_results.get('class_wise', {}).get('jpeg', {}).get('recall', 0):.4f} | {classifier_results.get('class_wise', {}).get('jpeg', {}).get('f1', 0):.4f} |
| PDF   | {classifier_results.get('class_wise', {}).get('pdf', {}).get('precision', 0):.4f} | {classifier_results.get('class_wise', {}).get('pdf', {}).get('recall', 0):.4f} | {classifier_results.get('class_wise', {}).get('pdf', {}).get('f1', 0):.4f} |
| OTHER | {classifier_results.get('class_wise', {}).get('other', {}).get('precision', 0):.4f} | {classifier_results.get('class_wise', {}).get('other', {}).get('recall', 0):.4f} | {classifier_results.get('class_wise', {}).get('other', {}).get('f1', 0):.4f} |

## Denoising Autoencoder
- **Average PSNR:** {autoencoder_results.get('psnr', 0):.4f} dB
- **Average SSIM:** {autoencoder_results.get('ssim', 0):.4f}

## Targets Check
- JPEG Recall Target: 90% (Current: {classifier_results.get('class_wise', {}).get('jpeg', {}).get('recall', 0)*100:.2f}%)
- PDF Recall Target: 85% (Current: {classifier_results.get('class_wise', {}).get('pdf', {}).get('recall', 0)*100:.2f}%)
"""
    with open(report_md, 'w') as f:
        f.write(md_content)
    print(f"Report saved to {report_md}")

if __name__ == "__main__":
    main()
