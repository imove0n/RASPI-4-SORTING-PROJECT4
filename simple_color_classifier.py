#!/usr/bin/env python3
"""
Simple Color-Based Tomato Classifier
Uses OpenCV HSV color detection - works immediately without training!
Perfect for testing while you collect dataset for YOLO
"""

from picamera2 import Picamera2
import cv2
import numpy as np
import time

print("=" * 70)
print("SIMPLE TOMATO COLOR CLASSIFIER")
print("=" * 70)
print()
print("This classifies tomatoes based on color:")
print("  GREEN -> Unripe")
print("  RED/ORANGE -> Ripe")
print("  DARK RED -> Overripe")
print()
print("Place tomato in view and press SPACE to classify")
print("Press 'q' to quit")
print()

# Initialize camera
camera = Picamera2()
config = camera.create_preview_configuration(
    main={"size": (640, 480)}
)
camera.configure(config)
camera.start()
time.sleep(2)

def classify_tomato(image):
    """
    Classify tomato based on dominant color in HSV space
    Returns: category, confidence, color_info
    """
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Define color ranges in HSV
    # Green (Unripe)
    green_lower1 = np.array([35, 40, 40])
    green_upper1 = np.array([85, 255, 255])

    # Red (Ripe) - red wraps around in HSV
    red_lower1 = np.array([0, 100, 100])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 100, 100])
    red_upper2 = np.array([180, 255, 255])

    # Dark Red (Overripe)
    dark_red_lower = np.array([0, 100, 20])
    dark_red_upper = np.array([10, 255, 100])

    # Create masks
    mask_green = cv2.inRange(hsv, green_lower1, green_upper1)
    mask_red1 = cv2.inRange(hsv, red_lower1, red_upper1)
    mask_red2 = cv2.inRange(hsv, red_lower2, red_upper2)
    mask_red = cv2.bitwise_or(mask_red1, mask_red2)
    mask_dark_red = cv2.inRange(hsv, dark_red_lower, dark_red_upper)

    # Count pixels in each category
    green_pixels = cv2.countNonZero(mask_green)
    red_pixels = cv2.countNonZero(mask_red)
    dark_red_pixels = cv2.countNonZero(mask_dark_red)

    total_colored = green_pixels + red_pixels + dark_red_pixels

    if total_colored == 0:
        return "Unknown", 0, "No tomato detected"

    # Calculate percentages
    green_pct = (green_pixels / total_colored) * 100
    red_pct = (red_pixels / total_colored) * 100
    dark_red_pct = (dark_red_pixels / total_colored) * 100

    # Classify based on dominant color
    if dark_red_pct > 40:
        return "Overripe", dark_red_pct, f"Dark Red: {dark_red_pct:.1f}%"
    elif green_pct > 50:
        return "Unripe", green_pct, f"Green: {green_pct:.1f}%"
    elif red_pct > 40:
        return "Ripe", red_pct, f"Red: {red_pct:.1f}%"
    elif green_pct > red_pct:
        return "Unripe", green_pct, f"Green: {green_pct:.1f}% (partial)"
    else:
        return "Ripe", red_pct, f"Red: {red_pct:.1f}% (partial)"


print("Camera ready! Position tomato and press SPACE to classify...")
print()

try:
    count_unripe = 0
    count_ripe = 0
    count_overripe = 0

    while True:
        # Capture frame
        frame = camera.capture_array()

        # Show live preview (if display available)
        print("Press SPACE to classify, 'q' to quit...", end='\r')

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            # Classify tomato
            print("\n" + "=" * 70)
            print("CLASSIFYING...")
            category, confidence, color_info = classify_tomato(frame)

            print(f"\nResult: {category.upper()}")
            print(f"Confidence: {confidence:.1f}%")
            print(f"Color Analysis: {color_info}")

            # Update counts
            if category == "Unripe":
                count_unripe += 1
            elif category == "Ripe":
                count_ripe += 1
            elif category == "Overripe":
                count_overripe += 1

            print()
            print(f"Session Counts: Unripe={count_unripe}, Ripe={count_ripe}, Overripe={count_overripe}")
            print("=" * 70)
            print()
            print("Ready for next tomato...")

        elif key == ord('q'):
            break

        time.sleep(0.1)

    print("\n" + "=" * 70)
    print("FINAL COUNTS")
    print("=" * 70)
    print(f"Unripe:   {count_unripe}")
    print(f"Ripe:     {count_ripe}")
    print(f"Overripe: {count_overripe}")
    print(f"Total:    {count_unripe + count_ripe + count_overripe}")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\nStopped by user")

finally:
    camera.stop()
    camera.close()
    cv2.destroyAllWindows()
    print("Camera closed. Goodbye!")
