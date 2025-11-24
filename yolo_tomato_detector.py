#!/usr/bin/env python3
"""
YOLO TOMATO DETECTOR - OPTIMIZED for Raspberry Pi!
Only detects actual tomatoes - ignores walls, shirts, backgrounds!
"""

from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import time

print("=" * 70)
print("🍅 YOLO TOMATO DETECTOR - OPTIMIZED VERSION")
print("=" * 70)
print()
print("This uses your trained YOLO model!")
print("✅ Only detects actual tomatoes")
print("✅ Ignores walls, shirts, backgrounds")
print("✅ Classifies as ripe or unripe")
print("✅ OPTIMIZED for faster FPS on Raspberry Pi!")
print()
print("Press 'q' to quit")
print()

# Path to your trained model
MODEL_PATH = "best.pt"  # Your trained model from yolo-train/my_model/train/weights/
# MODEL_PATH = "model.pt"  # Alternative name if you renamed it

print(f"📦 Loading YOLO model: {MODEL_PATH}")
print("This may take 30-60 seconds on Raspberry Pi...")
print()

try:
    # Load your trained YOLO model
    model = YOLO(MODEL_PATH)
    print("✅ Model loaded successfully!")
    print()
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print()
    print("Make sure model.pt is in the same folder as this script!")
    print("Or update MODEL_PATH variable above.")
    exit(1)

# Get class names from model
class_names = model.names
print(f"📋 Detection classes: {class_names}")
print()

# Initialize Pi Camera - sweet spot resolution
print("📷 Initializing camera...")
camera = Picamera2()
# Sweet spot: good enough for detection, small enough for speed
config = camera.create_preview_configuration(
    main={"size": (320, 240)}  # Sweet spot for speed + accuracy
)
camera.configure(config)
camera.start()
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
frame_count = 0
start_time = time.time()

# Frame skipping for speed - SWEET SPOT
SKIP_FRAMES = 2  # Process every 3rd frame (sweet spot)
skip_counter = 0
last_results = None

try:
    while True:
        # Capture frame
        frame = camera.capture_array()

        # Convert RGB to BGR for OpenCV
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Only run detection every SKIP_FRAMES frames
        if skip_counter % (SKIP_FRAMES + 1) == 0:
            # Run YOLO detection with SWEET SPOT settings
            results = model.predict(
                display_frame,
                verbose=False,
                imgsz=320,  # Match camera size for speed
                conf=0.45,  # Balanced confidence
                iou=0.45,   # Standard IOU
                half=False, # Don't use FP16 (not supported on Pi CPU)
                device='cpu',  # Explicitly use CPU
                max_det=10  # Allow 10 detections
            )
            last_results = results
        else:
            # Reuse last detection results
            results = last_results if last_results else []

        skip_counter += 1

        # Process detections
        detections_this_frame = 0
        frame_count += 1

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

                    # Draw bounding box (thinner line for speed)
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 1)

                    # Create label with confidence
                    label = f"{class_name} {confidence:.2f}"

                    # Draw label text (simplified - no background for speed)
                    cv2.putText(
                        display_frame,
                        label,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,  # Smaller font
                        color,
                        1  # Thinner text
                    )

        # Calculate FPS
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        # Add statistics overlay (simplified for speed)
        cv2.putText(
            display_frame,
            f"FPS: {fps:.1f} | Det: {detections_this_frame}",
            (5, 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 255, 255),
            1
        )

        cv2.putText(
            display_frame,
            f"Ripe: {ripe_count} | Unripe: {unripe_count}",
            (5, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )

        # Upscale for display (2x)
        display_frame = cv2.resize(display_frame, (640, 480), interpolation=cv2.INTER_NEAREST)

        # Show frame
        cv2.imshow('YOLO Tomato Detector', display_frame)

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
    camera.stop()
    camera.close()
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
