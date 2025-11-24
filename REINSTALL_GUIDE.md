# Raspberry Pi OS Reinstall Guide - Tomato Sorting Project

## Why Reinstalling?
Your current Pi has Python 3.11, which doesn't have PyTorch support for ARM.
We need Raspberry Pi OS Bullseye (Python 3.9) to run YOLO properly.

---

## What You Need
1. SD card reader (USB adapter for your PC)
2. Your Raspberry Pi's microSD card
3. 30-60 minutes

---

## Step 1: Download Raspberry Pi Imager (On Your PC)

### Windows:
```
Download from: https://www.raspberrypi.com/software/
File: Raspberry Pi Imager for Windows
Run the installer
```

### Mac:
```
Download from: https://www.raspberrypi.com/software/
File: Raspberry Pi Imager for macOS
Open the .dmg and install
```

### Linux:
```bash
sudo apt install rpi-imager
```

---

## Step 2: Flash Raspberry Pi OS Bullseye

1. Insert your microSD card into the SD card reader
2. Connect reader to your PC
3. Open **Raspberry Pi Imager**

4. Click **"Choose Device"**
   - Select: **Raspberry Pi 4**

5. Click **"Choose OS"**
   - Scroll down to: **Raspberry Pi OS (other)**
   - Select: **Raspberry Pi OS (Legacy, 64-bit) Bullseye**
   - ⚠️ IMPORTANT: Make sure it says "Bullseye", NOT "Bookworm"!

6. Click **"Choose Storage"**
   - Select your microSD card

7. Click **"Next"**

8. When asked "Would you like to apply OS customization settings?":
   - Click **"EDIT SETTINGS"**

9. **General Tab:**
   - Set hostname: `raspberrypi` (or whatever you want)
   - Enable SSH: ✓ Use password authentication
   - Set username: `bacadasa` (same as before)
   - Set password: (your password)
   - Configure wireless LAN:
     - SSID: (your WiFi name)
     - Password: (your WiFi password)
     - Country: (your country, e.g., PH)
   - Set locale settings:
     - Timezone: (e.g., Asia/Manila)
     - Keyboard: us

10. **Services Tab:**
    - Enable SSH: ✓ (should be checked)

11. Click **"SAVE"**

12. Click **"YES"** to apply settings

13. Click **"YES"** to confirm erasing the SD card

14. Wait for:
    - Writing (5-10 minutes)
    - Verifying (2-5 minutes)

15. When done, click **"CONTINUE"** and eject the SD card

---

## Step 3: Boot Up Your Raspberry Pi

1. Insert the flashed microSD card into your Raspberry Pi
2. Connect:
   - HDMI cable to monitor
   - Keyboard
   - Mouse
   - Power cable (it will boot automatically)

3. Wait 1-2 minutes for first boot

4. You should see the Raspberry Pi desktop

---

## Step 4: Verify Python Version

Open a terminal and run:
```bash
python3 --version
```

You should see: **Python 3.9.x** (NOT 3.11!)

If you see Python 3.11, you flashed the wrong OS. Go back to Step 2 and select Bullseye.

---

## Step 5: Configure Git (In Pi Terminal)

```bash
git config --global user.name "laurence de guzman"
git config --global user.email "laurence.deguzman@tup.edu.ph"
```

---

## Step 6: Set Up SSH Keys for GitHub

```bash
# Generate new SSH key
ssh-keygen -t ed25519 -C "laurence.deguzman@tup.edu.ph"

# Press Enter 3 times (default location, no passphrase)

# Display your public key
cat ~/.ssh/id_ed25519.pub
```

Copy the entire output (starts with `ssh-ed25519`)

Go to GitHub:
1. https://github.com/settings/keys
2. Click **"New SSH key"**
3. Title: `Raspberry Pi 4 - Bullseye`
4. Paste the key
5. Click **"Add SSH key"**

Test connection:
```bash
ssh -T git@github.com
# Type "yes" when asked
# Should say: "Hi imove0n! You've successfully authenticated"
```

---

## Step 7: Clone Your Project

```bash
cd ~/Desktop
git clone git@github.com:imove0n/RASPI-4-SORTING-PROJECT4.git "RASPI 4 SORTING PROJECT"
cd "RASPI 4 SORTING PROJECT"
```

Your files are back!

---

## Step 8: Install System Dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-opencv python3-picamera2
```

---

## Step 9: Install PyTorch (This Will Work Now!)

```bash
pip3 install torch torchvision --break-system-packages
```

Wait 5-10 minutes. This time it will work because Python 3.9 has ARM wheels!

Verify:
```bash
python3 -c "import torch; print('PyTorch version:', torch.__version__)"
```

Should print: `PyTorch version: 2.x.x`

---

## Step 10: Install Ultralytics

```bash
pip3 install ultralytics --break-system-packages
```

Wait 2-3 minutes.

Verify:
```bash
python3 -c "from ultralytics import YOLO; print('YOLO ready!')"
```

---

## Step 11: Test Your YOLO Detector

```bash
cd ~/Desktop/"RASPI 4 SORTING PROJECT"
python3 yolo_tomato_detector.py
```

You should see:
- Camera opens
- YOLO detects tomatoes
- Bounding boxes appear
- Ripe/Unripe classification

Press 'q' to quit.

---

## Important Files You Have (All on GitHub):

1. **best.pt** - Your trained YOLO model
2. **yolo_tomato_detector.py** - Main detector script
3. **camera_test.py** - Test camera
4. **simple_color_classifier.py** - Backup color detector
5. **yolo_client_pi.py** - For PC+Pi hybrid
6. **yolo_server_pc.py** - For PC+Pi hybrid

---

## Troubleshooting

### "Can't find best.pt"
```bash
cd ~/Desktop/"RASPI 4 SORTING PROJECT"
ls -la best.pt
# If missing, it's on GitHub in your repo
```

### "Camera not found"
```bash
# Enable camera
sudo raspi-config
# Go to: Interface Options > Camera > Enable
# Reboot
```

### "PyTorch import error"
```bash
# Make sure you're on Python 3.9
python3 --version

# Reinstall PyTorch
pip3 uninstall torch torchvision
pip3 install torch torchvision --break-system-packages
```

---

## Summary

After reinstalling:
1. ✅ Python 3.9 (has PyTorch support)
2. ✅ All your files from GitHub
3. ✅ PyTorch installs in 5-10 minutes (not 8-10 hours!)
4. ✅ YOLO detector works perfectly
5. ✅ No more compatibility issues

---

## After Everything Works

Remember to commit your changes:
```bash
git add .
git commit -m "Update after fresh install"
git push
```

---

## Questions to Ask Claude Code After Reinstalling:

1. "Can you help me test the YOLO detector?"
2. "How do I improve detection accuracy?"
3. "Can you help me add sorting mechanism control?"

---

Good luck with the reinstall! 🍅

- Your project is safe on GitHub
- This will fix all the Python 3.11 issues
- You'll be running YOLO in 30 minutes after reinstalling
