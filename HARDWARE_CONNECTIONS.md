# Hardware Connections Guide

Complete wiring and connection guide for all Enhanced Sentient Core peripherals.

## Table of Contents
- [Overview](#overview)
- [Google Coral USB Accelerator](#google-coral-usb-accelerator)
- [Flipper Zero](#flipper-zero)
- [Arduino with Sensors](#arduino-with-sensors)
- [Wiring Diagrams](#wiring-diagrams)
- [USB Port Layout](#usb-port-layout)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Enhanced Sentient Core uses multiple USB peripherals for multi-sensor fusion:

| Device | Connection | Purpose |
|--------|------------|---------|
| Google Coral TPU | USB 3.0 | AI inference (877 FPS capable) |
| Flipper Zero | USB-C to USB-A | Sub-GHz, NFC, IR, GPIO scanning |
| Arduino Mega/Uno | USB-B to USB-A | Environmental sensors |

**IMPORTANT**: All devices connect via USB. No GPIO pins on the Pi are used.

---

## Google Coral USB Accelerator

### Physical Connection

1. **Unpack Coral USB Accelerator**
   - Remove from anti-static packaging
   - Do NOT touch the gold connector pins

2. **Connect to Pi 5**
   - Use a **USB 3.0 port** (blue port on Pi 5)
   - Plug directly into Pi (no USB hubs)
   - Ensure firm connection

3. **Verify Detection**
   ```bash
   lsusb | grep "18d1:9302"
   # Should output: Bus XXX Device XXX: ID 18d1:9302 Google Inc.
   ```

### Thermal Considerations

The Coral TPU gets warm during continuous inference (normal behavior):
- Operating temperature: Up to 85°C
- Ensure good airflow around the device
- Do not block ventilation holes

### Common Issues

**Coral Not Detected**:
```bash
# Check USB devices
lsusb

# Check dmesg for errors
dmesg | grep -i "18d1:9302"

# Try different USB 3.0 port
# Ensure using USB 3.0 (blue port)
```

**Performance Issues**:
```bash
# Check USB speed
lsusb -t
# Should show "5000M" for USB 3.0

# If showing "480M", device is in USB 2.0 mode
# Replug into USB 3.0 port
```

---

## Flipper Zero

### Physical Connection

1. **Prepare Flipper Zero**
   - Ensure Flipper is powered on
   - Firmware: Official or Unleashed (both supported)
   - No special apps need to be running

2. **Connect to Pi 5**
   - Use USB-C to USB-A cable (included with Flipper)
   - Connect to any available USB port
   - Flipper screen should show "Connected to PC"

3. **Verify Detection**
   ```bash
   # Check serial devices
   ls -la /dev/ttyACM*
   # Should show: /dev/ttyACM0 or /dev/ttyACM1

   # Check device info
   udevadm info -a /dev/ttyACM0 | grep -i flipper
   ```

### Flipper Zero Capabilities

The Enhanced Sentient Core uses Flipper for:

- **Sub-GHz Radio** (300-928 MHz):
  - Remote controls
  - Garage door openers
  - Wireless sensors
  - LoRa devices

- **125kHz RFID**:
  - Access cards
  - Key fobs

- **NFC** (13.56 MHz):
  - Credit cards (read only)
  - Access badges
  - NFC tags

- **Infrared**:
  - TV remotes
  - AC controls
  - Universal remote codes

- **GPIO**:
  - External sensors
  - Custom hardware

### Configuration

```bash
# Check which serial port Flipper is using
ls -la /dev/ttyACM*

# If multiple devices, identify by vendor ID
udevadm info /dev/ttyACM0 | grep ID_VENDOR_ID
# Flipper: 0483 (STMicroelectronics)
```

### Common Issues

**Flipper Not Detected**:
```bash
# Ensure Flipper is powered on
# Check USB connection is secure

# Verify kernel recognizes device
dmesg | tail -20
# Should show: "cdc_acm" driver loaded

# Check permissions
ls -la /dev/ttyACM0
# Should show: crw-rw---- 1 root dialout

# Add user to dialout group if needed
sudo usermod -a -G dialout $USER
# Then log out and back in
```

**Serial Port Conflicts**:
```bash
# If both Arduino and Flipper connected:
# Flipper usually: /dev/ttyACM0
# Arduino usually: /dev/ttyACM1

# Create udev rules to assign fixed names
# See PERIPHERAL_CONFIGURATION.md
```

---

## Arduino with Sensors

### Recommended Arduino Board

- **Arduino Mega 2560** (preferred) - More pins for sensors
- **Arduino Uno** (alternative) - Fewer pins but adequate

### Sensor Connections

#### Pin Assignments (Arduino Mega 2560)

| Sensor | Arduino Pin | Type | Purpose |
|--------|-------------|------|---------|
| DHT11/22 | Pin 2 | Digital | Temperature & Humidity |
| HC-SR04 Trigger | Pin 9 | Digital | Ultrasonic distance |
| HC-SR04 Echo | Pin 10 | Digital | Ultrasonic distance |
| PIR Motion | Pin 24 | Digital | Motion detection |
| Microphone | Pin A3 (57) | Analog | Sound level |
| Status LED | Pin 13 | Digital | Visual feedback |
| LED Matrix (optional) | Pin 14 | Digital | Display |

#### Arduino Uno Pin Assignments

| Sensor | Arduino Pin | Type | Purpose |
|--------|-------------|------|---------|
| DHT11/22 | Pin 2 | Digital | Temperature & Humidity |
| HC-SR04 Trigger | Pin 9 | Digital | Ultrasonic distance |
| HC-SR04 Echo | Pin 10 | Digital | Ultrasonic distance |
| PIR Motion | Pin 7 | Digital | Motion detection |
| Microphone | Pin A3 | Analog | Sound level |
| Status LED | Pin 13 | Digital | Visual feedback |

### Wiring Instructions

#### DHT11/DHT22 Temperature & Humidity Sensor

```
DHT Sensor:
├── Pin 1 (VCC)   → Arduino 5V
├── Pin 2 (DATA)  → Arduino Pin 2 (with 10kΩ pullup to 5V)
├── Pin 3 (NC)    → Not connected
└── Pin 4 (GND)   → Arduino GND

Pullup Resistor:
10kΩ resistor between DATA pin and VCC
```

#### HC-SR04 Ultrasonic Distance Sensor

```
HC-SR04:
├── VCC    → Arduino 5V
├── TRIG   → Arduino Pin 9
├── ECHO   → Arduino Pin 10
└── GND    → Arduino GND

Note: Some sensors require 3.3V for ECHO (use voltage divider)
```

#### PIR Motion Sensor

```
PIR Sensor (HC-SR501):
├── VCC    → Arduino 5V
├── OUT    → Arduino Pin 24 (Mega) or Pin 7 (Uno)
└── GND    → Arduino GND

Adjust sensitivity and time delay using onboard potentiometers
```

#### Microphone Module (Analog)

```
Microphone Module:
├── VCC    → Arduino 5V
├── GND    → Arduino GND
└── OUT    → Arduino Pin A3

Common modules: MAX4466, LM393
```

#### Status LED

```
LED:
├── Anode (+)   → Arduino Pin 13
└── Cathode (-) → GND (through 220Ω resistor)

Note: Pin 13 has built-in resistor on most Arduinos
```

### USB Connection

```bash
# Connect Arduino to Pi via USB-B cable
# Verify detection
ls -la /dev/ttyACM*
# Should show /dev/ttyACM0 or /dev/ttyACM1

# Check Arduino info
udevadm info /dev/ttyACM1 | grep ID_VENDOR_ID
# Arduino: 2341 (Arduino) or 1a86 (CH340 clone)
```

### Power Considerations

**Powering Arduino:**
- USB power from Pi is usually sufficient
- If using many sensors, consider external 5V power supply
- Never exceed 5V on sensor inputs

**Power Budget:**
- Arduino Mega: ~50mA
- DHT sensor: ~2.5mA
- HC-SR04: ~15mA (during ping)
- PIR sensor: ~50mA
- Microphone: ~5mA
- **Total**: ~125mA (well within USB limits)

---

## Wiring Diagrams

### Complete System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 5                            │
│                                                               │
│  USB 3.0 (Blue)         USB 2.0          USB 2.0             │
│       │                   │                 │                │
│       │                   │                 │                │
└───────┼───────────────────┼─────────────────┼────────────────┘
        │                   │                 │
        │                   │                 │
        ▼                   ▼                 ▼
┌──────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Coral USB    │  │ Flipper Zero    │  │ Arduino Mega    │
│ Accelerator  │  │                 │  │ 2560            │
│              │  │ (USB-C cable)   │  │                 │
│ Edge TPU     │  │                 │  │ (USB-B cable)   │
└──────────────┘  └─────────────────┘  └────────┬────────┘
                                                 │
                                    ┌────────────┴────────────┐
                                    │                         │
                                    ▼                         ▼
                            ┌──────────────┐        ┌──────────────┐
                            │ DHT Sensor   │        │  HC-SR04     │
                            │ (Pin 2)      │        │  (Pin 9/10)  │
                            └──────────────┘        └──────────────┘
                                    │                         │
                                    ▼                         ▼
                            ┌──────────────┐        ┌──────────────┐
                            │ PIR Sensor   │        │  Microphone  │
                            │ (Pin 24)     │        │  (Pin A3)    │
                            └──────────────┘        └──────────────┘
```

### Breadboard Layout (Arduino Sensors)

```
        5V   GND  Pin2  Pin9  Pin10  Pin24  A3   Pin13
         │    │     │     │     │      │     │     │
         │    │     │     │     │      │     │     │
    ┌────┴────┴─────┴─────┴─────┴──────┴─────┴─────┴────┐
    │                                                     │
    │           Arduino Mega 2560                         │
    │                                                     │
    └─────────────────────────────────────────────────────┘
         │    │     │     │     │      │     │     │
         │    │     │     │     │      │     │     │
         │    │     │     │     │      │     │     ▼
         │    │     │     │     │      │     │   ┌───┐
         │    │     │     │     │      │     │   │LED│ Status
         │    │     │     │     │      │     │   └───┘
         │    │     │     │     │      │     │
         │    │     │     │     │      │     ▼
         │    │     │     │     │      │   ┌──────┐
         │    │     │     │     │      │   │ Mic  │
         │    │     │     │     │      │   └──────┘
         │    │     │     │     │      │
         │    │     │     │     │      ▼
         │    │     │     │     │   ┌──────┐
         │    │     │     │     │   │ PIR  │
         │    │     │     │     │   └──────┘
         │    │     │     │     │
         │    │     │     ▼     ▼
         │    │     │   ┌──────────┐
         │    │     │   │ HC-SR04  │
         │    │     │   │ Trigger→Echo
         │    │     │   └──────────┘
         │    │     │
         │    │     ▼
         │    │   ┌──────┐
         │    │   │ DHT  │
         │    │   │  +   │
         │    │   │ 10kΩ │ (pullup)
         │    │   └──────┘
         │    │      │
         ▼    ▼      ▼
       Power Rail (5V & GND)
```

---

## USB Port Layout

### Raspberry Pi 5 USB Ports

```
┌─────────────────────────────────────────┐
│                                         │
│  ┌──┐ ┌──┐          ┌──┐ ┌──┐         │
│  │U3│ │U3│          │U2│ │U2│         │  ← Top View
│  └──┘ └──┘          └──┘ └──┘         │
│  Blue  Blue         Black Black       │
│                                         │
│         Raspberry Pi 5                  │
└─────────────────────────────────────────┘

U3 = USB 3.0 (5 Gbps) - Use for Coral TPU
U2 = USB 2.0 (480 Mbps) - Use for Arduino/Flipper
```

### Recommended Port Assignment

```
Left Side (USB 3.0):
├── Port 1: Google Coral USB Accelerator ← Highest priority
└── Port 2: (Available for expansion)

Right Side (USB 2.0):
├── Port 3: Flipper Zero
└── Port 4: Arduino Mega 2560
```

---

## Troubleshooting

### Multiple Serial Devices (/dev/ttyACM0 conflict)

```bash
# List all serial devices with details
ls -la /dev/ttyACM*

# Identify each device
for dev in /dev/ttyACM*; do
    echo "=== $dev ==="
    udevadm info $dev | grep -E "ID_VENDOR_ID|ID_MODEL"
done

# Create persistent names (see PERIPHERAL_CONFIGURATION.md)
```

### Permission Denied Errors

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, then verify
groups | grep dialout

# Alternatively, change device permissions (temporary)
sudo chmod 666 /dev/ttyACM0
```

### Device Not Detected

```bash
# Check physical connection
lsusb

# Check kernel messages
dmesg | tail -30

# Check USB power
vcgencmd get_throttled
# 0x0 = Good, non-zero = power issue

# Try different USB port
# Ensure cable is data-capable (not charge-only)
```

### Intermittent Disconnects

```bash
# Disable USB autosuspend
echo 'SUBSYSTEM=="usb", TEST=="power/control", ATTR{power/control}="on"' | \
    sudo tee /etc/udev/rules.d/50-usb-power.rules

# Reload rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reboot
sudo reboot
```

---

## Next Steps

After connecting all hardware, proceed to:
1. **[Install Dependencies](./INSTALL_DEPENDENCIES.md)** - Install required software
2. **[Peripheral Configuration](./PERIPHERAL_CONFIGURATION.md)** - Configure each device
3. **[Testing Guide](./TESTING_GUIDE.md)** - Verify everything works
