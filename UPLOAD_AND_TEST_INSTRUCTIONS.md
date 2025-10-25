# Arduino Mega - Upload and Test Instructions

## ⚠️ CRITICAL WIRING NOTE - RFID READER

**The MFRC522 RFID reader MUST be rewired to use hardware SPI pins:**

### Required RFID Wiring Changes:
```
OLD (Custom SPI pins - NOT SUPPORTED):
❌ MOSI → Pin 35
❌ MISO → Pin 33
❌ SCK  → Pin 37

NEW (Hardware SPI pins - REQUIRED):
✅ MOSI → Pin 51 (shared with LED Matrix)
✅ MISO → Pin 50 (shared with LED Matrix)
✅ SCK  → Pin 52 (shared with LED Matrix)
✅ SS   → Pin 39 (unchanged)
✅ RST  → Pin 8 (unchanged)
```

**Why?** The standard MFRC522 library only supports hardware SPI. Both the LED Matrix and RFID can share the SPI bus (pins 50, 51, 52) as long as they have unique chip select (CS/SS) pins.

---

## Step 1: Install Required Arduino Libraries

Before uploading, you need to install these libraries in Arduino IDE:

### Method 1: Arduino IDE Library Manager (Recommended)
1. Open Arduino IDE
2. Go to: **Sketch → Include Library → Manage Libraries**
3. Search and install each library:

```
Required Libraries:
- DHT sensor library (by Adafruit)
- Adafruit Unified Sensor (dependency for DHT)
- MFRC522 (by GithubCommunity)
- LedControl (by Eberhard Fahle)
```

### Method 2: Manual Installation
```bash
cd ~/Arduino/libraries/

# DHT Sensor Library
git clone https://github.com/adafruit/DHT-sensor-library.git
git clone https://github.com/adafruit/Adafruit_Sensor.git

# MFRC522 RFID Library
git clone https://github.com/miguelbalboa/rfid.git MFRC522

# LedControl Library
git clone https://github.com/wayoda/LedControl.git
```

---

## Step 2: Upload the Sketch

### Option A: Arduino IDE (Recommended)

1. **Open Arduino IDE:**
   ```bash
   arduino
   ```

2. **Open the sketch:**
   - File → Open
   - Navigate to: `/home/mz1312/Sentient-Core-v4/arduino_sketch/arduino_sketch.ino`

3. **Configure Board:**
   - Tools → Board → Arduino AVR Boards → **Arduino Mega or Mega 2560**
   - Tools → Processor → **ATmega2560 (Mega 2560)**
   - Tools → Port → **/dev/ttyACM0** (Arduino Mega)

4. **Verify the sketch:**
   - Click the ✓ (Verify) button
   - Check for any compilation errors
   - If libraries are missing, install them (see Step 1)

5. **Upload:**
   - Click the → (Upload) button
   - Wait for "Done uploading" message
   - The built-in LED should flash during upload

### Option B: Arduino CLI (Advanced)

```bash
# Install Arduino CLI (if not already installed)
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
export PATH=$PATH:$HOME/bin

# Initialize and install core
arduino-cli core update-index
arduino-cli core install arduino:avr

# Install required libraries
arduino-cli lib install "DHT sensor library"
arduino-cli lib install "Adafruit Unified Sensor"
arduino-cli lib install "MFRC522"
arduino-cli lib install "LedControl"

# Compile and upload
cd /home/mz1312/Sentient-Core-v4/arduino_sketch
arduino-cli compile --fqbn arduino:avr:mega .
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:mega .
```

---

## Step 3: Verify Upload with Hardware Test

After uploading, wait 5 seconds for the Arduino to reset, then run:

```bash
cd /home/mz1312
python3 hardware_test.py
```

### Expected Output (Success):
```
2025-10-22 15:00:00,000 - INFO - --- Starting Arduino Hardware Diagnostic Test ---
2025-10-22 15:00:00,001 - INFO - Attempting to connect to Arduino on /dev/ttyACM0 at 115200 bps...
2025-10-22 15:00:00,003 - INFO - Serial port opened successfully. Waiting for Arduino to reset...
2025-10-22 15:00:02,005 - INFO - Sending handshake command: PING
2025-10-22 15:00:02,107 - INFO - Received response: 'PONG'
2025-10-22 15:00:02,107 - INFO - ✓ SUCCESS: Handshake successful. Arduino is responsive.
2025-10-22 15:00:02,107 - INFO - Sending discovery command: GET_PERIPHERALS
2025-10-22 15:00:02,108 - INFO - Reading peripheral list from Arduino...
2025-10-22 15:00:02,210 - INFO -   Found peripheral: PERIPHERAL:dht1:2:sensor
2025-10-22 15:00:02,211 - INFO -   Found peripheral: PERIPHERAL:ultrasonic1:9:sensor
2025-10-22 15:00:02,212 - INFO -   Found peripheral: PERIPHERAL:pir1:24:sensor
2025-10-22 15:00:02,213 - INFO -   Found peripheral: PERIPHERAL:mic1:A3:sensor
2025-10-22 15:00:02,214 - INFO -   Found peripheral: PERIPHERAL:status_led:13:actuator
2025-10-22 15:00:02,215 - INFO -   Found peripheral: PERIPHERAL:led_matrix:14:actuator
2025-10-22 15:00:02,216 - INFO -   Found peripheral: PERIPHERAL:rfid_reader:39:sensor
2025-10-22 15:00:02,217 - INFO - End of peripheral list received.
2025-10-22 15:00:02,217 - INFO - ✓ SUCCESS: Discovered 7 peripherals.
2025-10-22 15:00:02,217 - INFO - Serial port closed.
2025-10-22 15:00:02,218 - INFO - --- Diagnostic Test Complete ---
```

