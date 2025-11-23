#!/usr/bin/env python3
"""
Tomato Dataset Collection Tool
Captures images of tomatoes for YOLO training
"""

from picamera2 import Picamera2
import cv2
import time
import os
from datetime import datetime

# Create dataset folders
DATASET_DIR = "/home/bacadasa/Desktop/RASPI 4 SORTING PROJECT/tomato_dataset"
RIPE_DIR = os.path.join(DATASET_DIR, "ripe")
UNRIPE_DIR = os.path.join(DATASET_DIR, "unripe")
OVERRIPE_DIR = os.path.join(DATASET_DIR, "overripe")
DEFECT_DIR = os.path.join(DATASET_DIR, "defect")

# Create directories
for folder in [RIPE_DIR, UNRIPE_DIR, OVERRIPE_DIR, DEFECT_DIR]:
    os.makedirs(folder, exist_ok=True)

print("=" * 70)
print("TOMATO DATASET COLLECTION TOOL FOR YOLO TRAINING")
print("=" * 70)
print()
print("This tool helps you capture images of tomatoes for training.")
print()
print("INSTRUCTIONS:")
print("1. Place ONE tomato in front of camera")
print("2. Choose category (ripe/unripe/overripe/defect)")
print("3. Take photos from different angles (at least 10-20 per tomato)")
print("4. Rotate tomato between shots")
print("5. Vary lighting and distance slightly")
print()
print("Dataset will be saved to:")
print(f"  {DATASET_DIR}")
print()
print("-" * 70)

# Initialize camera
print("\nInitializing camera...")
camera = Picamera2()
config = camera.create_preview_configuration(
    main={"size": (1920, 1080)},
    lores={"size": (640, 480)}
)
camera.configure(config)
camera.start()
time.sleep(2)
print("[OK] Camera ready!")
print()

def get_category():
    """Ask user which category"""
    print("\nSelect tomato category:")
    print("  1 = Ripe (red, ready to eat)")
    print("  2 = Unripe (green, not ready)")
    print("  3 = Overripe (very soft, dark red)")
    print("  4 = Defect (damaged, rotten)")
    print("  q = Quit")

    while True:
        choice = input("\nEnter choice (1/2/3/4/q): ").strip().lower()
        if choice == '1':
            return 'ripe', RIPE_DIR
        elif choice == '2':
            return 'unripe', UNRIPE_DIR
        elif choice == '3':
            return 'overripe', OVERRIPE_DIR
        elif choice == '4':
            return 'defect', DEFECT_DIR
        elif choice == 'q':
            return None, None
        else:
            print("Invalid choice! Try again.")

def count_images(category_dir):
    """Count existing images in category"""
    return len([f for f in os.listdir(category_dir) if f.endswith('.jpg')])

try:
    session_count = 0

    while True:
        # Get category
        category, save_dir = get_category()

        if category is None:
            print("\nExiting dataset collection...")
            break

        # Count existing images
        existing_count = count_images(save_dir)
        print(f"\n[{category.upper()}] Currently have {existing_count} images")
        print()
        print("Place tomato in view and press ENTER to start capturing...")
        print("(or type 'back' to choose different category)")

        response = input().strip().lower()
        if response == 'back':
            continue

        print("\nStarting capture session!")
        print("Press ENTER to take photo, 'done' when finished with this tomato")
        print()

        photo_count = 0

        while True:
            command = input(f"Photo {photo_count + 1} - Press ENTER (or 'done'/'back'): ").strip().lower()

            if command == 'done':
                print(f"\n[OK] Captured {photo_count} images of {category} tomato")
                break
            elif command == 'back':
                break

            # Capture image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{category}_{timestamp}.jpg"
            filepath = os.path.join(save_dir, filename)

            # Capture and save
            camera.capture_file(filepath)
            photo_count += 1
            session_count += 1

            print(f"  [✓] Saved: {filename}")
            print(f"      Rotate tomato and press ENTER for next angle...")

        print()
        print("-" * 70)

    # Summary
    print()
    print("=" * 70)
    print("DATASET COLLECTION SUMMARY")
    print("=" * 70)
    print(f"Total images captured this session: {session_count}")
    print()
    print("Images by category:")
    print(f"  Ripe:     {count_images(RIPE_DIR)}")
    print(f"  Unripe:   {count_images(UNRIPE_DIR)}")
    print(f"  Overripe: {count_images(OVERRIPE_DIR)}")
    print(f"  Defect:   {count_images(DEFECT_DIR)}")
    print()
    print(f"Dataset location: {DATASET_DIR}")
    print()
    print("NEXT STEPS:")
    print("1. Aim for at least 10-20 images per tomato")
    print("2. At least 50-100 total images for good training")
    print("3. Run the YOLO training script when ready!")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\nInterrupted by user")

finally:
    camera.stop()
    camera.close()
    print("\nCamera closed. Goodbye!")
