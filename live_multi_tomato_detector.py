#!/usr/bin/env python3
"""
LIVE MULTI-TOMATO DETECTOR
Detects and classifies MULTIPLE tomatoes in real-time
Shows boxes and labels for each tomato
"""

from picamera2 import Picamera2
import cv2
import numpy as np
import time

print("=" * 70)
print("LIVE MULTI-TOMATO DETECTOR")
print("=" * 70)
print()
print("This will detect and classify MULTIPLE tomatoes at once!")
print("Each tomato gets its own box and label")
print()
print("CLASSIFICATION RULES:")
print("  UNRIPE = Green color (box: GREEN)")
print("  RIPE   = Red/Orange color (box: RED)")
print("  ROTTEN = Black spots/damage (box: PURPLE)")
print()
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

print("[OK] Camera started!")
print("Starting live detection...")
print()

def classify_region(roi):
    """
    Classify a single tomato region (ROI)
    Returns: category, confidence
    """
    # Convert to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # Green detection
    green_lower = np.array([30, 20, 20])
    green_upper = np.array([90, 255, 255])
    mask_green = cv2.inRange(hsv, green_lower, green_upper)

    # Red/Orange detection
    red_lower1 = np.array([0, 50, 50])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 50, 50])
    red_upper2 = np.array([180, 255, 255])
    orange_lower = np.array([8, 60, 60])
    orange_upper = np.array([25, 255, 255])

    mask_red1 = cv2.inRange(hsv, red_lower1, red_upper1)
    mask_red2 = cv2.inRange(hsv, red_lower2, red_upper2)
    mask_orange = cv2.inRange(hsv, orange_lower, orange_upper)
    mask_ripe = cv2.bitwise_or(mask_red1, mask_red2)
    mask_ripe = cv2.bitwise_or(mask_ripe, mask_orange)

    # Black spot detection (rotten)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)
    _, black_spots = cv2.threshold(blurred, 40, 255, cv2.THRESH_BINARY_INV)

    # Count pixels
    green_pixels = cv2.countNonZero(mask_green)
    ripe_pixels = cv2.countNonZero(mask_ripe)
    black_pixels = cv2.countNonZero(black_spots)

    total_colored = green_pixels + ripe_pixels
    if total_colored == 0:
        return "Unknown", 0

    green_pct = (green_pixels / total_colored) * 100
    ripe_pct = (ripe_pixels / total_colored) * 100
    total_pixels = roi.shape[0] * roi.shape[1]
    black_pct = (black_pixels / total_pixels) * 100

    # Classify
    if black_pct > 20:
        return "Rotten", black_pct
    elif green_pct > 20:
        return "Unripe", green_pct
    elif ripe_pct > 30:
        return "Ripe", ripe_pct
    elif green_pct >= ripe_pct:
        return "Unripe", green_pct
    else:
        return "Ripe", ripe_pct


def detect_tomatoes(frame):
    """
    Detect all tomatoes in frame
    Returns list of (x, y, w, h, category, confidence)
    """
    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create mask for all tomato colors (red, orange, green)
    # Red
    red_lower1 = np.array([0, 30, 30])
    red_upper1 = np.array([10, 255, 255])
    red_lower2 = np.array([160, 30, 30])
    red_upper2 = np.array([180, 255, 255])
    # Orange
    orange_lower = np.array([8, 30, 30])
    orange_upper = np.array([30, 255, 255])
    # Green
    green_lower = np.array([25, 20, 20])
    green_upper = np.array([95, 255, 255])

    # Combine all masks
    mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
    mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
    mask3 = cv2.inRange(hsv, orange_lower, orange_upper)
    mask4 = cv2.inRange(hsv, green_lower, green_upper)

    combined_mask = cv2.bitwise_or(mask1, mask2)
    combined_mask = cv2.bitwise_or(combined_mask, mask3)
    combined_mask = cv2.bitwise_or(combined_mask, mask4)

    # Clean up mask
    kernel = np.ones((5, 5), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)

    # Find contours (tomato shapes)
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for contour in contours:
        area = cv2.contourArea(contour)

        # Filter by size (ignore small noise, ignore huge blobs)
        if area > 2000 and area < 150000:  # Adjust these based on your setup
            x, y, w, h = cv2.boundingRect(contour)

            # Extract region of interest
            roi = frame[y:y+h, x:x+w]

            # Classify this tomato
            category, confidence = classify_region(roi)

            detections.append((x, y, w, h, category, confidence))

    return detections


# Statistics
total_detections = 0

try:
    while True:
        # Capture frame
        frame = camera.capture_array()
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Detect all tomatoes
        detections = detect_tomatoes(display_frame)

        # Draw boxes and labels for each tomato
        for (x, y, w, h, category, confidence) in detections:
            # Choose color based on category
            if category == "Unripe":
                color = (0, 255, 0)  # Green
            elif category == "Ripe":
                color = (0, 0, 255)  # Red
            elif category == "Rotten":
                color = (128, 0, 128)  # Purple
            else:
                color = (200, 200, 200)  # Gray

            # Draw rectangle around tomato
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), color, 3)

            # Create label
            label = f"{category} {confidence:.0f}%"

            # Get label size for background
            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)

            # Draw label background
            cv2.rectangle(display_frame, (x, y - label_h - 10), (x + label_w, y), color, -1)

            # Draw label text
            cv2.putText(display_frame, label, (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Show count at top
        count_text = f"Detected: {len(detections)} tomatoes"
        cv2.putText(display_frame, count_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

        # Instructions
        cv2.putText(display_frame, "Press 'q' to quit", (10, 460),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Show live video
        cv2.imshow('Live Multi-Tomato Detector', display_frame)

        # Check for quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

        total_detections += len(detections)

    print("\n" + "=" * 70)
    print("DETECTION SESSION ENDED")
    print("=" * 70)
    print(f"Total detections made: {total_detections}")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\nStopped by user")

finally:
    camera.stop()
    camera.close()
    cv2.destroyAllWindows()
    print("\nCamera closed. Goodbye!")
