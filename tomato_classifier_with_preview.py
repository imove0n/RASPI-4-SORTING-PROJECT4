#!/usr/bin/env python3
"""
TOMATO CLASSIFIER WITH LIVE PREVIEW WINDOW
Shows what camera sees + classifications
EASY TO USE!
"""

from picamera2 import Picamera2
import cv2
import numpy as np
import time
import os

# Create folder to save images
SAVE_FOLDER = "/home/bacadasa/Desktop/RASPI 4 SORTING PROJECT/classified_tomatoes"
os.makedirs(SAVE_FOLDER, exist_ok=True)

print("=" * 70)
print("TOMATO CLASSIFIER WITH LIVE PREVIEW")
print("=" * 70)
print()
print("CLASSIFICATION RULES:")
print("  UNRIPE = ANY green visible (light green, semi-green, whole green)")
print("  RIPE   = Red/Dark red/Orange ONLY (NO green parts!)")
print("  ROTTEN = Dots/Bites/Black spots/Damage (REJECT!)")
print()
print("INSTRUCTIONS:")
print("1. A window will open showing what camera sees")
print("2. Place tomato in front of camera")
print("3. Press SPACE to classify the tomato")
print("4. Result will show on screen AND save image")
print("5. Press 'q' to quit")
print()
print("Images will be saved to:")
print(f"  {SAVE_FOLDER}")
print()
print("Starting camera...")

# Initialize camera
camera = Picamera2()
config = camera.create_preview_configuration(
    main={"size": (640, 480)}
)
camera.configure(config)
camera.start()
time.sleep(2)

print("[OK] Camera started!")
print()
print("PREVIEW WINDOW OPENING...")
print("(If you don't see window, check if it's behind other windows)")
print()

def classify_tomato(image):
    """
    Classify tomato:
    - RIPE = Red/Dark red/Orange/Yellow-orange (ready to sell!)
    - UNRIPE = Green/Light green (not ready)
    - ROTTEN = Dots/Bites/Black spots/Damage (REJECT!)
    """
    # Convert to HSV for color detection
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Define color ranges
    # Green (Unripe) - includes light green, semi-green
    # Lower threshold to catch light green better
    green_lower = np.array([30, 20, 20])  # Catch lighter greens
    green_upper = np.array([90, 255, 255])  # Wider range

    # RIPE colors - ONLY Red and Dark Red (NO yellow-orange if has green)
    # Red (dark to bright)
    red_lower1 = np.array([0, 50, 50])  # Higher saturation = true red only
    red_upper1 = np.array([8, 255, 255])
    # Red (upper hue range)
    red_lower2 = np.array([165, 50, 50])
    red_upper2 = np.array([180, 255, 255])
    # Orange (only deep orange, not yellow-orange)
    orange_lower = np.array([8, 80, 80])  # Higher saturation
    orange_upper = np.array([20, 255, 255])

    # Create masks
    mask_green = cv2.inRange(hsv, green_lower, green_upper)
    mask_red1 = cv2.inRange(hsv, red_lower1, red_upper1)
    mask_red2 = cv2.inRange(hsv, red_lower2, red_upper2)
    mask_orange = cv2.inRange(hsv, orange_lower, orange_upper)

    # Combine all RIPE colors
    mask_ripe = cv2.bitwise_or(mask_red1, mask_red2)
    mask_ripe = cv2.bitwise_or(mask_ripe, mask_orange)

    # Detect ROTTEN - black spots, dots, bites
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    # Detect very dark spots (black spots, rot)
    _, black_spots = cv2.threshold(blurred, 40, 255, cv2.THRESH_BINARY_INV)

    # Detect irregular patterns (dots, bites)
    edges = cv2.Canny(blurred, 50, 150)

    # Count pixels
    green_pixels = cv2.countNonZero(mask_green)
    ripe_pixels = cv2.countNonZero(mask_ripe)
    black_pixels = cv2.countNonZero(black_spots)
    edge_pixels = cv2.countNonZero(edges)

    total_colored = green_pixels + ripe_pixels

    if total_colored == 0:
        return "Unknown", 0, (255, 255, 255)

    # Calculate percentages
    green_pct = (green_pixels / total_colored) * 100
    ripe_pct = (ripe_pixels / total_colored) * 100

    total_pixels = image.shape[0] * image.shape[1]
    black_pct = (black_pixels / total_pixels) * 100
    edge_pct = (edge_pixels / total_pixels) * 100

    # Classification logic
    # ROTTEN = Has black spots, dots, bites, damage
    if black_pct > 20:  # Lots of black spots = ROTTEN
        return "Rotten", black_pct, (64, 0, 64)  # Dark purple

    elif edge_pct > 25:  # Too many irregular edges = damaged/bitten
        return "Rotten", edge_pct, (64, 0, 64)

    # UNRIPE = Any green visible (light green, semi-green, whole green)
    # If tomato has ANY significant green = UNRIPE!
    elif green_pct > 20:  # Even 20% green = still unripe!
        return "Unripe", green_pct, (0, 255, 0)  # Green

    # RIPE = Red/Dark red/Orange ONLY (and NO green!)
    # Need higher threshold to be sure it's truly ripe
    elif ripe_pct > 60:  # Must be mostly ripe color
        return "Ripe", ripe_pct, (0, 0, 255)  # Red

    # If has some ripe but not enough, still mixed
    elif ripe_pct > 30 and green_pct < 10:  # Some ripe, very little green
        return "Ripe", ripe_pct, (0, 0, 255)

    # Default: if not clearly ripe and has any green = UNRIPE
    elif green_pct >= ripe_pct:
        return "Unripe", green_pct, (0, 255, 0)
    else:
        # Mostly ripe color
        return "Ripe", ripe_pct, (0, 0, 255)


