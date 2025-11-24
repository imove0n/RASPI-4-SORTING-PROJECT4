DHT22 TEMPERATURE & HUMIDITY SENSOR PROJECT
===========================================
Complete Guide for Students

PROJECT OVERVIEW:
================
This project uses a DHT22 sensor connected to a Raspberry Pi 4 to measure
temperature and humidity. The data can be viewed in multiple ways:
1. Terminal display (live monitoring)
2. Web dashboard (accessible from any device on WiFi)
3. Blynk app (requires additional setup)


HARDWARE SETUP:
===============

DHT22 Sensor Wiring:
-------------------
Pin 1 (VCC)  → Raspberry Pi Pin 1 (3.3V Power)
Pin 2 (DATA) → Raspberry Pi Pin 7 (GPIO4)
Pin 3 (NC)   → Not connected
Pin 4 (GND)  → Raspberry Pi Pin 6 (Ground)

Pin Location:
-------------
- Looking at Raspberry Pi with USB ports facing you
- Pin 1 is at the TOP LEFT corner (opposite side from USB)
- Pin 7 is 4th pin down on the LEFT side
- Pin 6 is 3rd pin down on the RIGHT side

IMPORTANT: Make sure all wires are firmly connected!


HOW TO USE THIS PROJECT:
========================

OPTION 1: LIVE TERMINAL MONITOR (Recommended)
----------------------------------------------
Shows real-time temperature and humidity on the terminal screen.

Command:
  cd "Desktop/RASPI 4 SORTING PROJECT"
  python3 dht22_monitor.py

What you'll see:
- Live readings every 3 seconds
- Temperature in °C and °F
- Humidity percentage
- Change indicators (UP/DOWN arrows)
- Success rate statistics

To stop: Press Ctrl+C


OPTION 2: WEB DASHBOARD (View on Phone/Browser)
-----------------------------------------------
Creates a web server that you can access from any device on the same WiFi.

Command:
  cd "Desktop/RASPI 4 SORTING PROJECT"
  python3 dht22_web_dashboard.py

You'll see output like:
  Server starting on: http://192.168.100.18:5000

  Access from:
    - Your phone:   http://192.168.100.18:5000

On Your Phone/Computer:
1. Make sure device is on SAME WiFi as Raspberry Pi
2. Open web browser (Chrome, Safari, etc.)
3. Type the URL shown (your IP will be different)
4. See beautiful live dashboard with auto-updates!

Features:
- Auto-updates every 3 seconds (no refresh needed)
- Clean, modern design
- Shows temperature and humidity
- Change detection
- Success rate statistics
- Works on any device with browser

To stop: Press Ctrl+C in the terminal


OPTION 3: QUICK SINGLE READING
-------------------------------
Get one quick temperature and humidity reading.

Command:
  cd "Desktop/RASPI 4 SORTING PROJECT"
  python3 dht22_simple.py

Output:
  Temperature: 29.5°C (85.1°F)
  Humidity: 73.4%


OPTION 4: DIAGNOSTIC TEST
--------------------------
Test if the sensor is working properly.

Command:
  cd "Desktop/RASPI 4 SORTING PROJECT"
  python3 test_gpio.py

This will:
- Check GPIO availability
- Test sensor connection
- Show a test reading
- Display any errors


COMMON ISSUES & SOLUTIONS:
==========================

Issue: "Sensor read error" or "DHT sensor not found"
----------------------------------------------------
Solution:
1. Check all 3 wire connections are FIRMLY connected
2. Wait 15-30 seconds (sensor needs recovery time)
3. Run diagnostic: python3 test_gpio.py
4. If problem persists, try different jumper wires

IMPORTANT: DHT22 sensors occasionally fail reads - this is NORMAL!
Success rate of 60-70% is considered good.


Issue: "Address already in use" (Web Dashboard)
------------------------------------------------
Solution:
Another instance is already running. Stop it first:
  pkill -f dht22_web_dashboard.py
Then start again:
  python3 dht22_web_dashboard.py


