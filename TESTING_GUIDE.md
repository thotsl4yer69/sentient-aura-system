# Testing and Verification Guide

Complete testing procedures to verify Enhanced Sentient Core functionality on Raspberry Pi 5.

## Table of Contents
- [Pre-Flight Checks](#pre-flight-checks)
- [Hardware Tests](#hardware-tests)
- [Software Tests](#software-tests)
- [Integration Tests](#integration-tests)
- [Performance Tests](#performance-tests)
- [Troubleshooting](#troubleshooting)

---

## Pre-Flight Checks

### System Requirements

```bash
# Verify Pi 5
grep "BCM2712" /proc/cpuinfo || echo "⚠️  Not running on Pi 5"

# Check memory
free -h | grep Mem
# Minimum: 4GB recommended

# Check disk space
df -h /
# Minimum: 10GB free recommended

# Check Python environment
~/.pyenv/versions/coral-py39/bin/python --version
# Expected: Python 3.9.18
```

### Connected Hardware Checklist

```bash
# List USB devices
lsusb

# Expected devices:
# - Google Coral: 18d1:9302
# - Flipper Zero: 0483:5740
# - Arduino: 2341:0042 (Mega) or 1a86:7523 (Uno)

# Check serial devices
ls -la /dev/ttyACM* /dev/flipper /dev/arduino_*

# Expected:
# /dev/ttyACM0 (Flipper)
# /dev/ttyACM1 (Arduino)
# /dev/flipper -> ttyACM0
# /dev/arduino_mega -> ttyACM1
```

---

## Hardware Tests

### Test 1: Coral TPU Detection

```bash
cd ~/Sentient-Core-v4

~/.pyenv/versions/coral-py39/bin/python << 'EOF'
from pycoral.utils import edgetpu

print("=== Coral TPU Detection Test ===")
devices = edgetpu.list_edge_tpus()

if devices:
    print(f"✓ PASS: Found {len(devices)} Coral TPU device(s)")
    for i, dev in enumerate(devices):
        print(f"  Device {i}: {dev}")
else:
    print("✗ FAIL: No Coral TPU devices found")
    print("  Check USB connection and udev rules")
EOF
```

**Expected Output**:
```
=== Coral TPU Detection Test ===
✓ PASS: Found 1 Coral TPU device(s)
  Device 0: {'type': 'usb', 'path': '/sys/bus/usb/devices/2-1'}
```

### Test 2: Coral Model Loading

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import tflite_runtime.interpreter as tflite
from pycoral.utils import edgetpu
import numpy as np

print("=== Coral Model Loading Test ===")

model_path = "models/sentient_viz_enhanced_edgetpu.tflite"

try:
    # Load model with Edge TPU
    interpreter = tflite.Interpreter(
        model_path=model_path,
        experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')]
    )
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"✓ PASS: Model loaded successfully")
    print(f"  Input shape: {input_details[0]['shape']}")
    print(f"  Output shape: {output_details[0]['shape']}")
    print(f"  Input dtype: {input_details[0]['dtype']}")

    # Test inference
    test_input = np.zeros(input_details[0]['shape'], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], test_input)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    print(f"✓ PASS: Test inference successful")
    print(f"  Output shape: {output.shape}")

except Exception as e:
    print(f"✗ FAIL: {e}")
EOF
```

**Expected Output**:
```
=== Coral Model Loading Test ===
✓ PASS: Model loaded successfully
  Input shape: [  1 120]
  Output shape: [    1 10000     3]
  Input dtype: <class 'numpy.float32'>
✓ PASS: Test inference successful
  Output shape: (1, 10000, 3)
```

### Test 3: Flipper Zero Communication

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import serial
import time

print("=== Flipper Zero Communication Test ===")

try:
    # Open serial connection
    ser = serial.Serial('/dev/flipper', 115200, timeout=2)
    time.sleep(0.5)  # Allow connection to stabilize

    # Send status command
    ser.write(b'status\n')
    time.sleep(0.5)

    # Read response
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')

    if response:
        print(f"✓ PASS: Flipper responded")
        print(f"  Response: {response[:100]}")  # First 100 chars
    else:
        print("✗ FAIL: No response from Flipper")

    ser.close()

except serial.SerialException as e:
    print(f"✗ FAIL: Cannot open /dev/flipper")
    print(f"  Error: {e}")
    print("  Check Flipper is connected and powered on")
except Exception as e:
    print(f"✗ FAIL: {e}")
EOF
```

### Test 4: Arduino Communication

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import serial
import time

print("=== Arduino Communication Test ===")

try:
    # Open serial connection
    ser = serial.Serial('/dev/arduino_mega', 115200, timeout=3)
    time.sleep(2)  # Arduino resets on serial connection

    # Clear boot messages
    ser.reset_input_buffer()

    # Send discover command
    ser.write(b'discover\n')
    time.sleep(1)

    # Read response
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')

    if 'PERIPHERAL' in response or 'END_OF_LIST' in response:
        print(f"✓ PASS: Arduino responded to discover command")
        peripherals = [line for line in response.split('\n') if 'PERIPHERAL:' in line]
        print(f"  Found {len(peripherals)} peripheral(s)")
        for p in peripherals[:5]:  # Show first 5
            print(f"  - {p.strip()}")
    else:
        print("✗ FAIL: Unexpected Arduino response")
        print(f"  Response: {response[:200]}")

    ser.close()

except serial.SerialException as e:
    print(f"✗ FAIL: Cannot open /dev/arduino_mega")
    print(f"  Error: {e}")
    print("  Check Arduino is connected and sketch is uploaded")
except Exception as e:
    print(f"✗ FAIL: {e}")
EOF
```

**Expected Output**:
```
=== Arduino Communication Test ===
✓ PASS: Arduino responded to discover command
  Found 6 peripheral(s)
  - PERIPHERAL:dht1:2:sensor
  - PERIPHERAL:ultrasonic1:9:sensor
  - PERIPHERAL:pir1:24:sensor
  - PERIPHERAL:mic1:57:sensor
  - PERIPHERAL:status_led:13:actuator
```

---

## Software Tests

### Test 5: Python Dependencies

```bash
cd ~/Sentient-Core-v4

~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import sys

print("=== Python Dependencies Test ===")

packages = [
    'numpy', 'cv2', 'PIL', 'serial', 'websockets',
    'aiohttp', 'psutil', 'sklearn', 'tflite_runtime', 'pycoral'
]

failed = []
for pkg in packages:
    try:
        if pkg == 'cv2':
            import cv2
        elif pkg == 'PIL':
            from PIL import Image
        elif pkg == 'sklearn':
            import sklearn
        else:
            __import__(pkg)
        print(f"  ✓ {pkg}")
    except ImportError:
        print(f"  ✗ {pkg}")
        failed.append(pkg)

if failed:
    print(f"\n✗ FAIL: Missing packages: {', '.join(failed)}")
else:
    print(f"\n✓ PASS: All required packages installed")
EOF
```

### Test 6: Configuration Loading

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import json
import os

print("=== Configuration Loading Test ===")

config_file = "config/sentient_config.json"

if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)

        print(f"✓ PASS: Configuration loaded")
        print(f"  Coral TPU enabled: {config.get('coral_tpu', {}).get('enabled', False)}")
        print(f"  Flipper enabled: {config.get('flipper_zero', {}).get('enabled', False)}")
        print(f"  Arduino enabled: {config.get('arduino', {}).get('enabled', False)}")
        print(f"  Target FPS: {config.get('coral_tpu', {}).get('target_fps', 'N/A')}")

    except json.JSONDecodeError as e:
        print(f"✗ FAIL: Invalid JSON in {config_file}")
        print(f"  Error: {e}")
else:
    print(f"⚠  WARNING: Config file not found at {config_file}")
    print(f"  Using default configuration")
EOF
```

---

## Integration Tests

### Test 7: Launch Sentient Core (Headless Mode)

```bash
cd ~/Sentient-Core-v4

# Kill any existing instances
pkill -f "sentient_aura_main.py" || true
sleep 2

# Launch in test mode (30 second timeout)
timeout 30 ./launch_enhanced.sh --no-voice-input --no-voice-output 2>&1 | tee /tmp/sentient_test.log &

# Wait for initialization
sleep 15

# Check if running
if pgrep -f "sentient_aura_main.py" > /dev/null; then
    echo "✓ PASS: Sentient Core launched successfully"

    # Check for errors in log
    if grep -i "error\|fail\|exception" /tmp/sentient_test.log | grep -v "WARNING" | grep -v "No module named 'dotenv'" > /dev/null; then
        echo "⚠  WARNING: Errors detected in log"
        grep -i "error\|fail" /tmp/sentient_test.log | head -5
    else
        echo "✓ PASS: No critical errors in log"
    fi

    # Check components
    grep "CORAL VISUALIZATION DAEMON ACTIVE" /tmp/sentient_test.log && echo "  ✓ Coral daemon active"
    grep "SENTIENT AURA IS ALIVE" /tmp/sentient_test.log && echo "  ✓ System alive"

    # Kill test instance
    pkill -f "sentient_aura_main.py"
else
    echo "✗ FAIL: Sentient Core did not launch"
    echo "Check log at /tmp/sentient_test.log"
fi
```

### Test 8: WebSocket Connectivity

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import asyncio
import websockets

print("=== WebSocket Connectivity Test ===")

async def test_websocket():
    uri = "ws://localhost:8765"
    try:
        async with websockets.connect(uri, timeout=5) as websocket:
            print(f"✓ PASS: Connected to WebSocket at {uri}")

            # Try to receive a message
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=3)
                print(f"✓ PASS: Received message ({len(message)} bytes)")
            except asyncio.TimeoutError:
                print(f"⚠  WARNING: No message received within 3 seconds")

    except Exception as e:
        print(f"✗ FAIL: Cannot connect to WebSocket")
        print(f"  Error: {e}")
        print(f"  Ensure Sentient Core is running")

# Run test (requires Sentient Core to be running)
try:
    asyncio.run(test_websocket())
except Exception as e:
    print(f"✗ FAIL: {e}")
EOF
```

---

## Performance Tests

### Test 9: Coral TPU Inference Benchmark

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import tflite_runtime.interpreter as tflite
import numpy as np
import time

print("=== Coral TPU Performance Benchmark ===")

model_path = "models/sentient_viz_enhanced_edgetpu.tflite"

try:
    # Load model
    interpreter = tflite.Interpreter(
        model_path=model_path,
        experimental_delegates=[tflite.load_delegate('libedgetpu.so.1')]
    )
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Prepare test input
    test_input = np.random.random(input_details[0]['shape']).astype(np.float32)

    # Warmup
    for _ in range(10):
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()

    # Benchmark
    iterations = 100
    start_time = time.perf_counter()

    for _ in range(iterations):
        interpreter.set_tensor(input_details[0]['index'], test_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details[0]['index'])

    total_time = time.perf_counter() - start_time
    avg_time_ms = (total_time / iterations) * 1000
    fps = iterations / total_time

    print(f"✓ Benchmark complete")
    print(f"  Iterations: {iterations}")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average inference: {avg_time_ms:.2f}ms")
    print(f"  FPS: {fps:.1f}")

    if avg_time_ms < 5:
        print(f"✓ PASS: Excellent performance (< 5ms per frame)")
    elif avg_time_ms < 20:
        print(f"✓ PASS: Good performance (< 20ms per frame)")
    else:
        print(f"⚠  WARNING: Slow performance ({avg_time_ms:.2f}ms)")

except Exception as e:
    print(f"✗ FAIL: {e}")
EOF
```

**Expected Performance**:
- Average inference: 2-3ms
- FPS: 300-500 (theoretical)
- Status: EXCELLENT

### Test 10: Memory Usage

```bash
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
import psutil
import os

print("=== Memory Usage Test ===")

process = psutil.Process(os.getpid())
mem_info = process.memory_info()
mem_mb = mem_info.rss / 1024 / 1024

print(f"  Python process memory: {mem_mb:.1f} MB")

# System memory
mem = psutil.virtual_memory()
total_gb = mem.total / 1024 / 1024 / 1024
available_gb = mem.available / 1024 / 1024 / 1024
used_percent = mem.percent

print(f"  System memory: {available_gb:.1f}GB / {total_gb:.1f}GB available")
print(f"  Memory usage: {used_percent:.1f}%")

if used_percent < 70:
    print(f"✓ PASS: Healthy memory usage")
elif used_percent < 85:
    print(f"⚠  WARNING: High memory usage")
else:
    print(f"✗ FAIL: Critical memory usage")
EOF
```

---

## Troubleshooting

### Common Issues

**Test fails with "Permission denied"**:
```bash
# Add user to required groups
sudo usermod -a -G plugdev,dialout,i2c $USER
# Log out and back in
```

**Coral TPU not detected**:
```bash
# Check USB connection
lsusb | grep 18d1

# Replug into USB 3.0 port (blue port)

# Check udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

**Serial devices not found**:
```bash
# Check connections
ls -la /dev/ttyACM*

# Check symlinks
ls -la /dev/flipper /dev/arduino_*

# Recreate symlinks
sudo udevadm trigger
```

**Python import errors**:
```bash
# Reinstall dependencies
cd ~/Sentient-Core-v4
~/.pyenv/versions/coral-py39/bin/pip install -r requirements.txt
```

---

## Test Summary Checklist

After completing all tests, verify:

- [ ] Coral TPU detected
- [ ] Coral model loads and runs inference
- [ ] Flipper Zero responds to commands
- [ ] Arduino responds with peripheral list
- [ ] All Python dependencies installed
- [ ] Configuration loads correctly
- [ ] Sentient Core launches without critical errors
- [ ] WebSocket server accepts connections
- [ ] Coral TPU inference < 5ms per frame
- [ ] Memory usage < 70%

If all tests pass, proceed to **[Production Deployment](./PRODUCTION_DEPLOYMENT.md)**

If any tests fail, review the [Troubleshooting](#troubleshooting) section or check specific peripheral guides.
