"""
build_mega_dataset.py

This script is designed to download and organically combine two robust Kaggle datasets:
1. 'new-plant-diseases-dataset': 38 plant disease classes
2. 'fruits-fresh-and-rotten-for-classification': 6 fruit classes (fresh apple, rotten apple, etc.)

It automatically handles the folder merging so you can instantly train an incredibly
smart comprehensive local Keras Model via 'python train_model.py --data_dir mega_dataset'
"""

import os
import shutil
import kagglehub
from pathlib import Path

def setup_mega_dataset():
    mega_dir = Path("mega_dataset")
    train_out = mega_dir / "train"
    valid_out = mega_dir / "valid"

    # Make target directories
    train_out.mkdir(parents=True, exist_ok=True)
    valid_out.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Step 1: Downloading standard Plant Diseases dataset...")
    # 1. Download Plant Diseases
    plant_path = Path(kagglehub.dataset_download("vipoooool/new-plant-diseases-dataset"))
    
    # 2. Download Fruits Fresh/Rotten
    print("🚀 Step 2: Downloading Fresh & Rotten Fruits dataset...")
    fruit_path = Path(kagglehub.dataset_download("sriramr/fruits-fresh-and-rotten-for-classification"))
    
    # Function to copy inner directories into the mega directory
    def merge_into_mega(source_root: Path, target_base: Path, split_name: str="train"):
        # We need to find the specific Split Folder (train/valid/test) inside the downloaded asset
        split_dir = None
        for r, dirs, files in os.walk(source_root):
            if os.path.basename(r).lower() == split_name.lower():
                split_dir = Path(r)
                break
        
        if not split_dir:
            print(f"⚠️  Could not find '{split_name}' inside {source_root}")
            return
            
        print(f"📦 Merging {split_dir.parent.name}/{split_name} into mega directory...")
        for class_dir in split_dir.iterdir():
            if class_dir.is_dir():
                target_dir = target_base / split_name / class_dir.name
                target_dir.mkdir(parents=True, exist_ok=True)
                # Copy files over
                files_copied = 0
                for f in class_dir.iterdir():
                    if f.is_file() and f.suffix.lower() in [".jpg", ".png", ".jpeg"]:
                        try:
                            shutil.copy2(f, target_dir / f.name)
                            files_copied += 1
                        except:
                            pass
                print(f"   -> Copied {files_copied} images for class '{class_dir.name}'")

    print("\n🚀 Step 3: Merging Training Data...")
    merge_into_mega(plant_path, mega_dir, "train")
    merge_into_mega(fruit_path, mega_dir, "train")
    
    print("\n🚀 Step 4: Merging Validation (Testing) Data...")
    # Some datasets use 'valid', some use 'test'. We'll map them both to mega_dataset/valid
    merge_into_mega(plant_path, mega_dir, "valid")
    merge_into_mega(fruit_path, mega_dir, "test")

    print("\n✅ MEGA DATASET CREATED SUCCESSFULLY!")
    print(f"It is located at: {mega_dir.absolute()}")
    print("\nYou can now train the massive combined 44-class model locally using:")
    print("python train_model.py --data_dir mega_dataset --epochs 20")

if __name__ == "__main__":
    setup_mega_dataset()
