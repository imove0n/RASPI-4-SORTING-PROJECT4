#!/usr/bin/env python3
"""
YOLO + DHT22 Integrated Dashboard Server
Combines camera detection with temperature/humidity monitoring
"""

from flask import Flask, render_template, jsonify, Response
from flask_cors import CORS
import board
import adafruit_dht
import time
import threading
from ultralytics import YOLO
from picamera2 import Picamera2
import numpy as np
import cv2

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize DHT22 sensor
print("Initializing DHT22 sensor...")
dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
time.sleep(2)

# Initialize YOLO model
print("Loading YOLO model...")
MODEL_PATH = "best.pt"
model = YOLO(MODEL_PATH)
print("✅ YOLO model loaded!")

# Initialize camera
print("Initializing camera...")
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(
    main={"size": (640, 480), "format": "RGB888"}
)
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
print("✅ Camera ready!")

# Statistics
successful_reads = 0
failed_reads = 0
last_temperature = None
last_humidity = None

# YOLO detection counts (updated by background thread)
detection_counts = {
    'unripe': 0,
    'ripe': 0,
    'last_update': time.time()
}
detection_lock = threading.Lock()

# Latest frame with detection boxes (for camera feed)
latest_frame = None
frame_lock = threading.Lock()


def read_sensor():
    """Read DHT22 sensor data with error handling"""
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
            'humidity': humidity
        }

    except RuntimeError as error:
        failed_reads += 1

        # Return last known values if available
        if last_temperature is not None and last_humidity is not None:
            return {
                'success': True,
                'temperature': last_temperature,
                'humidity': last_humidity,
                'note': 'Using cached values'
            }
        else:
            return {
                'success': False,
                'error': str(error.args[0])
            }


def yolo_detection_loop():
    """Background thread that continuously runs YOLO detection"""
    global detection_counts, latest_frame

    print("Starting YOLO detection thread...")
    class_names = model.names  # Get class names from model

    while True:
        try:
            # Capture frame from camera
            frame = picam2.capture_array()

            # Run YOLO detection
            results = model(frame, verbose=False)

            # Count detections
            unripe_count = 0
            ripe_count = 0

            # Draw detection boxes on frame
            annotated_frame = frame.copy()

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    confidence = float(box.conf[0])
                    class_id = int(box.cls[0])
                    class_name = class_names[class_id]

                    # Only count if confidence > 50%
                    if confidence > 0.5:
                        if class_name == 'unripe':
                            unripe_count += 1
                            color = (74, 222, 128)  # Green for unripe
                        elif class_name == 'ripe':
                            ripe_count += 1
                            color = (255, 107, 107)  # Red for ripe
                        else:
                            continue

                        # Get box coordinates
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        # Draw bounding box
                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                        # Draw label with confidence
                        label = f"{class_name} {confidence:.2f}"
                        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                        cv2.rectangle(annotated_frame, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)
                        cv2.putText(annotated_frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

            # Update global counts (thread-safe)
            with detection_lock:
                detection_counts['unripe'] = unripe_count
                detection_counts['ripe'] = ripe_count
                detection_counts['last_update'] = time.time()

            # Update latest frame (thread-safe)
            with frame_lock:
                latest_frame = annotated_frame

            # Small delay to prevent CPU overload (5 FPS)
            time.sleep(0.2)

        except Exception as e:
            print(f"Detection error: {e}")
            time.sleep(1)


@app.route('/')
def index():
    """Serve the dashboard HTML page"""
    return render_template('dashboard.html')


@app.route('/api/data')
def get_data():
    """API endpoint for sensor data and YOLO counts"""
    sensor_data = read_sensor()

    # Get YOLO detection counts (thread-safe)
    with detection_lock:
        unripe_count = detection_counts['unripe']
        ripe_count = detection_counts['ripe']

    # Build response
    data = {}

    if sensor_data['success']:
        # Container 1: UNRIPE (Real DHT22 + YOLO count)
        data['container_unripe'] = {
            'temperature': sensor_data['temperature'],
            'humidity': sensor_data['humidity'],
            'count': unripe_count,
            'status': 'active'
        }

        # Container 2: RIPE (Simulated temp/humidity + YOLO count)
        data['container_ripe'] = {
            'temperature': 22.5,  # Static for now
            'humidity': 65.0,     # Static for now
            'count': ripe_count,
            'status': 'active'
        }
    else:
        # Fallback if sensor fails
        data['container_unripe'] = {
            'temperature': 0,
            'humidity': 0,
            'count': unripe_count,
            'status': 'sensor_error'
        }

        data['container_ripe'] = {
            'temperature': 0,
            'humidity': 0,
            'count': ripe_count,
            'status': 'active'
        }

    return jsonify(data)


@app.route('/api/status')
def get_status():
    """API endpoint for server status"""
    with detection_lock:
        yolo_active = (time.time() - detection_counts['last_update']) < 2

    return jsonify({
        'status': 'online',
        'sensor': 'DHT22',
        'camera': 'YOLO Detection',
        'yolo_active': yolo_active,
        'successful_reads': successful_reads,
        'failed_reads': failed_reads,
        'success_rate': round(100 * successful_reads / (successful_reads + failed_reads), 1) if (successful_reads + failed_reads) > 0 else 0
    })


def generate_frames():
    """Generator function for video streaming"""
    global latest_frame

    while True:
        with frame_lock:
            if latest_frame is None:
                # Wait for first frame
                time.sleep(0.1)
                continue

            frame = latest_frame.copy()

        # Convert RGB to BGR for OpenCV
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        if not ret:
            continue

        frame_bytes = buffer.tobytes()

        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.1)  # Limit to 10 FPS for streaming


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("YOLO + DHT22 INTEGRATED DASHBOARD")
    print("=" * 60)

    # Start YOLO detection in background thread
    detection_thread = threading.Thread(target=yolo_detection_loop, daemon=True)
    detection_thread.start()

    print("\n✅ YOLO detection running in background")
    print("✅ DHT22 sensor ready")
    print("✅ Dashboard server starting...")
    print(f"\nAccess dashboard at: http://localhost:5000")
    print("\nPress Ctrl+C to stop")
    print("=" * 60 + "\n")

    try:
        # Run Flask server
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    finally:
        picam2.stop()
        dht.exit()
        print("Cleanup complete. Goodbye!")
