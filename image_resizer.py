#!/usr/bin/env python3
"""
Image Resizer Script
Creates medium and thumbnail versions of JPG images in a folder.
"""

import os
import sys
from pathlib import Path
from PIL import Image

# Configuration
MEDIUM_SIZE = (800, 600)  # Medium image dimensions
THUMBNAIL_SIZE = (150, 150)  # Thumbnail dimensions
QUALITY = 85  # JPEG quality (1-100)

def resize_image(input_path, output_path, size, maintain_aspect=True):
    """
    Resize an image to the specified size.
    
    Args:
        input_path: Path to the input image
        output_path: Path where resized image will be saved
        size: Tuple of (width, height) for the new size
        maintain_aspect: Whether to maintain aspect ratio
    """
    try:
        with Image.open(input_path) as img:
            if maintain_aspect:
                # Use thumbnail method to maintain aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                # Resize to exact dimensions (may distort image)
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary (handles RGBA, P mode images)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save the resized image
            img.save(output_path, 'JPEG', quality=QUALITY, optimize=True)
            print(f"✓ Created: {output_path}")
            
    except Exception as e:
        print(f"✗ Error processing {input_path}: {str(e)}")

def process_folder(folder_path):
    """
    Process all JPG files in the specified folder.
    
    Args:
        folder_path: Path to the folder containing JPG files
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory.")
        return
    
    # No need to create separate directories - saving in same folder
    
    # Find all JPG files (case insensitive)
    jpg_extensions = ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']
    jpg_files = []
    
    for ext in jpg_extensions:
        jpg_files.extend(folder.glob(ext))
    
    if not jpg_files:
        print(f"No JPG files found in '{folder_path}'")
        return
    
    print(f"Found {len(jpg_files)} JPG files to process...")
    print(f"Resized images will be saved in the same folder with '_med' and '_thumb' suffixes.")
    print()
    
    # Process each JPG file
    for jpg_file in jpg_files:
        base_name = jpg_file.stem
        
        # Create output paths in the same directory
        medium_path = jpg_file.parent / f"{base_name}_med.jpg"
        thumbnail_path = jpg_file.parent / f"{base_name}_thumb.jpg"
        
        # Create medium version
        resize_image(jpg_file, medium_path, MEDIUM_SIZE)
        
        # Create thumbnail version
        resize_image(jpg_file, thumbnail_path, THUMBNAIL_SIZE)
    
    print(f"\nProcessing complete! Processed {len(jpg_files)} images.")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) != 2:
        print("Usage: python image_resizer.py <folder_path>")
        print("Example: python image_resizer.py /path/to/images")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    process_folder(folder_path)

if __name__ == "__main__":
    main()