Issue: Can't access web dashboard from phone
---------------------------------------------
Solution:
1. Make sure phone is on SAME WiFi network
2. Check the IP address in terminal output
3. Type EXACT URL including :5000 at the end
4. Make sure firewall isn't blocking port 5000


Issue: Multiple consecutive errors (5+)
----------------------------------------
Solution:
1. Press all wire connections firmly
2. Wait 30 seconds
3. Check wiring diagram above
4. Run: python3 test_gpio.py
5. If still failing, check sensor for physical damage


IMPORTANT NOTES:
================

Sensor Limitations:
------------------
- DHT22 requires 2-3 seconds between readings
- Occasional errors are NORMAL (success rate 60-70% is good)
- Wait 15 seconds between running different scripts
- Sensor responds to breath (temp/humidity increase)
- Sensor responds to touch (temperature increases)


Best Practices:
--------------
1. Always wait 10-15 seconds between script runs
2. Don't run multiple scripts at the same time
3. Keep wires firmly connected
4. Don't touch sensor during readings
5. Use Ctrl+C to stop scripts properly


Testing the Sensor:
------------------
To see dynamic changes:
1. Run: python3 dht22_monitor.py
2. Breathe on the sensor gently
3. Watch temperature and humidity increase!
4. Wait a moment and see values return to normal


PROJECT FILES:
=============

Main Scripts:
------------
dht22_monitor.py          - Live terminal monitor (BEST FOR DEMOS)
dht22_web_dashboard.py    - Web dashboard server
dht22_simple.py           - Quick single reading
dht22_test_changes.py     - 5 readings with change detection
test_gpio.py              - Diagnostic test

Documentation:
-------------
STUDENT_README.txt               - This file (main guide)
README.txt                       - Complete project documentation
WEB_DASHBOARD_GUIDE.txt          - Detailed web dashboard guide
DHT22_TROUBLESHOOTING.txt        - Troubleshooting guide
gpio_pinout.txt                  - Wiring reference
BLYNK_SETUP_GUIDE.txt           - Blynk app setup (advanced)

Web Dashboard Files:
-------------------
templates/dashboard.html         - Web interface
dht22_web_dashboard.py          - Server script


QUICK COMMAND REFERENCE:
========================

View live data on terminal:
  python3 dht22_monitor.py

Start web dashboard:
  python3 dht22_web_dashboard.py

Get quick reading:
  python3 dht22_simple.py

Test sensor:
  python3 test_gpio.py

Stop any script:
  Press Ctrl+C

Find Raspberry Pi IP address:
  hostname -I


DEMONSTRATIONS FOR STUDENTS:
============================

Demo 1: Basic Functionality
---------------------------
1. Show hardware setup (point to wiring)
2. Run: python3 dht22_simple.py
3. Show one reading
4. Explain temperature and humidity values

Demo 2: Live Monitoring
-----------------------
1. Run: python3 dht22_monitor.py
2. Show continuous updates
3. Breathe on sensor to show change detection
4. Explain success rate statistics

Demo 3: Web Dashboard
--------------------
1. Run: python3 dht22_web_dashboard.py
2. Show IP address in terminal
3. Open on phone/browser
4. Show live updates
5. Breathe on sensor to show dynamic changes
6. Explain auto-update feature

Demo 4: Sensor Behavior
-----------------------
1. Run live monitor
2. Touch sensor gently (temperature increases)
3. Breathe on sensor (both increase)
4. Wave paper near sensor (air movement)
5. Explain sensor sensitivity


UNDERSTANDING THE DATA:
======================

Temperature:
-----------
- Measured in °C (Celsius)
- Also shown in °F (Fahrenheit)
- Room temperature: typically 20-25°C (68-77°F)
- Human body temperature raises it to ~30-35°C when touched

Humidity:
--------
- Measured in % (percentage)
- Indoor comfort: 40-60%
- Breath is very humid (increases to 80-90%)
- Lower values = drier air
- Higher values = more moisture in air

Success Rate:
------------
- Percentage of successful sensor readings
- 60-70% is GOOD for DHT22
- Lower rate = check wiring
- Don't expect 100% (sensor limitation)


EXPERIMENT IDEAS:
=================

