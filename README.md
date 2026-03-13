# Tomato Sorting System with YOLO Detection

A Raspberry Pi 4-based tomato sorting system using YOLO object detection and dual DHT22 environmental sensors with real-time web dashboard monitoring.

---

## Features

- **YOLO Object Detection**: Custom-trained model for ripe/unripe tomato classification
- **Dual DHT22 Sensors**: Real-time temperature and humidity monitoring for both containers
- **Web Dashboard**: Mobile-responsive interface accessible from any device on the network
- **Automatic Counting**: Smart tomato counting system with slow increment simulation
- **Reliability**: Cached sensor values for smooth operation during sensor failures
- **Network Access**: Monitor from phone, tablet, or computer on the same WiFi

---

## Hardware Requirements

### Components
- Raspberry Pi 4
- Pi Camera Module (CSI)
- 2x DHT22 Temperature/Humidity Sensors
- Jumper wires
- Breadboard (optional)

### DHT22 Sensor Wiring

**Sensor 1 (UNRIPE Container - GPIO 4)**
```
VCC (Red)    → Pin 1  (3.3V)
DATA (Yellow) → Pin 7  (GPIO 4)
GND (Black)   → Pin 6  (Ground)
```

**Sensor 2 (RIPE Container - GPIO 23)**
```
VCC (Red)    → Pin 17 (3.3V)
DATA (Yellow) → Pin 16 (GPIO 23)
GND (Black)   → Pin 14 (Ground)
```

---

## Software Requirements

- Raspberry Pi OS Bullseye (Python 3.9)
- Python 3.9+
- Flask
- OpenCV
- PyTorch
- Ultralytics YOLO
- Adafruit DHT22 Library
- Picamera2

---

## Installation

### 1. Clone the Repository
```bash
cd ~/Desktop
git clone https://github.com/imove0n/RASPI-4-SORTING-PROJECT4.git
cd RASPI-4-SORTING-PROJECT4
```

### 2. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv python3-picamera2
```

### 3. Install Python Packages
```bash
pip3 install torch torchvision --break-system-packages
pip3 install ultralytics --break-system-packages
pip3 install flask flask-cors adafruit-dht --break-system-packages
```

### 4. Enable Camera
```bash
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
# Reboot when prompted
```

---

## Usage

### Starting the Dashboard Server

```bash
cd ~/Desktop/RASPI-4-SORTING-PROJECT4
python3 dht22_web_dashboard.py
```

The server will display:
```
============================================================
DHT22 WEB DASHBOARD SERVER
============================================================

Server starting on: http://192.168.100.18:5000

Access from:
  - This device:  http://localhost:5000
  - Your phone:   http://192.168.100.18:5000
  - Any browser:  http://192.168.100.18:5000
```

**Leave this terminal running!**

### Accessing the Dashboard

**On Raspberry Pi:**
```
http://localhost:5000
```

**On Phone/Tablet:**
1. Connect to the same WiFi network
2. Open browser: `http://192.168.100.18:5000` (use IP shown in terminal)

---

## Running YOLO Detection

Open a **new terminal** (keep dashboard running):

```bash
cd ~/Desktop/RASPI-4-SORTING-PROJECT4
python3 yolo_tomato_detector.py
```

**Features:**
- Live camera feed with bounding boxes
- Green boxes: Unripe tomatoes
- Red boxes: Ripe tomatoes
- FPS counter (optimized for 4-5 FPS)
- Detection count

**To stop:** Press `q` key

---

## Dashboard Features

### UNRIPE Container (Green)
- Real-time temperature from DHT22 Sensor #1
- Real-time humidity from DHT22 Sensor #1
- Tomato count: Increases by 1 every 20 seconds
- Status badge: "🌡️ REAL DHT22 SENSOR" or "📊 SIMULATED DATA (Sensor Offline)"

### RIPE Container (Red)
- Real-time temperature from DHT22 Sensor #2
- Real-time humidity from DHT22 Sensor #2
- Tomato count: Static at 85 (prevents browser lag)
- Status badge: "🌡️ REAL DHT22 SENSOR" or "📊 SIMULATED DATA (Sensor Offline)"

### Dashboard Updates
- Auto-refresh every 2 seconds
- Timestamp display
- Cached values during sensor failures
- Mobile-responsive design

---

## Testing Sensors

**Important:** Stop the dashboard before running sensor tests!

```bash
# Stop dashboard: Press Ctrl+C

# Run sensor test
python3 test_dht22_both.py
```

**Output:**
- Pin configuration verification
- 5 readings from each sensor
- Success/failure statistics
- Success rate percentage

**Restart dashboard after testing:**
```bash
python3 dht22_web_dashboard.py
```

---

## Project Structure

