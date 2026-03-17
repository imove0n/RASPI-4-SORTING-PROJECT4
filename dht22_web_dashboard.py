#!/usr/bin/env python3
"""
DHT22 Web Dashboard Server
Access from any device on your network via web browser
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import board
import adafruit_dht
import time
import socket
import RPi.GPIO as GPIO

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# --- BTS7960 Motor Driver Setup (Conveyor Belt) ---
# Wiring:
#   RPWM  → GPIO 25 (Pin 22) - Forward PWM speed
#   LPWM  → GPIO 24 (Pin 18) - Reverse PWM speed
#   R_EN  → GPIO 17 (Pin 11) - Right Enable
#   L_EN  → GPIO 27 (Pin 13) - Left Enable
#   VCC   → 3.3V (Pin 1)
#   GND   → Pi GND (Pin 9)
#   B+    → External 12V PSU +
#   B-    → External 12V PSU -
#   M+    → Conveyor motor wire 1
#   M-    → Conveyor motor wire 2
MOTOR_RPWM = 25   # Forward PWM
MOTOR_LPWM = 24   # Reverse PWM
MOTOR_R_EN = 17   # Right Enable
MOTOR_L_EN = 27   # Left Enable

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(MOTOR_RPWM, GPIO.OUT)
GPIO.setup(MOTOR_LPWM, GPIO.OUT)
GPIO.setup(MOTOR_R_EN, GPIO.OUT)
GPIO.setup(MOTOR_L_EN, GPIO.OUT)

# PWM on both direction pins (1 kHz for BTS7960)
pwm_forward = GPIO.PWM(MOTOR_RPWM, 1000)
pwm_reverse = GPIO.PWM(MOTOR_LPWM, 1000)
pwm_forward.start(0)
pwm_reverse.start(0)

# Enable the driver (both enables HIGH)
GPIO.output(MOTOR_R_EN, GPIO.HIGH)
GPIO.output(MOTOR_L_EN, GPIO.HIGH)

# Conveyor state
conveyor_state = {
    'running': False,
    'speed': 75,       # default speed percentage (0-100)
    'direction': 'forward'
}

def conveyor_stop():
    pwm_forward.ChangeDutyCycle(0)
    pwm_reverse.ChangeDutyCycle(0)
    conveyor_state['running'] = False

def conveyor_forward(speed=None):
    if speed is not None:
        conveyor_state['speed'] = speed
    pwm_reverse.ChangeDutyCycle(0)
    pwm_forward.ChangeDutyCycle(conveyor_state['speed'])
    conveyor_state['running'] = True
    conveyor_state['direction'] = 'forward'

def conveyor_reverse(speed=None):
    if speed is not None:
        conveyor_state['speed'] = speed
    pwm_forward.ChangeDutyCycle(0)
    pwm_reverse.ChangeDutyCycle(conveyor_state['speed'])
    conveyor_state['running'] = True
    conveyor_state['direction'] = 'reverse'

print("✓ BTS7960 Motor Driver initialized (RPWM=GPIO25, LPWM=GPIO24, EN=GPIO17)")

# --- MG996R Servo Motor Setup (Sorting Gate) ---
# Wiring:
#   Signal (orange) → GPIO 21 (Pin 40)
#   VCC (red)       → 5V (Pin 2)
#   GND (brown)     → GND (Pin 39)
#   180-degree servo: 0°=2.5%, 90°=7.5%, 180°=12.5% duty cycle at 50Hz
SERVO_PIN = 21
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for servo
servo_pwm.start(0)

servo_state = {
    'angle': 120,  # default gate closed position
}

SERVO_REST = 120   # Gate closed (resting position)
SERVO_OPEN = 180   # Gate open (sorting position)

# Calibrated duty cycles for this specific servo mount
SERVO_DUTY_CLOSE = 10.0   # Duty cycle for closed position (120°)
SERVO_DUTY_OPEN = 12.5    # Duty cycle for open position (180°)

def servo_pulse(duty):
    """Send a strong, consistent PWM pulse to servo 1"""
    # Double pulse for reliability on software PWM
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo_pwm.ChangeDutyCycle(0)
    time.sleep(0.05)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo_pwm.ChangeDutyCycle(0)

def servo_open():
    """Open gate using calibrated duty cycle"""
    servo_pulse(SERVO_DUTY_OPEN)
    servo_state['angle'] = SERVO_OPEN

def servo_close():
    """Close gate using calibrated duty cycle"""
    servo_pulse(SERVO_DUTY_CLOSE)
    servo_state['angle'] = SERVO_REST

def set_servo_angle(angle):
    """Set servo to angle (0-180 degrees)"""
    angle = max(0, min(180, angle))
    duty = 2.0 + (angle / 180.0) * 10.5
    servo_pulse(duty)
    servo_state['angle'] = angle

def servo_sort():
    """Sorting action: open gate then close gate"""
    servo_open()
    time.sleep(0.5)
    servo_close()

# Move to resting position on startup
servo_pwm.ChangeDutyCycle(SERVO_DUTY_CLOSE)
time.sleep(0.5)
servo_pwm.ChangeDutyCycle(0)
servo_state['angle'] = SERVO_REST
print("✓ MG996R Servo 1 - Gate (GPIO 21, Pin 40) - 180°")

# --- MG996R Servo 2 - Sorting Arm (Left/Center/Right) ---
# Wiring:
#   Signal (orange) → GPIO 20 (Pin 38)
#   VCC (red)       → Breadboard 5V rail
#   GND (brown)     → Breadboard GND rail
SERVO2_PIN = 20
GPIO.setup(SERVO2_PIN, GPIO.OUT)
servo2_pwm = GPIO.PWM(SERVO2_PIN, 50)  # 50Hz for servo
servo2_pwm.start(0)

# Calibrated duty cycles for servo 2
SERVO2_DUTY_LEFT = 5.0
SERVO2_DUTY_CENTER = 6.0
SERVO2_DUTY_RIGHT = 7.0

servo2_state = {
    'position': 'center',
}

def servo2_pulse(duty):
    """Send a strong, consistent PWM pulse to servo 2"""
    servo2_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo2_pwm.ChangeDutyCycle(0)
    time.sleep(0.05)
    servo2_pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)
    servo2_pwm.ChangeDutyCycle(0)

def set_servo2_position(position):
    """Set servo 2 to left, center, or right"""
    if position == 'left':
        servo2_pulse(SERVO2_DUTY_LEFT)
    elif position == 'right':
        servo2_pulse(SERVO2_DUTY_RIGHT)
    else:
        position = 'center'
        servo2_pulse(SERVO2_DUTY_CENTER)
    servo2_state['position'] = position

# Move to center on startup
servo2_pwm.ChangeDutyCycle(SERVO2_DUTY_CENTER)
time.sleep(0.5)
servo2_pwm.ChangeDutyCycle(0)
print("✓ MG996R Servo 2 - Sorter (GPIO 20, Pin 38) - L/C/R")

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


@app.route('/api/conveyor', methods=['GET'])
def get_conveyor():
    """Get current conveyor state"""
    return jsonify(conveyor_state)


@app.route('/api/conveyor', methods=['POST'])
def control_conveyor():
    """Control conveyor belt: action = start/stop/reverse, speed = 0-100"""
    data = request.get_json()
    action = data.get('action', '')
    speed = data.get('speed')

    if speed is not None:
        speed = max(0, min(100, int(speed)))
        conveyor_state['speed'] = speed

    if action == 'start':
        if conveyor_state['direction'] == 'reverse':
            conveyor_reverse(speed)
        else:
            conveyor_forward(speed)
    elif action == 'stop':
        conveyor_stop()
    elif action == 'forward':
        conveyor_forward(speed)
    elif action == 'reverse':
        conveyor_reverse(speed)
    elif action == 'speed' and speed is not None:
        # Update speed without changing direction/state
        if conveyor_state['running']:
            if conveyor_state['direction'] == 'forward':
                pwm_forward.ChangeDutyCycle(conveyor_state['speed'])
            else:
                pwm_reverse.ChangeDutyCycle(conveyor_state['speed'])

    return jsonify(conveyor_state)


@app.route('/api/servo', methods=['GET'])
def get_servo():
    """Get current servo state"""
    return jsonify(servo_state)


@app.route('/api/servo', methods=['POST'])
def control_servo():
    """Control servo: angle = 0-180, or action = 'sweep' for full 0->180->0"""
    data = request.get_json()
    action = data.get('action', '')
    angle = data.get('angle')

    if action == 'sweep':
        servo_close()
        time.sleep(0.5)
        servo_open()
        time.sleep(0.5)
        servo_close()
    elif action == 'sort':
        servo_sort()
    elif action == 'open':
        servo_open()
    elif action == 'close':
        servo_close()
    elif angle is not None:
        angle = max(0, min(180, int(angle)))
        set_servo_angle(angle)

    return jsonify(servo_state)


@app.route('/api/servo2', methods=['GET'])
def get_servo2():
    """Get current servo 2 state"""
    return jsonify(servo2_state)


@app.route('/api/servo2', methods=['POST'])
def control_servo2():
    """Control servo 2: position = left/center/right"""
    data = request.get_json()
    position = data.get('position', 'center')
    set_servo2_position(position)
    return jsonify(servo2_state)


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
        conveyor_stop()
        pwm_forward.stop()
        pwm_reverse.stop()
        servo_pwm.stop()
        servo2_pwm.stop()
        GPIO.cleanup()
        dht1.exit()
        dht2.exit()
        print("Cleanup complete. Goodbye!")
