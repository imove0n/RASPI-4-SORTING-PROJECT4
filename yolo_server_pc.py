#!/usr/bin/env python3
"""
YOLO Server for PC
Receives images from Pi, runs YOLO detection, sends back results
Run this on your PC/Laptop with PyTorch installed
"""

from flask import Flask, request, jsonify
from ultralytics import YOLO
import cv2
import numpy as np

app = Flask(__name__)

print("=" * 70)
print("🍅 YOLO TOMATO DETECTOR - PC Server")
print("=" * 70)
print()

# Load YOLO model
MODEL_PATH = "best.pt"  # Put your best.pt in same folder as this script
print(f"📦 Loading YOLO model: {MODEL_PATH}")
model = YOLO(MODEL_PATH)
print("✅ Model loaded successfully!")
print()

class_names = model.names
print(f"📋 Detection classes: {class_names}")
print()

@app.route('/detect', methods=['POST'])
def detect():
    """Receive image, run YOLO, return detections"""
    try:
        # Get image from request
        file = request.files['image']
        img_bytes = file.read()

        # Decode image
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Run YOLO detection
        results = model(img, verbose=False)

        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                confidence = float(box.conf[0])

                # Only return detections above 50% confidence
                if confidence > 0.5:
                    x1, y1, x2, y2 = box.xyxy[0]
                    class_id = int(box.cls[0])
                    class_name = class_names[class_id]

                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'class': class_name,
                        'confidence': confidence
                    })

        return jsonify({'detections': detections})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting server...")
    print("Listening on http://0.0.0.0:5000")
    print()
    print("Pi can connect using your PC's IP address")
    print("Find your PC's IP with: ipconfig (Windows) or ifconfig (Mac/Linux)")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()

    app.run(host='0.0.0.0', port=5000, debug=False)
