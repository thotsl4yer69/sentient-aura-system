# Peripheral Configuration Guide

Complete configuration guide for Flipper Zero, Arduino, and Coral TPU.

## Table of Contents
- [Coral TPU Configuration](#coral-tpu-configuration)
- [Flipper Zero Configuration](#flipper-zero-configuration)
- [Arduino Configuration](#arduino-configuration)
- [Serial Port Management](#serial-port-management)
- [Model Deployment](#model-deployment)

---

## Coral TPU Configuration

### Verify Coral Detection

```bash
# Check USB detection
lsusb | grep "18d1:9302"
# Expected: Bus XXX Device XXX: ID 18d1:9302 Google Inc.

# Check Edge TPU detection
cd ~/Sentient-Core-v4
~/.pyenv/versions/coral-py39/bin/python -c "
from pycoral.utils import edgetpu
devices = edgetpu.list_edge_tpus()
print(f'Found {len(devices)} Coral TPU(s)')
for i, dev in enumerate(devices):
    print(f'  Device {i}: {dev}')
"
```

### Expected Output:
```
Found 1 Coral TPU(s)
  Device 0: {'type': 'usb', 'path': '/sys/bus/usb/devices/2-1'}
```

### Model Deployment

The Enhanced Sentient Core uses a TensorFlow Lite model compiled for Edge TPU:

**Location**: `models/sentient_viz_enhanced_edgetpu.tflite`

**Model Specification**:
- Input: `[1, 120]` - 120-dimensional feature vector
- Output: `[1, 10000, 3]` - 10,000 particles with X, Y, Z coordinates
- Type: FLOAT32 (enhanced model)
- Size: ~4.0 MB

### Performance Expectations

```bash
# Expected inference times on Pi 5 + Coral TPU:
# - Warmup (first inference): 30-40ms
# - Sustained inference: 2-3ms per frame
# - Theoretical max FPS: 877 FPS (limited by USB 3.0 overhead)
# - Practical target FPS: 60 FPS
```

### Troubleshooting Coral TPU

**"No Edge TPU found"**:
```bash
# Replug Coral into USB 3.0 port
# Check permissions
ls -la /sys/bus/usb/devices/*/idVendor

# Verify udev rules
cat /etc/udev/rules.d/99-edgetpu-accelerator.rules

# Check user is in plugdev group
groups | grep plugdev
```

**"Model failed to load"**:
```bash
# Verify model file exists
ls -lh models/sentient_viz_enhanced_edgetpu.tflite

# Check model is Edge TPU compiled (not regular TFLite)
file models/sentient_viz_enhanced_edgetpu.tflite
# Should show: data (binary model)

# Verify model hash
md5sum models/sentient_viz_enhanced_edgetpu.tflite
```

---

## Flipper Zero Configuration

### Prerequisites

- Flipper Zero with official firmware v0.x or Unleashed firmware
- USB-C cable (data-capable)
- Serial communication enabled

### Verify Flipper Detection

```bash
# Connect Flipper Zero via USB
# Flipper should show "Connected to PC" on screen

# Check serial device
ls -la /dev/flipper /dev/ttyACM*

# Identify Flipper (vendor ID: 0483)
udevadm info /dev/ttyACM0 | grep ID_VENDOR_ID
```

### Flipper Serial Protocol

The Sentient Core communicates with Flipper Zero via serial commands:

**Baud Rate**: 115200
**Data Format**: 8N1 (8 data bits, no parity, 1 stop bit)
**Flow Control**: None

### Supported Commands

```bash
# Test Flipper communication manually
screen /dev/flipper 115200

# Commands (type in screen):
# - "status" → Get Flipper status
# - "scan_subghz" → Scan Sub-GHz frequencies
# - "read_nfc" → Read NFC tag
# - "read_rfid" → Read 125kHz RFID
# - "send_ir:0xFF00" → Send IR signal
```

**Example Session**:
```
> status
OK: Flipper Zero, Battery: 85%, Uptime: 3600s

> scan_subghz
OK: Scanning 433.92 MHz
SIGNAL: 433.92 MHz, RSSI: -45 dBm
END

> read_nfc
OK: NFC scan started
CARD: UID=04:52:B3:A2:C8:90:80, SAK=08, ATQA=0004
END
```

### Flipper Integration in Sentient Core

The `flipper_daemon.py` handles Flipper communication:

```python
# Configuration in sentient_aura_main.py
FLIPPER_PORT = "/dev/flipper"  # or /dev/ttyACM0
FLIPPER_BAUD = 115200

# Features extracted from Flipper:
# - Sub-GHz signal presence (binary)
# - NFC card detected (binary)
# - RFID tag detected (binary)
# - IR signal strength (0.0-1.0)
# - GPIO pin states (8 channels)
```

### Troubleshooting Flipper

**Flipper not responding**:
```bash
# Check Flipper is powered on and unlocked
# Verify serial connection
cat /dev/flipper
# Should show output (Ctrl+C to stop)

# Reset Flipper serial
sudo systemctl restart serial-getty@ttyACM0.service

# Or disconnect/reconnect USB
```

**Permission denied**:
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Temporary fix
sudo chmod 666 /dev/flipper
```

**Multiple ttyACM devices**:
```bash
# Use symlink created by udev rules
ls -la /dev/flipper
# Should point to correct ttyACM device

# If symlink missing, check udev rules
cat /etc/udev/rules.d/99-sentient-serial.rules
```

---

## Arduino Configuration

### Upload Arduino Sketch

The Arduino must run the Sentient Core peripheral firmware:

**Location**: `arduino/sentient_peripherals/sentient_peripherals.ino`

### Upload Instructions

```bash
# Install Arduino CLI (if not installed)
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh

# Add to PATH
export PATH=$PATH:$HOME/bin

# Initialize Arduino CLI
arduino-cli config init

# Install board support (Arduino Mega)
arduino-cli core update-index
arduino-cli core install arduino:avr

# Connect Arduino via USB
# Identify port
arduino-cli board list

# Upload sketch
cd ~/Sentient-Core-v4/arduino/sentient_peripherals
arduino-cli compile --fqbn arduino:avr:mega sentient_peripherals.ino
arduino-cli upload -p /dev/arduino_mega --fqbn arduino:avr:mega sentient_peripherals.ino
```

### Verify Arduino Communication

```bash
# Open serial monitor
screen /dev/arduino_mega 115200

# You should see heartbeat messages:
HEARTBEAT: READY
HEARTBEAT: READY
...

# Test discovery command
# Type: discover
# Expected output:
PERIPHERAL:dht1:2:sensor
PERIPHERAL:ultrasonic1:9:sensor
PERIPHERAL:pir1:24:sensor
PERIPHERAL:mic1:57:sensor
PERIPHERAL:status_led:13:actuator
PERIPHERAL:led_matrix:14:actuator
END_OF_LIST

# Press Ctrl+A, K to exit screen
```

### Arduino Serial Protocol

**Baud Rate**: 115200
**Commands**:
- `discover` - List all connected peripherals
- `read:<peripheral>` - Read sensor value
- `write:<peripheral>:<value>` - Write to actuator

**Response Format**:
```
VALUE:<peripheral>:<value>
```

**Example**:
```
> read:dht1
VALUE:dht1:22.5,45.0

> read:ultrasonic1
VALUE:ultrasonic1:150

> write:status_led:1
OK
```

### Arduino Sensor Mapping

Configured in `arduino/sentient_peripherals/sentient_peripherals.ino`:

```cpp
// Sensor definitions
#define DHT_PIN 2           // Temperature & Humidity
#define TRIG_PIN 9          // Ultrasonic trigger
#define ECHO_PIN 10         // Ultrasonic echo
#define PIR_PIN 24          // Motion sensor (Mega) or 7 (Uno)
#define MIC_PIN A3          // Microphone (analog)
#define STATUS_LED_PIN 13   // Status LED
#define LED_MATRIX_PIN 14   // LED Matrix (optional)
```

### Troubleshooting Arduino

**Arduino not detected**:
```bash
# Check USB connection
lsusb | grep -E "2341|1a86"

# Check dmesg
dmesg | tail -20

# Verify symlink
ls -la /dev/arduino_mega /dev/arduino_uno
```

**Upload fails**:
```bash
# Check board type
arduino-cli board list

# For Arduino Mega:
arduino-cli upload -p /dev/arduino_mega --fqbn arduino:avr:mega

# For Arduino Uno:
arduino-cli upload -p /dev/arduino_uno --fqbn arduino:avr:uno
```

**No sensor data**:
```bash
# Verify sensors are connected
# Check Arduino sketch is uploaded (look for LED blink)

# Test individual sensors
screen /dev/arduino_mega 115200
# Type: read:dht1
# Type: read:ultrasonic1
# Type: read:pir1
```

---

## Serial Port Management

### Port Assignment Strategy

The Sentient Core uses persistent device names via udev rules:

```bash
# Flipper Zero → /dev/flipper
# Arduino Mega → /dev/arduino_mega
# Arduino Uno → /dev/arduino_uno
```

### Verify Port Assignments

```bash
# List all serial devices
ls -la /dev/ttyACM* /dev/flipper /dev/arduino_*

# Expected output:
# /dev/ttyACM0 → First connected device
# /dev/ttyACM1 → Second connected device
# /dev/flipper → Symlink to Flipper (ttyACM0)
# /dev/arduino_mega → Symlink to Arduino (ttyACM1)
```

### Manual Port Identification

```bash
# Identify each device
for dev in /dev/ttyACM*; do
    echo "=== $dev ==="
    udevadm info $dev | grep -E "ID_VENDOR_ID|ID_MODEL|ID_SERIAL"
    echo ""
done

# Vendor IDs:
# Flipper: 0483 (STMicroelectronics)
# Arduino Mega: 2341 (Arduino)
# Arduino Uno (CH340): 1a86 (QinHeng Electronics)
```

### Connection Order Matters

**Best Practice**: Connect in this order to ensure consistent /dev/ttyACM assignment:
1. Flipper Zero first → /dev/ttyACM0
2. Arduino second → /dev/ttyACM1

### Serial Port Mutex

The Sentient Core implements port locking to prevent conflicts:

```python
# In hardware_discovery.py
class SerialPortManager:
    def __init__(self):
        self.locked_ports = set()
        self.lock = threading.Lock()

    def acquire_port(self, port):
        with self.lock:
            if port in self.locked_ports:
                return False
            self.locked_ports.add(port)
            return True

    def release_port(self, port):
        with self.lock:
            self.locked_ports.discard(port)
```

### Troubleshooting Serial Conflicts

**Both devices on same port**:
```bash
# Check udev rules loaded correctly
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reconnect devices in correct order
# 1. Disconnect both
# 2. Connect Flipper
# 3. Wait 2 seconds
# 4. Connect Arduino
```

**Permission denied**:
```bash
# Verify user in dialout group
groups | grep dialout

# If missing:
sudo usermod -a -G dialout $USER
# Log out and back in
```

---

## Model Deployment

### Enhanced Model Files

The system uses two model variants:

**1. Enhanced Edge TPU Model** (Production):
- File: `models/sentient_viz_enhanced_edgetpu.tflite`
- Features: 120 input features
- Output: 10,000 particles × 3D coordinates
- Target: Google Coral USB Accelerator

**2. Standard TFLite Model** (CPU Fallback):
- File: `models/sentient_viz_enhanced.tflite`
- Same architecture, not Edge TPU compiled
- Used when Coral unavailable (slower)

### Deploy New Model

```bash
cd ~/Sentient-Core-v4

# Backup existing model
cp models/sentient_viz_enhanced_edgetpu.tflite \
   models/sentient_viz_enhanced_edgetpu.tflite.backup

# Copy new model
cp /path/to/new/model.tflite models/sentient_viz_enhanced_edgetpu.tflite

# Verify model
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import tflite_runtime.interpreter as tflite

model_path = "models/sentient_viz_enhanced_edgetpu.tflite"
interpreter = tflite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(f"Input shape: {input_details[0]['shape']}")
print(f"Output shape: {output_details[0]['shape']}")
print(f"Input dtype: {input_details[0]['dtype']}")
print(f"Output dtype: {output_details[0]['dtype']}")
EOF

# Expected output:
# Input shape: [  1 120]
# Output shape: [    1 10000     3]
# Input dtype: <class 'numpy.float32'>
# Output dtype: <class 'numpy.float32'>
```

### Retrain Model

If you need to retrain the model with updated dataset:

```bash
cd ~/Sentient-Core-v4/coral_training

# Generate new dataset
~/.pyenv/versions/coral-py39/bin/python generate_complete_dataset.py

# Train model
~/.pyenv/versions/coral-py39/bin/python train_enhanced_model.py

# Compile for Edge TPU
edgetpu_compiler models/sentient_viz_enhanced.tflite

# Deploy
cp models/sentient_viz_enhanced_edgetpu.tflite ../models/
```

---

## Configuration Files

### Main Configuration

Located in `config/sentient_config.json`:

```json
{
  "coral_tpu": {
    "model_path": "models/sentient_viz_enhanced_edgetpu.tflite",
    "target_fps": 60,
    "fallback_to_cpu": true
  },
  "flipper_zero": {
    "serial_port": "/dev/flipper",
    "baud_rate": 115200,
    "timeout": 1.0,
    "enabled": true
  },
  "arduino": {
    "serial_port": "/dev/arduino_mega",
    "baud_rate": 115200,
    "timeout": 2.0,
    "enabled": true
  },
  "websocket": {
    "host": "localhost",
    "port": 8765,
    "max_connections": 10
  },
  "visualization": {
    "particle_count": 10000,
    "update_rate_hz": 60
  }
}
```

### Environment Variables

Create `.env` file in project root:

```bash
# Coral TPU
CORAL_MODEL_PATH=models/sentient_viz_enhanced_edgetpu.tflite
CORAL_TARGET_FPS=60

# Serial Devices
FLIPPER_PORT=/dev/flipper
ARDUINO_PORT=/dev/arduino_mega

# WebSocket
WS_HOST=localhost
WS_PORT=8765

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/sentient_core.log
```

---

## Next Steps

After configuring all peripherals:

1. **[Testing Guide](./TESTING_GUIDE.md)** - Verify everything works
2. **[Production Deployment](./PRODUCTION_DEPLOYMENT.md)** - Set up systemd services
3. **Launch Sentient Core**: `./launch_enhanced.sh --no-voice-input --no-voice-output`