```
RASPI-4-SORTING-PROJECT4/
├── dht22_web_dashboard.py        # Main dashboard server
├── yolo_tomato_detector.py       # YOLO detection script
├── test_dht22_both.py            # Sensor testing utility
├── best.pt                       # Trained YOLO model weights
├── templates/
│   └── dashboard.html            # Web dashboard interface
├── REINSTALL_GUIDE.md            # OS reinstallation guide
└── README.md                     # This file
```

---

## Technical Details

### YOLO Model
- Custom-trained on tomato dataset
- Classes: `ripe`, `unripe`
- Optimized for Raspberry Pi 4
- Performance: 4-5 FPS

### DHT22 Sensors
- Temperature range: -40°C to 80°C (±0.5°C accuracy)
- Humidity range: 0-100% (±2-5% accuracy)
- Read interval: 2 seconds
- Note: 40-60% failure rate is normal for DHT22 sensors

### Counting System
- **UNRIPE**: Time-based increment (1 per 20 seconds)
- **RIPE**: Static count (85 tomatoes)
- **ROTTEN**: Random range (5-12 tomatoes)

---

## Troubleshooting

### Dashboard shows "Sensor Offline"
- Check sensor wiring (VCC, DATA, GND)
- DHT22 sensors have inherent reliability issues (40-60% failure rate)
- System automatically uses cached values

### Can't access dashboard from phone
- Verify phone is on same WiFi network as Raspberry Pi
- Check Raspberry Pi IP: `hostname -I`
- Use correct IP address in browser

### "GPIO busy" error
- Only one program can access GPIO pins at a time
- Stop dashboard before running sensor tests
- Kill existing processes: `sudo pkill -f dht22`

### YOLO detector is slow
- 4-5 FPS is normal and expected on Raspberry Pi 4
- Performance is already optimized
- Higher FPS requires more powerful hardware

### Camera not found
```bash
sudo raspi-config
# Interface Options > Camera > Enable
sudo reboot
```

### PyTorch import error
- Verify Python version: `python3 --version` (should be 3.9)
- Reinstall PyTorch:
  ```bash
  pip3 uninstall torch torchvision
  pip3 install torch torchvision --break-system-packages
  ```

---

## Git Configuration

### Set up Git credentials
```bash
git config --global user.name "Laurence De Guzman"
git config --global user.email "laurence.deguzman@tup.edu.ph"
```

### Push changes to GitHub
```bash
git add .
git commit -m "Your commit message"
git push
```

**Authentication:**
- Username: `imove0n`
- Password: Use GitHub Personal Access Token (not password)

**Create token at:** https://github.com/settings/tokens
- Select: `repo` (Full control of private repositories)
- Copy token (starts with `ghp_...`)

---

## Performance Metrics

- **YOLO FPS**: 4-5 FPS (Raspberry Pi 4)
- **Dashboard Refresh**: 2 seconds
- **Sensor Read Rate**: Every 2 seconds
- **DHT22 Success Rate**: 40-60% (typical)
- **Network Latency**: <100ms (local network)

---

## System Architecture

```
┌─────────────────┐
│  Pi Camera      │
│  (CSI Port)     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│   YOLO Object Detection             │
│   - Detect tomatoes                 │
│   - Classify ripe/unripe            │
│   - Draw bounding boxes             │
└─────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐
│  DHT22 Sensor 1 │     │  DHT22 Sensor 2 │
│  (GPIO 4)       │     │  (GPIO 23)      │
│  UNRIPE         │     │  RIPE           │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌─────────────────────┐
         │   Flask Web Server  │
         │   (Port 5000)       │
         └──────────┬──────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
         ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│  Web Dashboard  │   │  Mobile Browser │
│  (Desktop)      │   │  (Phone/Tablet) │
└─────────────────┘   └─────────────────┘
```

---

## Stopping the System

### Stop Dashboard
In the dashboard terminal:
```bash
Ctrl+C
```

### Stop YOLO Detector
Press `q` in the camera window or `Ctrl+C` in terminal

### Shutdown Raspberry Pi
```bash
sudo shutdown now
```

---

## Credits

**Developer:** Laurence De Guzman
**Email:** laurence.deguzman@tup.edu.ph
**Institution:** Technological University of the Philippines
**Repository:** https://github.com/imove0n/RASPI-4-SORTING-PROJECT4

---

## License

This project is for educational purposes.

---

## Future Enhancements

- [ ] Add sorting mechanism control (servo motors)
- [ ] Implement data logging to CSV/database
- [ ] Add email/SMS alerts for abnormal conditions
- [ ] Improve YOLO detection accuracy
- [ ] Add historical graphs for temperature/humidity
- [ ] Implement user authentication
- [ ] Add API endpoints for external integration
- [ ] Support for additional sensor types

---

## Additional Documentation

For detailed reinstallation guide (switching to Raspberry Pi OS Bullseye), see [REINSTALL_GUIDE.md](REINSTALL_GUIDE.md)

---

**Last Updated:** November 25, 2025

🍅 Happy Sorting!



hostname -I

