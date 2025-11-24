#!/usr/bin/env python3
"""
YOLO TOMATO DETECTOR - Docker Compatible Version
Uses OpenCV VideoCapture instead of picamera2
"""

from ultralytics import YOLO
import cv2
import time

print("=" * 70)
print("🍅 YOLO TOMATO DETECTOR - DOCKER VERSION")
print("=" * 70)
print()
print("This uses your trained YOLO model!")
print("✅ Only detects actual tomatoes")
print("✅ Ignores walls, shirts, backgrounds")
print("✅ Classifies as ripe or unripe")
print()
print("Press 'q' to quit")
print()

# Path to your trained model
MODEL_PATH = "/workspace/best.pt"

print(f"📦 Loading YOLO model: {MODEL_PATH}")
print("This may take 30-60 seconds...")
print()

try:
    # Load your trained YOLO model
    model = YOLO(MODEL_PATH)
    print("✅ Model loaded successfully!")
    print()
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print()
    print("Make sure best.pt is in the workspace folder!")
    exit(1)

# Get class names from model
class_names = model.names
print(f"📋 Detection classes: {class_names}")
print()

# Initialize Camera with OpenCV
print("📷 Initializing camera...")
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(2)
print("✅ Camera ready!")
print()

print("🎯 Starting live detection...")
print("="*70)
print()

# Statistics
total_detections = 0
ripe_count = 0
unripe_count = 0

try:
    while True:
        # Capture frame
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Run YOLO detection
        results = model(frame, verbose=False)

        # Process detections
        detections_this_frame = 0

        for result in results:
            boxes = result.boxes

            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Get confidence and class
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = class_names[class_id]

                # Only show detections above 50% confidence
                if confidence > 0.5:
                    detections_this_frame += 1
                    total_detections += 1

                    # Count by class
                    if "ripe" in class_name.lower():
                        ripe_count += 1
                        color = (0, 0, 255)  # Red for ripe
                    elif "unripe" in class_name.lower():
                        unripe_count += 1
                        color = (0, 255, 0)  # Green for unripe
                    else:
                        color = (255, 0, 255)  # Magenta for others

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    # Create label with confidence
                    label = f"{class_name} {confidence:.2f}"

                    # Get label size
                    (label_w, label_h), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                    )

                    # Draw label background
                    cv2.rectangle(
                        frame,
                        (x1, y1 - label_h - 10),
                        (x1 + label_w, y1),
                        color,
                        -1
                    )

                    # Draw label text
                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 255),
                        2
                    )

        # Add statistics overlay
        stats_y = 30
        cv2.putText(
            frame,
            f"Detected: {detections_this_frame} tomatoes",
            (10, stats_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        stats_y += 30
        cv2.putText(
            frame,
            f"Total - Ripe: {ripe_count} | Unripe: {unripe_count}",
            (10, stats_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # Add instructions
        cv2.putText(
            frame,
            "Press 'q' to quit",
            (10, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # Show frame
        cv2.imshow('YOLO Tomato Detector', frame)

        # Check for quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Final statistics
    print()
    print("=" * 70)
    print("DETECTION SESSION SUMMARY")
    print("=" * 70)
    print(f"Total detections: {total_detections}")
    print(f"  Ripe tomatoes: {ripe_count}")
    print(f"  Unripe tomatoes: {unripe_count}")
    print("=" * 70)

except KeyboardInterrupt:
    print("\n\nStopped by user (Ctrl+C)")

finally:
    camera.release()
    cv2.destroyAllWindows()
    print("\n✅ Camera closed. Goodbye!")
    print()
    print("🎉 YOLO detection complete!")
    print()
    print("COMPARISON TO OLD SYSTEM:")
    print("  ❌ Old: Detected walls, shirts, backgrounds")
    print("  ✅ New: Only detects actual tomatoes!")
    print()
    print("Great job! 🍅")
