import os
import numpy as np

def generate_dummy_fragments(base_dir, label, count, seed):
    np.random.seed(seed)
    label_dir = os.path.join(base_dir, label)
    os.makedirs(label_dir, exist_ok=True)
    
    for i in range(count):
        # Generate some "structured" noise for different labels
        if label == "jpeg":
            # JPEG fragments often have high entropy but some patterns (e.g., FFD8 at start)
            data = np.random.randint(0, 256, 512, dtype=np.uint8)
            if i % 10 == 0:
                data[:2] = [0xFF, 0xD8] # Fake header
        elif label == "pdf":
            # PDF fragments often have ASCII text or %PDF
            data = np.random.randint(32, 127, 512, dtype=np.uint8) # ASCII range
            if i % 10 == 0:
                data[:4] = [0x25, 0x50, 0x44, 0x46] # %PDF
        else:
            # Other/Noise
            data = np.random.randint(0, 256, 512, dtype=np.uint8)
            
        with open(os.path.join(label_dir, f"{label}_dummy_{i:04d}.bin"), "wb") as f:
            f.write(data.tobytes())

if __name__ == "__main__":
    base_dir = "dataset/fragments"
    generate_dummy_fragments(base_dir, "jpeg", 100, 42)
    generate_dummy_fragments(base_dir, "pdf", 100, 43)
    generate_dummy_fragments(base_dir, "other", 100, 44)
    print(f"Generated 300 dummy fragments in {base_dir}")