# Counters
count_unripe = 0
count_ripe = 0
count_rotten = 0
total_classified = 0

try:
    while True:
        # Capture frame
        frame = camera.capture_array()

        # Convert RGB to BGR for OpenCV display
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Add text instructions on image
        cv2.putText(display_frame, "Press SPACE to classify tomato",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(display_frame, "Press 'q' to quit",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Show counts
        cv2.putText(display_frame, f"Unripe: {count_unripe}  Ripe: {count_ripe}  Rotten: {count_rotten}",
                    (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        # Show preview window
        cv2.imshow('Tomato Classifier - Live Preview', display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            # Classify!
            print("\n" + "=" * 70)
            print("CLASSIFYING TOMATO...")

            category, confidence, color = classify_tomato(display_frame)

            print(f"\nRESULT: {category.upper()}")
            print(f"Confidence: {confidence:.1f}%")

            # Update counts
            if category == "Unripe":
                count_unripe += 1
            elif category == "Ripe":
                count_ripe += 1
            elif category == "Rotten":
                count_rotten += 1

            total_classified += 1

            # Save image with classification
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{category}_{timestamp}.jpg"
            filepath = os.path.join(SAVE_FOLDER, filename)

            # Draw result on image
            result_frame = display_frame.copy()
            cv2.putText(result_frame, f"{category.upper()} - {confidence:.1f}%",
                        (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)

            cv2.imwrite(filepath, result_frame)
            print(f"\nImage saved: {filename}")
            print(f"Location: {SAVE_FOLDER}")

            print()
            print(f"Total classified: {total_classified}")
            print(f"  Unripe: {count_unripe}")
            print(f"  Ripe:   {count_ripe}")
            print(f"  Rotten: {count_rotten}")
            print("=" * 70)
            print()

            # Show result for 2 seconds
            cv2.imshow('Tomato Classifier - Live Preview', result_frame)
            cv2.waitKey(2000)

        elif key == ord('q'):
            break

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Total classified: {total_classified}")
    print(f"  Unripe: {count_unripe}")
    print(f"  Ripe:   {count_ripe}")
    print(f"  Rotten: {count_rotten}")
    print()
    print(f"All images saved to:")
    print(f"  {SAVE_FOLDER}")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\nStopped by user")

finally:
    camera.stop()
    camera.close()
    cv2.destroyAllWindows()
    print("\nCamera closed. Goodbye!")