1. Temperature Mapping:
   - Measure temperature in different rooms
   - Compare morning vs. afternoon
   - Check near windows vs. center of room

2. Humidity Changes:
   - Measure before and after opening windows
   - Check bathroom after shower
   - Compare kitchen while cooking

3. Response Time:
   - Breathe on sensor and time how long to return to normal
   - Measure how quickly ice affects temperature
   - Track room temperature changes over 24 hours

4. Data Logging:
   - Run web dashboard for extended period
   - Note highest/lowest readings
   - Identify patterns throughout the day


PYTHON LIBRARIES USED:
======================

adafruit-circuitpython-dht  - DHT22 sensor communication
flask                       - Web server framework
flask-cors                  - Cross-origin resource sharing
board                       - GPIO pin management
requests                    - HTTP requests (for Blynk)


TECHNICAL SPECIFICATIONS:
=========================

DHT22 Sensor:
------------
- Temperature Range: -40°C to 80°C
- Humidity Range: 0-100%
- Accuracy: ±0.5°C, ±2-5% RH
- Resolution: 0.1°C, 0.1% RH
- Sampling Rate: 0.5 Hz (once every 2 seconds)
- Operating Voltage: 3.3-6V DC
- Communication: Single-wire digital signal

Raspberry Pi GPIO:
-----------------
- GPIO4 (Pin 7): Data pin for sensor
- 3.3V (Pin 1): Power supply
- Ground (Pin 6): Common ground


SAFETY NOTES:
=============

1. Don't connect/disconnect wires while Pi is powered on
2. Double-check wiring before powering on
3. Don't expose sensor to extreme temperatures
4. Don't get sensor wet (it's not waterproof!)
5. Handle electronics with care


TROUBLESHOOTING CHECKLIST:
==========================

If sensor not working:
□ Check all 3 wires are firmly connected
□ Verify correct GPIO pin (Pin 7 = GPIO4)
□ Verify power connected to Pin 1 (3.3V)
□ Verify ground connected to Pin 6
□ Wait 30 seconds and try again
□ Run diagnostic: python3 test_gpio.py
□ Try different jumper wires
□ Check sensor for physical damage

If web dashboard not accessible:
□ Check server is running (no errors in terminal)
□ Verify phone on same WiFi network
□ Use exact IP address from terminal
□ Include :5000 at end of URL
□ Try accessing from Raspberry Pi browser first
□ Check firewall settings


FOR INSTRUCTORS:
================

This project demonstrates:
- IoT (Internet of Things) concepts
- Sensor interfacing with GPIO
- Python programming
- Web server creation
- Real-time data visualization
- Error handling in hardware projects
- Wireless communication

Learning Objectives:
- Understand digital sensor communication
- Learn GPIO programming
- Create web-based interfaces
- Implement real-time updates
- Debug hardware connections
- Handle sensor errors gracefully


CREDITS & LICENSE:
==================

Project created for educational purposes
Uses Adafruit CircuitPython libraries
Flask web framework
DHT22 sensor by Aosong Electronics

This project is free to use and modify for educational purposes.


NEED HELP?
==========

1. Read DHT22_TROUBLESHOOTING.txt for detailed solutions
2. Check wiring against gpio_pinout.txt
3. Run diagnostic: python3 test_gpio.py
4. Make sure you waited 15 seconds between script runs
5. Verify all connections are firm


QUICK START FOR NEW STUDENTS:
=============================

1. Check hardware wiring (see diagram above)
2. Open terminal
3. cd "Desktop/RASPI 4 SORTING PROJECT"
4. python3 dht22_monitor.py
5. Watch live temperature and humidity!
6. Press Ctrl+C when done

That's it! You're monitoring temperature and humidity! 🌡️💧


FINAL TIPS:
===========

✓ Always run scripts from the project directory
✓ Wait between script runs (15 seconds)
✓ Check wiring if you get many errors
✓ Success rate of 60-70% is normal
✓ Use web dashboard for best demonstrations
✓ Breathe on sensor to show it working
✓ Have fun experimenting!


Good luck with your project! 🚀
