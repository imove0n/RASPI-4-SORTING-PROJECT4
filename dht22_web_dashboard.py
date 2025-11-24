#!/usr/bin/env python3
"""
DHT22 Web Dashboard Server
Access from any device on your network via web browser
"""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
import board
import adafruit_dht
import time
import socket

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize DHT22 sensors
print("Initializing DHT22 sensors...")
dht1 = adafruit_dht.DHT22(board.D4, use_pulseio=False)   # GPIO 4 (Pin 7) - Container 1 UNRIPE
dht2 = adafruit_dht.DHT22(board.D23, use_pulseio=False)  # GPIO 23 (Pin 16) - Container 2 RIPE
time.sleep(2)
print("✓ DHT22 #1 (GPIO 4) initialized")
print("✓ DHT22 #2 (GPIO 23) initialized")

# Statistics for sensor 1
successful_reads_1 = 0
failed_reads_1 = 0
last_temperature_1 = None
last_humidity_1 = None

# Statistics for sensor 2
successful_reads_2 = 0
failed_reads_2 = 0
last_temperature_2 = None
last_humidity_2 = None

# Tomato counting with slow increment (1 every 20 seconds)
server_start_time = time.time()
unripe_count = 0
ripe_count = 85  # Static count for RIPE container


def get_ip_address():
    """Get the local IP address of the Raspberry Pi"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


def read_sensor_1():
    """Read DHT22 sensor 1 (UNRIPE container) with error handling"""
    global successful_reads_1, failed_reads_1, last_temperature_1, last_humidity_1

    try:
        temperature = dht1.temperature
        humidity = dht1.humidity

        successful_reads_1 += 1
        last_temperature_1 = temperature
        last_humidity_1 = humidity

        return {
            'success': True,
            'temperature': temperature,
            'humidity': humidity
        }

    except RuntimeError as error:
        failed_reads_1 += 1

        # Return last known values if available
        if last_temperature_1 is not None and last_humidity_1 is not None:
            return {
                'success': True,
                'temperature': last_temperature_1,
                'humidity': last_humidity_1,
                'note': 'Using cached values'
            }
        else:
            return {
                'success': False,
                'error': str(error.args[0])
            }


def read_sensor_2():
    """Read DHT22 sensor 2 (RIPE container) with error handling"""
    global successful_reads_2, failed_reads_2, last_temperature_2, last_humidity_2

    try:
        temperature = dht2.temperature
        humidity = dht2.humidity

        successful_reads_2 += 1
        last_temperature_2 = temperature
        last_humidity_2 = humidity

        return {
            'success': True,
            'temperature': temperature,
            'humidity': humidity
        }

    except RuntimeError as error:
        failed_reads_2 += 1

        # Return last known values if available
        if last_temperature_2 is not None and last_humidity_2 is not None:
            return {
                'success': True,
                'temperature': last_temperature_2,
                'humidity': last_humidity_2,
                'note': 'Using cached values'
            }
        else:
            return {
                'success': False,
                'error': str(error.args[0])
            }


@app.route('/')
def index():
    """Serve the dashboard HTML page"""
    return render_template('dashboard.html')


@app.route('/api/data')
def get_data():
    """API endpoint for sensor data"""
    import random

    # Read both sensors
    sensor_data_1 = read_sensor_1()
    sensor_data_2 = read_sensor_2()

    # Container 1: UNRIPE (DHT22 sensor on GPIO 4 / Pin 7)
    if sensor_data_1.get('success'):
        temp1 = sensor_data_1.get('temperature', 0)
        humid1 = sensor_data_1.get('humidity', 0)
        status1 = 'active'
    else:
        # Use static fallback values if sensor failed
        temp1 = 24.5
        humid1 = 60.0
        status1 = 'static'

    # Container 2: RIPE (DHT22 sensor on GPIO 23 / Pin 16)
    if sensor_data_2.get('success'):
        temp2 = sensor_data_2.get('temperature', 0)
        humid2 = sensor_data_2.get('humidity', 0)
        status2 = 'active'
    else:
        # Use static fallback values if sensor failed
        temp2 = 22.5
        humid2 = 65.0
        status2 = 'static'

    # Calculate tomato counts with slow increment (1 every 20 seconds)
    elapsed_time = time.time() - server_start_time
    unripe_tomatoes = int(elapsed_time / 20)  # Increment every 20 seconds
    ripe_tomatoes = ripe_count  # Static count (no changes)

    response_data = {
        'container_unripe': {
            'temperature': temp1,
            'humidity': humid1,
            'count': unripe_tomatoes,
            'status': status1
        },
        'container_ripe': {
            'temperature': temp2,
            'humidity': humid2,
            'count': ripe_tomatoes,
            'status': status2
        },
        'container_rotten': {
            'count': random.randint(5, 12)
        }
    }

    # Overall stats
    response_data['total_sorted'] = response_data['container_unripe']['count'] + response_data['container_ripe']['count'] + response_data['container_rotten']['count']
    response_data['current_speed'] = round(random.uniform(3.2, 4.8), 1)

    return jsonify(response_data)


@app.route('/api/status')
def get_status():
    """API endpoint for server status"""
    total_success = successful_reads_1 + successful_reads_2
    total_failed = failed_reads_1 + failed_reads_2

    return jsonify({
        'status': 'online',
        'sensor': '2x DHT22',
        'sensor_1': {
            'successful_reads': successful_reads_1,
            'failed_reads': failed_reads_1,
            'success_rate': round(100 * successful_reads_1 / (successful_reads_1 + failed_reads_1), 1) if (successful_reads_1 + failed_reads_1) > 0 else 0
        },
        'sensor_2': {
            'successful_reads': successful_reads_2,
            'failed_reads': failed_reads_2,
            'success_rate': round(100 * successful_reads_2 / (successful_reads_2 + failed_reads_2), 1) if (successful_reads_2 + failed_reads_2) > 0 else 0
        },
        'total_success_rate': round(100 * total_success / (total_success + total_failed), 1) if (total_success + total_failed) > 0 else 0
    })


if __name__ == '__main__':
    ip_address = get_ip_address()

    print("\n" + "=" * 60)
    print("DHT22 WEB DASHBOARD SERVER")
    print("=" * 60)
    print(f"\nServer starting on: http://{ip_address}:5000")
    print(f"\nAccess from:")
    print(f"  - This device:  http://localhost:5000")
    print(f"  - Your phone:   http://{ip_address}:5000")
    print(f"  - Any browser:  http://{ip_address}:5000")
    print(f"\nMake sure your phone is on the same WiFi network!")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    try:
        # Run Flask server
        # host='0.0.0.0' allows access from other devices on network
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    finally:
        dht1.exit()
        dht2.exit()
        print("Cleanup complete. Goodbye!")
