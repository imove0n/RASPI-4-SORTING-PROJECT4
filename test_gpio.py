#!/usr/bin/env python3
"""
GPIO diagnostic script to test DHT22 connectivity
"""

import sys

print("Testing GPIO access and DHT22 sensor...")
print("=" * 50)

# Test 1: Check if running with proper permissions
import os
print(f"User: {os.getenv('USER')}")
print(f"Groups: ", end="")
import subprocess
result = subprocess.run(['groups'], capture_output=True, text=True)
print(result.stdout.strip())
print()

# Test 2: Check board library
try:
    import board
    print("[OK] Board library imported successfully")
    print(f"  Available pins: {dir(board)}")
    print(f"  GPIO4 (D4) available: {hasattr(board, 'D4')}")
except Exception as e:
    print(f"[ERROR] Board library error: {e}")
    sys.exit(1)

print()

# Test 3: Try to initialize DHT22
try:
    import adafruit_dht
    print("[OK] Adafruit DHT library imported successfully")
    print("  Attempting to initialize DHT22 on GPIO4...")

    dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    print("[OK] DHT22 initialized successfully")

    print("\n  Attempting to read sensor (this may take a few seconds)...")
    import time
    time.sleep(2)  # Give sensor time to stabilize

    try:
        temperature = dht.temperature
        humidity = dht.humidity
        print(f"\n[SUCCESS!] Sensor is working!")
        print(f"  Temperature: {temperature:.1f}°C")
        print(f"  Humidity: {humidity:.1f}%")
    except RuntimeError as e:
        print(f"\n[WARNING] Sensor initialized but read failed: {e.args[0]}")
        print("  This is normal on first try. Try running the script again.")
    finally:
        dht.exit()

except Exception as e:
    print(f"[ERROR] DHT library error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check wiring connections")
    print("2. Make sure sensor is DHT22 (not DHT11)")
    print("3. Try running with: sudo python3 test_gpio.py")
    sys.exit(1)

print("\n" + "=" * 50)
print("Diagnostic complete")
