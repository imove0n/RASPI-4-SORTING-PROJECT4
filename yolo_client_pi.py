#!/usr/bin/env python3
"""
YOLO Client for Raspberry Pi
Sends camera images to PC for YOLO detection, displays results
"""

from picamera2 import Picamera2
import cv2
import requests
import numpy as np
import time
import io

print("=" * 70)
print("🍅 YOLO TOMATO DETECTOR - Pi Client")
print("=" * 70)
print()

# PC server address - UPDATE THIS with your PC's IP address
PC_SERVER_URL = "http://192.168.1.100:5000/detect"  # Change to your PC's IP
print(f"Connecting to PC server at: {PC_SERVER_URL}")
print()

# Initialize Pi Camera
print("📷 Initializing camera...")
camera = Picamera2()
config = camera.create_preview_configuration(main={"size": (640, 480)})
camera.configure(config)
camera.start()
time.sleep(2)
print("✅ Camera ready!")
print()

print("🎯 Starting live detection...")
print("Press 'q' to quit")
print("=" * 70)
print()

# Statistics
total_detections = 0
ripe_count = 0
unripe_count = 0

try:
    while True:
        # Capture frame
        frame = camera.capture_array()

        # Convert RGB to BGR for OpenCV
        display_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Encode image as JPEG
        _, img_encoded = cv2.imencode('.jpg', display_frame)

        try:
            # Send image to PC server
            response = requests.post(
                PC_SERVER_URL,
                files={'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')},
                timeout=2
            )

            if response.status_code == 200:
                results = response.json()
                detections = results.get('detections', [])

                detections_this_frame = len(detections)

                # Draw detections
                for det in detections:
                    x1, y1, x2, y2 = det['bbox']
                    class_name = det['class']
                    confidence = det['confidence']

                    total_detections += 1

                    # Count by class
                    if "ripe" in class_name.lower() and "unripe" not in class_name.lower():
                        ripe_count += 1
                        color = (0, 0, 255)  # Red for ripe
                    elif "unripe" in class_name.lower():
                        unripe_count += 1
                        color = (0, 255, 0)  # Green for unripe
                    else:
                        color = (255, 0, 255)  # Magenta for others

                    # Draw bounding box
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)

                    # Create label
                    label = f"{class_name} {confidence:.2f}"

                    # Get label size
                    (label_w, label_h), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                    )

                    # Draw label background
                    cv2.rectangle(
                        display_frame,
                        (x1, y1 - label_h - 10),
                        (x1 + label_w, y1),
                        color,
                        -1
                    )

                    # Draw label text
                    cv2.putText(
                        display_frame,
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
                    display_frame,
                    f"Detected: {detections_this_frame} tomatoes",
                    (10, stats_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                stats_y += 30
                cv2.putText(
                    display_frame,
                    f"Total - Ripe: {ripe_count} | Unripe: {unripe_count}",
                    (10, stats_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
            else:
                # Server error
                cv2.putText(
                    display_frame,
                    "Server Error",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2
                )

        except requests.exceptions.RequestException as e:
            # Connection error
            cv2.putText(
                display_frame,
                f"Cannot connect to PC: {PC_SERVER_URL}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )
            cv2.putText(
                display_frame,
                "Make sure PC server is running!",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                2
            )

        # Add instructions
        cv2.putText(
            display_frame,
            "Press 'q' to quit",
            (10, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # Show frame
        cv2.imshow('YOLO Tomato Detector (Pi + PC)', display_frame)

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
