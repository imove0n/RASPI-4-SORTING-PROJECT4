#!/usr/bin/env python3
"""
DHT22 Live Monitor - Shows real-time temperature and humidity changes
Press Ctrl+C to stop
"""

import time
import board
import adafruit_dht
from datetime import datetime

# Initialize DHT22 on GPIO4
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

print("=" * 60)
print("DHT22 LIVE MONITOR - Real-time Temperature & Humidity")
print("=" * 60)
print("\nTIP: Try breathing on the sensor or touching it gently")
print("     to see the values change!\n")
print("Press Ctrl+C to stop\n")
print("Initializing sensor, please wait...")
time.sleep(3)  # Give sensor time to stabilize on startup
print("-" * 60)

reading_count = 0
successful_readings = 0
previous_temp = None
previous_humidity = None
consecutive_errors = 0

try:
    while True:
        try:
            # Read sensor
            temp = dht.temperature
            humidity = dht.humidity
            reading_count += 1
            successful_readings += 1
            consecutive_errors = 0  # Reset error counter on success

            # Get current time
            current_time = datetime.now().strftime("%H:%M:%S")

            # Calculate changes if we have previous readings
            temp_change = ""
            humidity_change = ""

            if previous_temp is not None:
                temp_diff = temp - previous_temp
                if abs(temp_diff) > 0.1:
                    if temp_diff > 0:
                        temp_change = f" [+{temp_diff:.1f}°C UP]"
                    else:
                        temp_change = f" [{temp_diff:.1f}°C DOWN]"

            if previous_humidity is not None:
                hum_diff = humidity - previous_humidity
                if abs(hum_diff) > 0.5:
                    if hum_diff > 0:
                        humidity_change = f" [+{hum_diff:.1f}% UP]"
                    else:
                        humidity_change = f" [{hum_diff:.1f}% DOWN]"

            # Display reading
            print(f"[{current_time}] Reading #{successful_readings}:")
            print(f"  Temperature: {temp:.1f}°C ({temp * 9/5 + 32:.1f}°F){temp_change}")
            print(f"  Humidity:    {humidity:.1f}%{humidity_change}")
            print("-" * 60)

            # Store current values for next comparison
            previous_temp = temp
            previous_humidity = humidity

        except RuntimeError as error:
            # DHT sensor errors are normal occasionally
            reading_count += 1
            consecutive_errors += 1
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Read error: {error.args[0]}")

            # Check if wiring might be loose
            if consecutive_errors >= 5:
                print("  WARNING: Multiple consecutive errors!")
                print("  -> Check if wires are connected firmly")
                print("  -> Make sure sensor has power (VCC and GND)")
                consecutive_errors = 0  # Reset to avoid spam

            print("-" * 60)

        # Wait 3 seconds before next reading
        time.sleep(3)

except KeyboardInterrupt:
    print("\n" + "=" * 60)
    print(f"Monitoring stopped.")
    print(f"Total attempts: {reading_count}")
    print(f"Successful readings: {successful_readings}")
    if reading_count > 0:
        success_rate = (successful_readings / reading_count) * 100
        print(f"Success rate: {success_rate:.1f}%")
    print("=" * 60)

finally:
    dht.exit()
