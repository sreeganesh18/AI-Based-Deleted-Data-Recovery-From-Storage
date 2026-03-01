from typing import List, Dict, Tuple
import numpy as np
import cv2
import os

def generate_carving_summary(results: List[Dict]) -> Dict:
    """
    Produces a summary of the carving scan.
    `results` is a list of { "offset": int, "identification": { "type": str, "source": str, ... } }
    """
    summary = {
        "total_fragments": len(results),
        "jpeg": {"signature": 0, "ai": 0, "total": 0},
        "pdf": {"signature": 0, "ai": 0, "total": 0},
        "other": 0
    }
    
    for item in results:
        ident = item["identification"]
        itype = ident["type"]
        isource = ident["source"]
        
        if itype == "jpeg":
            summary["jpeg"]["total"] += 1
            if isource == "signature":
                summary["jpeg"]["signature"] += 1
            else:
                summary["jpeg"]["ai"] += 1
        elif itype == "pdf":
            summary["pdf"]["total"] += 1
            if isource == "signature":
                summary["pdf"]["signature"] += 1
            else:
                summary["pdf"]["ai"] += 1
        else:
            summary["other"] += 1
            
    return summary

def get_visual_comparison(original: bytes, denoised: bytes) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepares original and denoised bytes for visual comparison in UI.
    Converts 512-byte fragments to normalized numpy arrays.
    """
    orig_np = np.frombuffer(original, dtype=np.uint8).astype(np.float32) / 255.0
    denoised_np = np.frombuffer(denoised, dtype=np.uint8).astype(np.float32) / 255.0
    return orig_np, denoised_np

def save_visual_report(original: np.ndarray, denoised: np.ndarray, enhanced: np.ndarray, output_path: str, metrics: dict = None):
    """
    Generates a visual comparison report (HTML + side-by-side image).
    Follows 'original_name.recovered' convention for filenames.
    """
    # Create side-by-side comparison
    h, w = original.shape[:2]
    
    # Resize all to match enhanced size for fair comparison (or denoised to match enhanced)
    eh, ew = enhanced.shape[:2]
    
    orig_res = cv2.resize(original, (ew, eh), interpolation=cv2.INTER_NEAREST)
    denoised_res = cv2.resize(denoised, (ew, eh), interpolation=cv2.INTER_NEAREST)
    
    # Add labels
    def add_label(img, text):
        img_copy = img.copy()
        cv2.putText(img_copy, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return img_copy

    comparison = np.hstack([
        add_label(orig_res, "Original"),
        add_label(denoised_res, "Denoised"),
        add_label(enhanced, "AI Enhanced")
    ])
    
    # Save the comparison image
    img_filename = f"{os.path.basename(output_path)}.comparison.jpg"
    img_path = os.path.join(os.path.dirname(output_path), img_filename)
    cv2.imwrite(img_path, comparison)
    
    # Generate HTML report
    html_content = f"""
    <html>
    <head>
        <title>Recovery Report - {os.path.basename(output_path)}</title>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            .comparison-img {{ max-width: 100%; border: 1px solid #ccc; }}
            .metrics {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>Recovery Report: {os.path.basename(output_path)}</h1>
        <p>This report shows the progression of the data recovery process.</p>
        
        <h2>Visual Comparison</h2>
        <img src="{img_filename}" class="comparison-img">
        
        <h2>Metrics</h2>
        <div class="metrics">
            <ul>
    """
    
    if metrics:
        for k, v in metrics.items():
            html_content += f"<li><strong>{k}:</strong> {v:.4f}</li>"
    else:
        html_content += "<li>No metrics available.</li>"
        
    html_content += """
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"Visual report saved to: {output_path}")

if __name__ == "__main__":
    import sys
    if "--test-visual" in sys.argv:
        # Create dummy data for testing
        test_orig = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.putText(test_orig, "Test", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        test_denoised = test_orig.copy()
        test_enhanced = cv2.resize(test_orig, (200, 200), interpolation=cv2.INTER_CUBIC)
        
        test_metrics = {"PSNR": 35.5, "SSIM": 0.98}
        
        # Follow original_name.recovered convention
        report_path = "test_image.recovered.html"
        save_visual_report(test_orig, test_denoised, test_enhanced, report_path, test_metrics)
        
        if os.path.exists(report_path) and os.path.exists("test_image.recovered.html.comparison.jpg"):
            print("Visual reporting test PASSED.")
            # Cleanup
            os.remove(report_path)
            os.remove("test_image.recovered.html.comparison.jpg")
        else:
            print("Visual reporting test FAILED.")
            sys.exit(1)
    else:
        # Test summary logic
        test_results = [
            {"offset": 0, "identification": {"type": "jpeg", "source": "signature"}},
            {"offset": 512, "identification": {"type": "jpeg", "source": "ai"}},
            {"offset": 1024, "identification": {"type": "other", "source": "ai_low_confidence"}},
            {"offset": 1536, "identification": {"type": "pdf", "source": "signature"}}
        ]
        summary = generate_carving_summary(test_results)
        print(f"Test Summary: {summary}")
        assert summary["total_fragments"] == 4
        assert summary["jpeg"]["total"] == 2
        assert summary["pdf"]["total"] == 1
        assert summary["other"] == 1
        print("Reporting logic test PASSED.")
