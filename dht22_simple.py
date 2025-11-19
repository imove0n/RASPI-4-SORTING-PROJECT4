#!/usr/bin/env python3
"""
Simple DHT22 sensor reading - single measurement with retries
"""

import board
import adafruit_dht
import time

# Initialize DHT22 on GPIO4
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

# Try up to 3 times with delays
max_attempts = 3
for attempt in range(max_attempts):
    try:
        temperature = dht.temperature
        humidity = dht.humidity

        print(f"Temperature: {temperature:.1f}°C ({temperature * 9/5 + 32:.1f}°F)")
        print(f"Humidity: {humidity:.1f}%")
        break

    except RuntimeError as e:
        if attempt < max_attempts - 1:
            time.sleep(2)  # Wait before retry
            continue
        else:
            print(f"Error after {max_attempts} attempts: {e.args[0]}")

dht.exit()
