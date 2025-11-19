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

# Initialize DHT22 sensor
print("Initializing DHT22 sensor...")
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
time.sleep(2)

# Statistics
successful_reads = 0
failed_reads = 0
last_temperature = None
last_humidity = None


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


def read_sensor():
    """Read sensor data with error handling"""
    global successful_reads, failed_reads, last_temperature, last_humidity

    try:
        temperature = dht.temperature
        humidity = dht.humidity

        successful_reads += 1
        last_temperature = temperature
        last_humidity = humidity

        return {
            'success': True,
            'temperature': temperature,
            'humidity': humidity,
            'success_rate': round(100 * successful_reads / (successful_reads + failed_reads), 1),
            'total_readings': successful_reads + failed_reads
        }

    except RuntimeError as error:
        failed_reads += 1

        # Return last known values if available
        if last_temperature is not None and last_humidity is not None:
            return {
                'success': True,
                'temperature': last_temperature,
                'humidity': last_humidity,
                'success_rate': round(100 * successful_reads / (successful_reads + failed_reads), 1),
                'total_readings': successful_reads + failed_reads,
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
    data = read_sensor()
    return jsonify(data)


@app.route('/api/status')
def get_status():
    """API endpoint for server status"""
    return jsonify({
        'status': 'online',
        'sensor': 'DHT22',
        'successful_reads': successful_reads,
        'failed_reads': failed_reads,
        'success_rate': round(100 * successful_reads / (successful_reads + failed_reads), 1) if (successful_reads + failed_reads) > 0 else 0
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
        dht.exit()
        print("Cleanup complete. Goodbye!")
