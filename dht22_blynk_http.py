#!/usr/bin/env python3
"""
DHT22 + Blynk Integration (HTTP/REST API method)
Sends temperature and humidity data to Blynk app on your phone
This uses the HTTP API which works with Blynk 2.0 (blynk.cloud)
"""

import time
import board
import adafruit_dht
import requests

# ============================================
# CONFIGURATION
# ============================================
BLYNK_AUTH = "NiLKQrFiT7Qr-wZcbx7JZZlpEzQghWA_"  # Your Blynk Auth Token

# Virtual Pins Configuration
TEMPERATURE_PIN = "V0"  # Virtual Pin for Temperature
HUMIDITY_PIN = "V1"     # Virtual Pin for Humidity

# Blynk server URL (new Blynk 2.0)
BLYNK_SERVER = "https://blynk.cloud/external/api/update"

# Update interval in seconds (minimum 5 seconds for HTTP)
UPDATE_INTERVAL = 5
# ============================================


# Initialize DHT22 sensor
print("Initializing DHT22 sensor...")
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
time.sleep(2)  # Let sensor stabilize

# Statistics
successful_reads = 0
failed_reads = 0
data_sent = 0
connection_errors = 0

print(f"\n{'=' * 60}")
print("DHT22 to BLYNK - Monitoring Started (HTTP API)")
print(f"{'=' * 60}")
print(f"Temperature Pin: {TEMPERATURE_PIN}")
print(f"Humidity Pin: {HUMIDITY_PIN}")
print(f"Update Interval: {UPDATE_INTERVAL} seconds")
print("\nPress Ctrl+C to stop")
print(f"{'=' * 60}\n")


def send_to_blynk(temperature, humidity):
    """Send both temperature and humidity to Blynk using HTTP API"""
    try:
        # Send both values in one request
        url = f"{BLYNK_SERVER}?token={BLYNK_AUTH}&V0={temperature}&V1={humidity}"
        response = requests.get(url, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"  Connection error: {e}")
        return False


def read_and_send():
    """Read sensor and send data to Blynk"""
    global successful_reads, failed_reads, data_sent, connection_errors

    try:
        # Read sensor
        temperature = dht.temperature
        humidity = dht.humidity

        successful_reads += 1

        # Send to Blynk
        sent = send_to_blynk(temperature, humidity)

        if sent:
            data_sent += 1
            connection_errors = 0  # Reset on success

            # Display on console
            current_time = time.strftime("%H:%M:%S")
            print(f"[{current_time}] Data #{data_sent} sent to Blynk:")
            print(f"  Temperature: {temperature:.1f}°C ({temperature * 9/5 + 32:.1f}°F)")
            print(f"  Humidity: {humidity:.1f}%")
            print(f"  Sensor success rate: {successful_reads}/{successful_reads + failed_reads} ({100 * successful_reads / (successful_reads + failed_reads):.1f}%)")
            print("-" * 60)
        else:
            connection_errors += 1
            print(f"[{time.strftime('%H:%M:%S')}] Failed to send to Blynk ({connection_errors} consecutive errors)")
            print("  Check your internet connection")
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
    # Test connection first
    print("Testing Blynk connection...")
    if send_to_blynk(0, 0):
        print("[OK] Connected to Blynk successfully!\n")
    else:
        print("[WARNING] Could not connect to Blynk. Check:")
        print("  1. Auth Token is correct")
        print("  2. Internet connection is working")
        print("  3. Device exists on blynk.cloud")
        print("\nContinuing anyway...\n")

    while True:
        read_and_send()
        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print(f"\n{'=' * 60}")
    print("Monitoring stopped by user")
    print(f"Total successful sensor reads: {successful_reads}")
    print(f"Total failed sensor reads: {failed_reads}")
    print(f"Total data sent to Blynk: {data_sent}")
    if successful_reads > 0:
        print(f"Sensor success rate: {100 * successful_reads / (successful_reads + failed_reads):.1f}%")
    print(f"{'=' * 60}")

finally:
    # Cleanup
    dht.exit()
    print("Cleanup complete. Goodbye!")