---

## Step 4: Test with ArduinoDaemon

Once `hardware_test.py` succeeds, test the full daemon:

```bash
cd /home/mz1312/Sentient-Core-v4
python3 arduino_daemon.py
```

### Expected Output:
```
INFO - Initializing Arduino daemon...
INFO - Attempting to connect to Arduino on /dev/ttyACM0
INFO - ✓ Arduino connected on /dev/ttyACM0
INFO - Discovering Arduino peripherals...
INFO - Sent 'discover' command to Arduino
INFO -   > Discovered: dht1 (sensor on pin 2)
INFO -   > Discovered: ultrasonic1 (sensor on pin 9)
INFO -   > Discovered: pir1 (sensor on pin 24)
INFO -   > Discovered: mic1 (sensor on pin A3)
INFO -   > Discovered: status_led (actuator on pin 13)
INFO -   > Discovered: led_matrix (actuator on pin 14)
INFO -   > Discovered: rfid_reader (sensor on pin 39)
INFO - ✓ Discovered 7 peripherals

✓ Daemon initialized
✓ Ready to send/receive data from Arduino...

Press Ctrl+C to stop
```

---

## Step 5: Test Individual Peripherals

Once the daemon is running, you can test reading sensors. Open a new terminal:

```bash
# Test PIR motion sensor
echo "read:pir1" | nc -w 1 localhost /dev/ttyACM0

# Test temperature/humidity
echo "read:dht1" | nc -w 1 localhost /dev/ttyACM0

# Test ultrasonic distance
echo "read:ultrasonic1" | nc -w 1 localhost /dev/ttyACM0

# Control status LED (turn on)
echo "write:status_led:1" | nc -w 1 localhost /dev/ttyACM0

# Control status LED (turn off)
echo "write:status_led:0" | nc -w 1 localhost /dev/ttyACM0
```

---

## Troubleshooting

### Upload Fails / Port Not Found
```bash
# Check Arduino is connected
ls -la /dev/ttyACM*

# Check USB device
lsusb | grep -i arduino

# Try different port
arduino-cli board list
```

### Compilation Errors - Missing Libraries
```
ERROR: MFRC522.h: No such file or directory
```
**Solution:** Install missing libraries (see Step 1)

### PING Test Fails
1. Wait 5-10 seconds after upload (Arduino needs to boot)
2. Unplug and replug USB cable
3. Close Arduino IDE Serial Monitor (conflicts with test script)
4. Verify baud rate is 115200 in sketch

### No Peripherals Discovered
1. Open Arduino IDE Serial Monitor (Tools → Serial Monitor)
2. Set baud rate to 115200
3. Type `GET_PERIPHERALS` and press Enter
4. Should see list of 7 peripherals
5. If nothing appears, re-upload sketch

### DHT Sensor Errors
```
ERROR:DHT_READ_FAILED
```
- Check DHT11 wiring (VCC to 5V, GND to GND, DATA to Pin 2)
- DHT sensors need 1-2 seconds to stabilize after power-on
- Try reading again after a few seconds

### RFID Not Working
```
ERROR:RFID_READ_FAILED
```
- Verify RFID is wired to Hardware SPI pins (50, 51, 52)
- Check RST pin is on Pin 8
- Check SS pin is on Pin 39
- RFID requires a card to be present to read (won't return data without a card)

---

## Success Criteria

✅ **Hardware test passes** with PONG response
✅ **7 peripherals discovered** in GET_PERIPHERALS
✅ **ArduinoDaemon initializes** without errors
✅ **PIR sensor reads** 0 or 1 (motion detected/not detected)
✅ **Status LED can be controlled** (on/off)

Once all these succeed, the Sentient Core will be able to "see" through its sensors! 🎉

---

## Next Steps

After successful testing:
1. The **WorldState** will receive sensor data
2. The **ArduinoDaemon** will poll sensors at 1 Hz
3. **Motion events** from PIR will trigger alerts
4. The "Sense, Think, Act" loop will be operational

You can then run the full Sentient Aura system:
```bash
cd /home/mz1312/Sentient-Core-v4
python3 sentient_aura_main.py
```
