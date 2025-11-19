#!/usr/bin/env python3
"""
DHT22 Change Detection Test
Takes 5 readings over 20 seconds to show dynamic changes
"""

import time
import board
import adafruit_dht

dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)

print("=" * 70)
print("DHT22 CHANGE DETECTION TEST")
print("=" * 70)
print("\nThis will take 5 readings over 20 seconds.")
print("TRY THIS: Gently breathe on the sensor or touch it with your finger")
print("          between readings to see the temperature change!\n")

readings = []
max_readings = 5

for i in range(max_readings):
    print(f"Reading {i+1}/{max_readings}...", end=" ", flush=True)

    attempt = 0
    while attempt < 3:
        try:
            temp = dht.temperature
            humidity = dht.humidity
            readings.append((temp, humidity))

            temp_f = temp * 9/5 + 32
            print(f"Temperature: {temp:.1f}°C ({temp_f:.1f}°F), Humidity: {humidity:.1f}%")

            # Show change from previous reading
            if i > 0:
                prev_temp, prev_hum = readings[i-1]
                temp_diff = temp - prev_temp
                hum_diff = humidity - prev_hum

                if abs(temp_diff) > 0.1 or abs(hum_diff) > 0.1:
                    change_msg = "  >>> "
                    if abs(temp_diff) > 0.1:
                        direction = "warmer" if temp_diff > 0 else "cooler"
                        change_msg += f"Temperature {direction} by {abs(temp_diff):.1f}°C  "
                    if abs(hum_diff) > 0.1:
                        direction = "increased" if hum_diff > 0 else "decreased"
                        change_msg += f"Humidity {direction} by {abs(hum_diff):.1f}%"
                    print(change_msg)

            break

        except RuntimeError as e:
            attempt += 1
            if attempt < 3:
                time.sleep(2)
            else:
                print(f"Error: {e.args[0]}")

    if i < max_readings - 1:
        print("Waiting 4 seconds for next reading...")
        time.sleep(4)

dht.exit()

print("\n" + "=" * 70)
print("SUMMARY:")
if len(readings) >= 2:
    first_temp, first_hum = readings[0]
    last_temp, last_hum = readings[-1]

    temp_change = last_temp - first_temp
    hum_change = last_hum - first_hum

    print(f"First reading:  {first_temp:.1f}°C, {first_hum:.1f}%")
    print(f"Last reading:   {last_temp:.1f}°C, {last_hum:.1f}%")
    print(f"Total change:   {temp_change:+.1f}°C, {hum_change:+.1f}%")

    if abs(temp_change) > 0.5 or abs(hum_change) > 1:
        print("\n✓ Dynamic changes detected! Sensor is responding to environment.")
    else:
        print("\nEnvironment is stable. Try breathing on sensor to see changes.")
else:
    print("Not enough readings collected.")

print("=" * 70)
