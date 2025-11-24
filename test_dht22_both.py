#!/usr/bin/env python3
"""
Test both DHT22 sensors to verify connections
"""
import board
import adafruit_dht
import time

print("=" * 60)
print("DHT22 DUAL SENSOR TEST")
print("=" * 60)
print()

# Initialize both sensors
print("Initializing sensors...")
print()

try:
    dht1 = adafruit_dht.DHT22(board.D4, use_pulseio=False)
    print("✓ DHT22 #1 initialized on GPIO 4 (Pin 7)")
    print("  Wiring: Pin 1 (VCC) → 3.3V")
    print("          Pin 6 (GND) → GND")
    print("          Pin 7 (DATA) → GPIO 4")
    print()
except Exception as e:
    print(f"✗ Failed to initialize DHT22 #1: {e}")
    print()

try:
    dht2 = adafruit_dht.DHT22(board.D23, use_pulseio=False)
    print("✓ DHT22 #2 initialized on GPIO 23 (Pin 16)")
    print("  Wiring: Pin 17 (VCC) → 3.3V")
    print("          Pin 14 (GND) → GND")
    print("          Pin 16 (DATA) → GPIO 23")
    print()
except Exception as e:
    print(f"✗ Failed to initialize DHT22 #2: {e}")
    print()

print("-" * 60)
print("Testing sensors (5 readings each)...")
print("-" * 60)
print()

for i in range(5):
    print(f"Reading {i+1}/5:")
    print()

    # Test sensor 1
    try:
        temp1 = dht1.temperature
        humid1 = dht1.humidity
        print(f"  DHT22 #1 (GPIO 4):  Temp={temp1:.1f}°C  Humidity={humid1:.1f}%")
    except RuntimeError as e:
        print(f"  DHT22 #1 (GPIO 4):  FAILED - {e.args[0]}")

    # Test sensor 2
    try:
        temp2 = dht2.temperature
        humid2 = dht2.humidity
        print(f"  DHT22 #2 (GPIO 23): Temp={temp2:.1f}°C  Humidity={humid2:.1f}%")
    except RuntimeError as e:
        print(f"  DHT22 #2 (GPIO 23): FAILED - {e.args[0]}")

    print()
    time.sleep(3)

print("=" * 60)
print("Test complete!")
print()
print("PIN SUMMARY:")
print()
print("DHT22 #1 (Container UNRIPE):")
print("  VCC  → Pin 1  (3.3V)")
print("  DATA → Pin 7  (GPIO 4)")
print("  GND  → Pin 6  (Ground)")
print()
print("DHT22 #2 (Container RIPE) - RECOMMENDED:")
print("  VCC  → Pin 17 (3.3V)")
print("  DATA → Pin 16 (GPIO 23)")
print("  GND  → Pin 14 (Ground)")
print("=" * 60)

dht1.exit()
dht2.exit()
