# Dependency Installation Guide

Automated installation script for all Enhanced Sentient Core dependencies on Raspberry Pi 5.

## Table of Contents
- [Quick Install](#quick-install)
- [Manual Installation](#manual-installation)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Quick Install

### One-Command Installation

```bash
cd /home/mz1312/Sentient-Core-v4
chmod +x install_dependencies.sh
./install_dependencies.sh
```

This will install:
- Python 3.9 via pyenv (required for Coral compatibility)
- Google Coral Edge TPU libraries
- All Python dependencies
- System packages
- udev rules for hardware devices

**Estimated Time**: 15-20 minutes

---

## Manual Installation

If you prefer step-by-step installation:

### 1. System Packages

```bash
# Update package lists
sudo apt update

# Install essential build tools
sudo apt install -y \
    build-essential \
    git \
    curl \
    wget \
    libffi-dev \
    libssl-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    liblzma-dev \
    python3-dev

# Install USB and serial tools
sudo apt install -y \
    usbutils \
    i2c-tools \
    python3-serial \
    screen \
    minicom

# Install audio dependencies (for voice features)
sudo apt install -y \
    portaudio19-dev \
    python3-pyaudio \
    espeak
```

### 2. Install pyenv (Python Version Manager)

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to shell configuration
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell
exec $SHELL
```

### 3. Install Python 3.9

```bash
# Install Python 3.9.18 (required for Coral TPU compatibility)
pyenv install 3.9.18

# Create coral-py39 environment
pyenv virtualenv 3.9.18 coral-py39

# Verify installation
~/.pyenv/versions/coral-py39/bin/python --version
# Should output: Python 3.9.18
```

### 4. Install Google Coral Edge TPU Runtime

```bash
# Add Google Coral repository
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
    sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

# Add Google's package signing key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    sudo apt-key add -

# Update and install Edge TPU runtime
sudo apt update
sudo apt install -y libedgetpu1-std

# Install pycoral
~/.pyenv/versions/coral-py39/bin/pip install \
    --extra-index-url https://google-coral.github.io/py-repo/ \
    pycoral
```

### 5. Install Python Dependencies

```bash
cd /home/mz1312/Sentient-Core-v4

# Install all Python packages
~/.pyenv/versions/coral-py39/bin/pip install \
    numpy \
    opencv-python \
    pillow \
    pyserial \
    websockets \
    aiohttp \
    psutil \
    scikit-learn \
    tflite-runtime \
    requests
```

### 6. Install Optional Dependencies

```bash
# Voice input (optional)
~/.pyenv/versions/coral-py39/bin/pip install vosk

# Voice output (optional)
~/.pyenv/versions/coral-py39/bin/pip install piper-tts

# Environment management (optional)
~/.pyenv/versions/coral-py39/bin/pip install python-dotenv

# Monitoring (recommended for production)
~/.pyenv/versions/coral-py39/bin/pip install prometheus-client
```

### 7. Configure udev Rules

```bash
# Create udev rules for Coral TPU
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="1a6e", GROUP="plugdev"' | \
    sudo tee /etc/udev/rules.d/99-edgetpu-accelerator.rules

echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="18d1", ATTRS{idProduct}=="9302", GROUP="plugdev"' | \
    sudo tee -a /etc/udev/rules.d/99-edgetpu-accelerator.rules

# Create udev rules for serial devices (Flipper + Arduino)
sudo tee /etc/udev/rules.d/99-sentient-serial.rules << 'EOF'
# Flipper Zero
SUBSYSTEM=="tty", ATTRS{idVendor}=="0483", ATTRS{idProduct}=="5740", SYMLINK+="flipper", GROUP="dialout", MODE="0666"

# Arduino Mega
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0042", SYMLINK+="arduino_mega", GROUP="dialout", MODE="0666"

# Arduino Uno (CH340)
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="arduino_uno", GROUP="dialout", MODE="0666"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to required groups
sudo usermod -a -G plugdev $USER
sudo usermod -a -G dialout $USER
sudo usermod -a -G i2c $USER
```

### 8. Disable USB Autosuspend

```bash
# Prevent USB devices from auto-suspending
echo 'SUBSYSTEM=="usb", TEST=="power/control", ATTR{power/control}="on"' | \
    sudo tee /etc/udev/rules.d/50-usb-power.rules

sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## Verification

### Verify Python Installation

```bash
# Check Python version
~/.pyenv/versions/coral-py39/bin/python --version
# Expected: Python 3.9.18

# Check pycoral
~/.pyenv/versions/coral-py39/bin/python -c "import pycoral; print('pycoral OK')"
# Expected: pycoral OK

# Check numpy
~/.pyenv/versions/coral-py39/bin/python -c "import numpy; print('numpy OK')"
# Expected: numpy OK

# Check websockets
~/.pyenv/versions/coral-py39/bin/python -c "import websockets; print('websockets OK')"
# Expected: websockets OK
```

### Verify Coral TPU

```bash
# Plug in Coral USB Accelerator

# Check USB detection
lsusb | grep "18d1:9302"
# Expected: Bus XXX Device XXX: ID 18d1:9302 Google Inc.

# Test Edge TPU
cd /home/mz1312/Sentient-Core-v4
~/.pyenv/versions/coral-py39/bin/python << 'EOF'
from pycoral.utils import edgetpu

devices = edgetpu.list_edge_tpus()
if devices:
    print(f"✓ Found {len(devices)} Coral TPU device(s)")
    for i, dev in enumerate(devices):
        print(f"  Device {i}: {dev['type']} at {dev['path']}")
else:
    print("✗ No Coral TPU devices found")
EOF
```

### Verify Serial Devices

```bash
# With Flipper Zero and Arduino connected

# Check serial devices
ls -la /dev/ttyACM* /dev/flipper /dev/arduino_*

# Expected output:
# /dev/ttyACM0 -> Flipper Zero
# /dev/ttyACM1 -> Arduino
# /dev/flipper -> symlink to Flipper
# /dev/arduino_mega or /dev/arduino_uno -> symlink to Arduino

# Test Flipper Zero
screen /dev/flipper 115200
# Press Ctrl+A, K to exit

# Test Arduino
screen /dev/arduino_mega 115200
# Press Ctrl+A, K to exit
```

### Verify Group Membership

```bash
# Check user groups
groups | grep -E "plugdev|dialout|i2c"

# Expected output should include:
# plugdev dialout i2c

# If missing, log out and back in
```

---

## Troubleshooting

### Python Installation Issues

**pyenv install fails**:
```bash
# Install additional dependencies
sudo apt install -y \
    liblzma-dev \
    tk-dev \
    libffi-dev

# Retry installation
pyenv install 3.9.18
```

**pycoral import fails**:
```bash
# Verify correct Python version
~/.pyenv/versions/coral-py39/bin/python --version

# Reinstall pycoral
~/.pyenv/versions/coral-py39/bin/pip uninstall pycoral
~/.pyenv/versions/coral-py39/bin/pip install \
    --extra-index-url https://google-coral.github.io/py-repo/ \
    pycoral
```

### Coral TPU Issues

**Device not detected**:
```bash
# Check USB connection
lsusb

# Check dmesg for errors
dmesg | grep -i "18d1:9302"

# Verify udev rules
cat /etc/udev/rules.d/99-edgetpu-accelerator.rules

# Reload udev
sudo udevadm control --reload-rules
sudo udevadm trigger

# Replug Coral TPU
```

**Permission denied**:
```bash
# Add to plugdev group
sudo usermod -a -G plugdev $USER

# Log out and back in
exit

# Reconnect via SSH
ssh pi@sentient-core.local
```

### Serial Device Issues

**No /dev/ttyACM devices**:
```bash
# Check if devices are connected
lsusb

# Check dmesg
dmesg | tail -30

# Verify cdc_acm driver is loaded
lsmod | grep cdc_acm
```

**Permission denied on serial ports**:
```bash
# Add to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in
```

**Multiple ttyACM devices, can't identify which is which**:
```bash
# Use udev info to identify
for dev in /dev/ttyACM*; do
    echo "=== $dev ==="
    udevadm info $dev | grep -E "ID_VENDOR_ID|ID_MODEL|ID_SERIAL"
done

# Flipper: ID_VENDOR_ID=0483
# Arduino: ID_VENDOR_ID=2341 or 1a86
```

---

## Next Steps

After successful installation:

1. **[Hardware Connections](./HARDWARE_CONNECTIONS.md)** - Connect all peripherals
2. **[Peripheral Configuration](./PERIPHERAL_CONFIGURATION.md)** - Configure devices
3. **[Testing Guide](./TESTING_GUIDE.md)** - Verify system functionality
4. **[Production Deployment](./PRODUCTION_DEPLOYMENT.md)** - Set up systemd services
