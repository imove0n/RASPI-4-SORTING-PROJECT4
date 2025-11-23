#!/usr/bin/env python3
"""
Pi Camera v2 Test Script
Simple test to verify camera is working
"""

from picamera2 import Picamera2
import time

print("=" * 60)
print("PI CAMERA v2 TEST")
print("=" * 60)
print()

try:
    print("[1/4] Initializing camera...")
    camera = Picamera2()
    print("    [OK] Camera object created")

    print()
    print("[2/4] Configuring camera...")
    # Create preview configuration (lower resolution for testing)
    config = camera.create_preview_configuration(
        main={"size": (1920, 1080)},
        lores={"size": (640, 480)},
        display="lores"
    )
    camera.configure(config)
    print("    [OK] Camera configured")
    print(f"    Resolution: 1920x1080")

    print()
    print("[3/4] Starting camera...")
    camera.start()
    print("    [OK] Camera started")

    # Give camera time to adjust
    print("    Warming up (2 seconds)...")
    time.sleep(2)

    print()
    print("[4/4] Capturing test image...")
    test_image_path = "/home/bacadasa/Desktop/RASPI 4 SORTING PROJECT/test_capture.jpg"
    camera.capture_file(test_image_path)
    print(f"    [OK] Image saved to:")
    print(f"    {test_image_path}")

    print()
    print("=" * 60)
    print("SUCCESS! Camera is working!")
    print("=" * 60)
    print()
    print("Test image saved. You can view it with:")
    print(f"  eom {test_image_path}")
    print()

except Exception as e:
    print()
    print("=" * 60)
    print("ERROR: Camera test failed!")
    print("=" * 60)
    print(f"Error message: {e}")
    print()
    print("Troubleshooting:")
    print("1. Check camera cable connection (blue side faces USB ports)")
    print("2. Make sure cable is firmly inserted on both ends")
    print("3. Try rebooting: sudo reboot")
    print("4. Check camera is enabled: sudo raspi-config")
    print()

finally:
    try:
        camera.stop()
        camera.close()
        print("Camera closed cleanly.")
    except:
        pass
