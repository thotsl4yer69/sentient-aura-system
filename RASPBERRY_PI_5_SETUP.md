# Raspberry Pi 5 Setup Guide for Enhanced Sentient Core

Complete setup guide for deploying the Enhanced Sentient Core with 120-feature multi-sensor fusion on a fresh Raspberry Pi 5.

## Table of Contents
- [Hardware Requirements](#hardware-requirements)
- [Initial Pi 5 Setup](#initial-pi-5-setup)
- [System Configuration](#system-configuration)
- [Quick Start](#quick-start)

---

## Hardware Requirements

### Required Hardware
- **Raspberry Pi 5** (4GB or 8GB RAM recommended)
- **Google Coral USB Accelerator** - For Edge TPU inference
- **MicroSD Card** - 64GB+ recommended
- **Power Supply** - Official Pi 5 27W USB-C power supply
- **Case with Cooling** - Active cooling recommended for sustained AI workloads

### Peripheral Hardware (Optional but Recommended)
- **Flipper Zero** - For Sub-GHz, NFC, IR, GPIO scanning
- **Arduino Mega 2560** or **Arduino Uno** - For environmental sensors
- **Sensors** (if using Arduino):
  - DHT11/DHT22 Temperature & Humidity sensor
  - HC-SR04 Ultrasonic distance sensor
  - PIR Motion sensor
  - Microphone/sound level sensor
  - LED indicators (optional)

### Connectivity
- Ethernet cable or WiFi
- USB-A ports for Coral TPU, Flipper Zero, Arduino
- HDMI cable for initial setup (optional if using SSH)

---

## Initial Pi 5 Setup

### 1. Flash Raspberry Pi OS

**Recommended OS**: Raspberry Pi OS (64-bit) Bookworm or later

Using Raspberry Pi Imager:
```bash
# On your computer, download Raspberry Pi Imager
# https://www.raspberrypi.com/software/

# Flash to SD card:
# - OS: Raspberry Pi OS (64-bit)
# - Enable SSH
# - Set username/password
# - Configure WiFi (optional)
```

**SSH Configuration** (if enabling during flash):
- Enable SSH
- Set username: `pi` (or your preference)
- Set strong password
- Configure WiFi if not using Ethernet

### 2. First Boot

```bash
# SSH into your Pi (if headless)
ssh pi@raspberrypi.local
# OR
ssh pi@<IP_ADDRESS>

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    screen \
    build-essential \
    usbutils \
    i2c-tools
```

### 3. Enable Required Interfaces

```bash
# Run raspi-config
sudo raspi-config

# Enable:
# - Interface Options > SSH (if not already enabled)
# - Interface Options > I2C
# - Interface Options > Serial Port (Hardware: Yes, Login Shell: No)

# Reboot to apply changes
sudo reboot
```

### 4. Verify Pi 5 Specifications

```bash
# Check system info
cat /proc/cpuinfo | grep -i "model name"
# Should show: BCM2712 (Pi 5 processor)

# Check memory
free -h

# Check USB devices (should be empty for now)
lsusb

# Check disk space
df -h
```

---

## System Configuration

### 1. Increase Swap Size (Recommended for 4GB models)

```bash
# Edit swap configuration
sudo nano /etc/dphys-swapfile

# Change CONF_SWAPSIZE to 2048 (or 4096)
CONF_SWAPSIZE=2048

# Restart swap service
sudo /etc/init.d/dphys-swapfile restart

# Verify
free -h
```

### 2. Set Static IP (Optional but Recommended)

```bash
# Edit dhcpcd configuration
sudo nano /etc/dhcpcd.conf

# Add at the end (adjust to your network):
interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=192.168.1.1 8.8.8.8

# Restart networking
sudo systemctl restart dhcpcd
```

### 3. Configure Hostname

```bash
# Set friendly hostname
sudo hostnamectl set-hostname sentient-core

# Edit hosts file
sudo nano /etc/hosts

# Change:
127.0.1.1       raspberrypi
# To:
127.0.1.1       sentient-core

# Reboot
sudo reboot
```

---

## Quick Start

Once the basic Pi setup is complete, proceed to:

1. **[Install Dependencies](./INSTALL_DEPENDENCIES.md)** - Automated installation of all required software
2. **[Hardware Connections](./HARDWARE_CONNECTIONS.md)** - Connect Flipper Zero, Arduino, and sensors
3. **[Peripheral Configuration](./PERIPHERAL_CONFIGURATION.md)** - Configure each peripheral device
4. **[Testing Guide](./TESTING_GUIDE.md)** - Verify everything works

---

## Performance Optimization for Pi 5

### CPU Frequency Scaling

```bash
# Install cpufrequtils
sudo apt install -y cpufrequtils

# Set performance governor
sudo cpufreq-set -g performance

# Make permanent by editing /etc/default/cpufrequtils
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
```

### Cooling Considerations

The Enhanced Sentient Core runs continuous AI inference on the Coral TPU and performs real-time sensor processing. Ensure adequate cooling:

- **Active Cooling**: Recommended (fan case)
- **Monitor Temperature**: `vcgencmd measure_temp`
- **Thermal Throttling**: Avoid exceeding 80°C

```bash
# Monitor temperature
watch -n 1 vcgencmd measure_temp

# Check for throttling
vcgencmd get_throttled
# 0x0 = No throttling (good!)
# Non-zero = Throttling detected
```

### USB Power Management

```bash
# Disable USB autosuspend (prevents Coral TPU/Arduino disconnects)
echo 'SUBSYSTEM=="usb", TEST=="power/control", ATTR{power/control}="on"' | \
    sudo tee /etc/udev/rules.d/50-usb-power.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

## Troubleshooting

### Pi 5 Won't Boot
- Verify power supply is official 27W USB-C
- Check SD card is properly inserted
- Re-flash SD card if corrupted

### No Network Connectivity
- Check Ethernet cable or WiFi credentials
- Verify router DHCP is enabled
- Try setting static IP

### USB Devices Not Detected
- Run `lsusb` to check connected devices
- Check USB power management settings
- Try different USB ports
- Ensure adequate power supply

### System Running Slow
- Check CPU temperature: `vcgencmd measure_temp`
- Monitor system load: `htop`
- Increase swap size
- Close unnecessary processes

---

## Next Steps

Proceed to [INSTALL_DEPENDENCIES.md](./INSTALL_DEPENDENCIES.md) to install all required software packages.
