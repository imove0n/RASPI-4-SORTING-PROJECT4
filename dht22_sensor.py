#!/usr/bin/env python3
"""
DHT22 Temperature and Humidity Sensor Reader for Raspberry Pi
This script reads temperature and humidity data from a DHT22 sensor.

Wiring:
- DHT22 VCC -> Raspberry Pi 3.3V or 5V
- DHT22 GND -> Raspberry Pi GND
- DHT22 DATA -> Raspberry Pi GPIO pin (default: GPIO4)
"""

import time
import board
import adafruit_dht

# Initialize the DHT22 sensor on GPIO4 (Pin 7)
# You can change this to other GPIO pins like board.D17, board.D18, etc.
dht_device = adafruit_dht.DHT22(board.D4, use_pulseio=False)

def read_sensor():
    """Read temperature and humidity from DHT22 sensor."""
    try:
        # Read sensor data
        temperature_c = dht_device.temperature
        humidity = dht_device.humidity

        # Convert to Fahrenheit
        temperature_f = temperature_c * (9 / 5) + 32

        # Print the results
        print("=" * 50)
        print(f"Temperature: {temperature_c:.1f}°C / {temperature_f:.1f}°F")
        print(f"Humidity: {humidity:.1f}%")
        print("=" * 50)

        return temperature_c, humidity

    except RuntimeError as error:
        # DHT sensors can occasionally fail to read, this is normal
        print(f"Error reading sensor: {error.args[0]}")
        return None, None
    except Exception as error:
        print(f"Unexpected error: {str(error)}")
        dht_device.exit()
        raise error

def main():
    """Main function to continuously read sensor data."""
    print("DHT22 Sensor Reading Started")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            read_sensor()
            # Wait 2 seconds between readings (DHT22 requires at least 2s)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping sensor readings...")
    finally:
        # Clean up
        dht_device.exit()
        print("Cleanup complete")

if __name__ == "__main__":
    main()
