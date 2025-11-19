#!/usr/bin/env python3
"""
DHT22 + Blynk Integration
Sends temperature and humidity data to Blynk app on your phone
"""

import time
import board
import adafruit_dht
import BlynkLib

# ============================================
# CONFIGURATION - CHANGE THIS!
# ============================================
# Get your Auth Token from: blynk.cloud → Devices → Your Device → Device Info
BLYNK_AUTH = "NiLKQrFiT7Qr-wZcbx7JZZlpEzQghWA_"  # Your Blynk Auth Token

# Virtual Pins Configuration
TEMPERATURE_PIN = "V0"  # Virtual Pin for Temperature
HUMIDITY_PIN = "V1"     # Virtual Pin for Humidity

# Update interval in seconds (minimum 1 second, recommended 5+)
UPDATE_INTERVAL = 5
# ============================================


# Initialize DHT22 sensor
print("Initializing DHT22 sensor...")
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
time.sleep(2)  # Let sensor stabilize

# Initialize Blynk
print("Connecting to Blynk...")
try:
    blynk = BlynkLib.Blynk(BLYNK_AUTH)
    print("✓ Connected to Blynk!")
except Exception as e:
    print(f"✗ Failed to connect to Blynk: {e}")
    print("\nPlease check:")
    print("1. Your Auth Token is correct")
    print("2. Your Raspberry Pi is connected to internet")
    print("3. You've created the device on blynk.cloud")
    exit(1)

# Statistics
successful_reads = 0
failed_reads = 0
data_sent = 0

print(f"\n{'=' * 60}")
print("DHT22 → BLYNK - Monitoring Started")
print(f"{'=' * 60}")
print(f"Temperature Pin: {TEMPERATURE_PIN}")
print(f"Humidity Pin: {HUMIDITY_PIN}")
print(f"Update Interval: {UPDATE_INTERVAL} seconds")
print("\nPress Ctrl+C to stop")
print(f"{'=' * 60}\n")


def read_and_send():
    """Read sensor and send data to Blynk"""
    global successful_reads, failed_reads, data_sent

    try:
        # Read sensor
        temperature = dht.temperature
        humidity = dht.humidity

        # Send to Blynk
        blynk.virtual_write(0, temperature)  # V0 for temperature
        blynk.virtual_write(1, humidity)     # V1 for humidity

        successful_reads += 1
        data_sent += 1

        # Display on console
        current_time = time.strftime("%H:%M:%S")
        print(f"[{current_time}] Data #{data_sent} sent to Blynk:")
        print(f"  Temperature: {temperature:.1f}°C ({temperature * 9/5 + 32:.1f}°F)")
        print(f"  Humidity: {humidity:.1f}%")
        print(f"  Success rate: {successful_reads}/{successful_reads + failed_reads} ({100 * successful_reads / (successful_reads + failed_reads):.1f}%)")
        print("-" * 60)

    except RuntimeError as error:
        failed_reads += 1
        print(f"[{time.strftime('%H:%M:%S')}] Sensor read error: {error.args[0]}")
        print(f"  (This is normal, will retry in {UPDATE_INTERVAL} seconds)")
        print("-" * 60)
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Unexpected error: {e}")
        print("-" * 60)


# Main loop
try:
    while True:
        # Process Blynk events
        blynk.run()

        # Read sensor and send data
        read_and_send()

        # Wait before next update
        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print(f"\n{'=' * 60}")
    print("Monitoring stopped by user")
    print(f"Total successful reads: {successful_reads}")
    print(f"Total failed reads: {failed_reads}")
    print(f"Total data sent to Blynk: {data_sent}")
    print(f"{'=' * 60}")

finally:
    # Cleanup
    dht.exit()
    print("Cleanup complete. Goodbye!")
