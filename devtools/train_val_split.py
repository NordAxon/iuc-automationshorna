import shutil
import random
from pathlib import Path

def split_dataset(source_dir: str, output_dir: str, train_split: float = 0.8) -> None:
    """
    Split dataset into train and validation sets.
    
    Args:
        source_dir: Directory containing 'defective' and 'non-defective' folders
        output_dir: Directory where train and validation splits will be created
        train_split: Fraction of data to use for training (default: 0.8)
    """
    # Create output directory structure
    output_path = Path(output_dir)
    for split in ['train', 'val']:
        for class_name in ['defective', 'non-defective']:
            (output_path / split / class_name).mkdir(parents=True, exist_ok=True)
    
    # Process each class
    for class_name in ['defective', 'non-defective']:
        # Get all images in the class
        source_path = Path(source_dir) / class_name
        image_files = list(source_path.glob('*.jpg')) + list(source_path.glob('*.JPG')) + list(source_path.glob('*.png'))
        
        # Shuffle images
        random.shuffle(image_files)
        
        # Calculate split point
        split_idx = int(len(image_files) * train_split)
        train_files = image_files[:split_idx]
        val_files = image_files[split_idx:]
        
        # Copy files to respective directories
        for file in train_files:
            shutil.copy2(file, output_path / 'train' / class_name / file.name)
        
        for file in val_files:
            shutil.copy2(file, output_path / 'val' / class_name / file.name)
        
        print(f"{class_name}: {len(train_files)} training, {len(val_files)} validation images")

if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    
    # Configure paths
    source_directory = "data/set_1"  # Contains 'defective' and 'non-defective' folders
    output_directory = "data/set_1/split"  # Where train/val splits will be created
    
    split_dataset(source_directory, output_directory)
