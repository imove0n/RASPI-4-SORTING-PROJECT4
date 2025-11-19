#!/usr/bin/env python3
"""
DHT22 Demo - Shows 3 readings
"""

import time
import board
import adafruit_dht

dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

print("DHT22 Sensor Demo - Taking 3 readings...")
print("=" * 50)

for i in range(3):
    try:
        temp = dht.temperature
        humidity = dht.humidity
        print(f"\nReading {i+1}:")
        print(f"  Temperature: {temp:.1f}°C ({temp * 9/5 + 32:.1f}°F)")
        print(f"  Humidity: {humidity:.1f}%")
    except RuntimeError as e:
        print(f"\nReading {i+1}: Error - {e.args[0]}")

    if i < 2:  # Don't wait after last reading
        time.sleep(2.5)

dht.exit()
print("\n" + "=" * 50)
print("Demo complete!")
