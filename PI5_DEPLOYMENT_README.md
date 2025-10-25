# Enhanced Sentient Core - Raspberry Pi 5 Deployment Guide

Complete deployment documentation for the **Enhanced Sentient Core** - a 120-feature multi-sensor AI fusion system running on Raspberry Pi 5 with Google Coral Edge TPU.

## 🚀 Quick Start (30 Minutes)

For experienced users who want to get running quickly:

```bash
# 1. Flash Pi 5 with Raspberry Pi OS (64-bit)
# 2. SSH into Pi
# 3. Clone repository
git clone <repo-url> ~/Sentient-Core-v4
cd ~/Sentient-Core-v4

# 4. Run automated installation
chmod +x install_dependencies.sh
./install_dependencies.sh

# 5. Connect hardware (Coral TPU, Flipper Zero, Arduino)
# 6. Test system
./launch_enhanced.sh --no-voice-input --no-voice-output

# 7. Deploy as service
sudo cp systemd/sentient-core.service /etc/systemd/system/
sudo systemctl enable sentient-core.service
sudo systemctl start sentient-core.service
```

---

## 📚 Complete Deployment Path

For a fresh Raspberry Pi 5 setup, follow this complete path:

### Step 1: Initial Pi 5 Setup
**Time**: ~30 minutes
**Document**: [RASPBERRY_PI_5_SETUP.md](./RASPBERRY_PI_5_SETUP.md)

- Flash Raspberry Pi OS (64-bit)
- Configure SSH, WiFi, hostname
- Enable I2C, Serial interfaces
- Optimize for AI workloads

### Step 2: Install Dependencies
**Time**: ~15-20 minutes
**Document**: [INSTALL_DEPENDENCIES.md](./INSTALL_DEPENDENCIES.md)

- Python 3.9 via pyenv
- Google Coral Edge TPU runtime
- All Python packages
- udev rules for hardware

**Quick Install**:
```bash
cd ~/Sentient-Core-v4
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Step 3: Connect Hardware
**Time**: ~30 minutes
**Document**: [HARDWARE_CONNECTIONS.md](./HARDWARE_CONNECTIONS.md)

- Google Coral USB Accelerator → USB 3.0 port
- Flipper Zero → USB port
- Arduino with sensors → USB port

**Wiring diagrams included** for all sensors.

### Step 4: Configure Peripherals
**Time**: ~20 minutes
**Document**: [PERIPHERAL_CONFIGURATION.md](./PERIPHERAL_CONFIGURATION.md)

- Verify Coral TPU detection
- Configure Flipper Zero serial communication
- Upload Arduino sketch
- Set up persistent device names

### Step 5: Testing & Verification
**Time**: ~15 minutes
**Document**: [TESTING_GUIDE.md](./TESTING_GUIDE.md)

- 10 comprehensive tests
- Hardware verification
- Performance benchmarks
- Integration tests

**Run all tests**:
```bash
cd ~/Sentient-Core-v4
python3 scripts/run_all_tests.py
```

### Step 6: Production Deployment
**Time**: ~10 minutes
**Document**: [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)

- systemd service setup
- Auto-start on boot
- Monitoring & logging
- Backup configuration

**Deploy**:
```bash
sudo systemctl enable sentient-core.service
sudo systemctl start sentient-core.service
```

---

## 🔧 System Architecture

### Hardware Stack
```
┌─────────────────────────────────────────┐
│        Raspberry Pi 5 (ARM64)            │
│  ┌────────┐  ┌──────────┐  ┌──────────┐ │
│  │Coral   │  │Flipper   │  │Arduino   │ │
│  │USB TPU │  │Zero      │  │+ Sensors │ │
│  └────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────┘
```

### Software Stack
- **OS**: Raspberry Pi OS (64-bit) Bookworm
- **Python**: 3.9.18 (pyenv coral-py39)
- **AI Runtime**: TensorFlow Lite + pycoral
- **Model**: 120-feature Edge TPU compiled (.tflite)
- **WebSocket**: Real-time visualization server
- **Service**: systemd for production deployment

### Performance
- **Inference Speed**: 2-3ms per frame on Coral TPU
- **Target FPS**: 60 (visualization)
- **Actual FPS**: 35-42 (WebSocket bottleneck)
- **Theoretical Max**: 877 FPS (Coral capability)

---

## 📦 What's Included

### Documentation
- ✅ Pi 5 initial setup guide
- ✅ Automated dependency installation
- ✅ Hardware wiring diagrams
- ✅ Peripheral configuration
- ✅ Comprehensive testing suite
- ✅ Production deployment guide

### Hardware Support
- ✅ Google Coral USB Accelerator
- ✅ Flipper Zero (Sub-GHz, NFC, IR, GPIO)
- ✅ Arduino Mega/Uno with sensors:
  - DHT11/DHT22 (temperature & humidity)
  - HC-SR04 (ultrasonic distance)
  - PIR (motion detection)
  - Microphone (sound level)

### Features
- ✅ 120-feature multi-sensor fusion
- ✅ Real-time Edge TPU inference
- ✅ WebSocket visualization (10,000 particles)
- ✅ Graceful error recovery
- ✅ systemd auto-start
- ✅ Health monitoring
- ✅ Log rotation
- ✅ Automated backups

---

## ⚠️ Known Issues & Fixes

### Issue 1: WebSocket Performance Bottleneck
**Status**: Identified, fix pending
**Impact**: FPS limited to 35-42 instead of 60
**Cause**: JSON serialization of 10,000 particles (500KB+)

**Planned Fix**: Binary protocol
```python
# Replace JSON with binary
particles_buffer = particles_3d.astype(np.float32).tobytes()  # 120KB
```

**Priority**: Medium (system functional, optimization needed)

### Issue 2: Serial Port Conflicts
**Status**: Documented, workaround available
**Impact**: Flipper/Arduino may conflict on /dev/ttyACM*
**Workaround**: udev rules create persistent /dev/flipper and /dev/arduino_mega symlinks

**Planned Fix**: Serial port mutex (complete port locking)

### Issue 3: No Authentication on WebSocket
**Status**: Open, production-critical
**Impact**: WebSocket endpoint is open to all clients
**Planned Fix**: JWT authentication + TLS/SSL

---

## 🎯 Deployment Checklist

Use this checklist when deploying on a new Pi 5:

### Hardware Setup
- [ ] Raspberry Pi 5 (4GB+ RAM)
- [ ] Google Coral USB Accelerator
- [ ] Flipper Zero (optional but recommended)
- [ ] Arduino Mega/Uno with sensors (optional)
- [ ] USB cables (USB-A, USB-C to USB-A, USB-B)
- [ ] Power supply (27W official Pi 5 PSU)
- [ ] Active cooling (fan recommended)

### Software Installation
- [ ] Pi OS (64-bit) flashed to SD card
- [ ] SSH enabled
- [ ] Dependencies installed (`install_dependencies.sh`)
- [ ] User added to groups (plugdev, dialout, i2c)
- [ ] Logged out and back in (for group changes)

### Hardware Configuration
- [ ] Coral TPU detected (`lsusb | grep 18d1:9302`)
- [ ] Flipper Zero connected (`ls /dev/flipper`)
- [ ] Arduino connected (`ls /dev/arduino_mega`)
- [ ] udev rules loaded
- [ ] USB autosuspend disabled

### Testing
- [ ] Coral TPU loads model successfully
- [ ] Inference runs < 5ms per frame
- [ ] Flipper Zero responds to commands
- [ ] Arduino peripherals discovered
- [ ] WebSocket server accepts connections
- [ ] All dependencies import correctly

### Production Deployment
- [ ] systemd service created
- [ ] Service enabled for auto-start
- [ ] Service survives reboot
- [ ] Logs rotating properly
- [ ] Health checks configured
- [ ] Monitoring dashboard accessible
- [ ] Backup script scheduled

---

## 📊 System Requirements

### Minimum
- Raspberry Pi 5 (4GB RAM)
- 32GB microSD card
- Google Coral USB Accelerator
- 5V/3A+ power supply

### Recommended
- Raspberry Pi 5 (8GB RAM)
- 64GB+ microSD card (or SSD)
- Google Coral USB Accelerator
- 27W official Pi 5 PSU
- Active cooling (fan case)
- Flipper Zero
- Arduino Mega 2560 with sensors

### Network
- Ethernet or WiFi
- Static IP recommended for production
- Open port 8765 for WebSocket (or use firewall)

---

## 🔍 Troubleshooting

### Quick Diagnostics

```bash
# Check service status
systemctl status sentient-core.service

# View logs
sudo journalctl -u sentient-core.service -n 50

# Health check
~/Sentient-Core-v4/scripts/health_check.sh

# Monitor in real-time
~/Sentient-Core-v4/scripts/monitor.sh
```

### Common Issues

**Service won't start**:
```bash
# Check logs
sudo journalctl -xe -u sentient-core.service

# Verify Python environment
~/.pyenv/versions/coral-py39/bin/python --version

# Check permissions
ls -la ~/Sentient-Core-v4/launch_enhanced.sh
```

**Coral TPU not detected**:
```bash
# Replug into USB 3.0 port (blue)
# Reload udev rules
sudo udevadm trigger

# Check permissions
groups | grep plugdev
```

**High CPU usage** (should be low with Coral TPU):
```bash
# Check if using CPU fallback
sudo journalctl -u sentient-core.service | grep fallback

# Verify Coral is being used
sudo journalctl -u sentient-core.service | grep "Coral TPU"
```

See individual guide documents for detailed troubleshooting.

---

## 🚦 Production Readiness Status

### ✅ Production Ready
- Coral TPU inference (2-3ms per frame)
- Hardware auto-detection
- systemd service
- Health monitoring
- Log rotation
- Graceful error recovery
- Auto-restart on failure

### ⚠️ Requires Optimization
- WebSocket binary protocol (currently JSON)
- Connection pooling & rate limiting
- Authentication & TLS encryption
- Performance monitoring dashboard
- Serial port mutex

### 📋 Roadmap
- [ ] Binary WebSocket protocol
- [ ] JWT authentication
- [ ] Prometheus metrics exporter
- [ ] WebRTC data channels (lower latency)
- [ ] Multi-process architecture
- [ ] GPU acceleration for particle rendering

---

## 📞 Support

### Documentation
- [Raspberry Pi 5 Setup](./RASPBERRY_PI_5_SETUP.md)
- [Install Dependencies](./INSTALL_DEPENDENCIES.md)
- [Hardware Connections](./HARDWARE_CONNECTIONS.md)
- [Peripheral Configuration](./PERIPHERAL_CONFIGURATION.md)
- [Testing Guide](./TESTING_GUIDE.md)
- [Production Deployment](./PRODUCTION_DEPLOYMENT.md)

### Logs & Diagnostics
```bash
# System logs
sudo journalctl -u sentient-core.service -f

# Application logs
tail -f ~/Sentient-Core-v4/logs/sentient_core.log

# Health check
~/Sentient-Core-v4/scripts/health_check.sh
```

---

## 🎉 You're Ready!

Your Enhanced Sentient Core deployment documentation is complete!

**Deployment Time**: ~2-3 hours for complete setup
**Difficulty**: Intermediate (basic Linux knowledge required)

**Access your system**:
- WebSocket: `ws://<pi-ip>:8765`
- Visualization: Open `sentient_aura/sentient_core.html` in browser
- Logs: `sudo journalctl -u sentient-core.service -f`

**Next steps**:
1. Follow [RASPBERRY_PI_5_SETUP.md](./RASPBERRY_PI_5_SETUP.md) to start
2. Complete all setup steps in order
3. Run tests to verify functionality
4. Deploy as production service
5. Monitor and enjoy your sentient AI system! 🤖

---

**Version**: 1.0.0
**Last Updated**: 2025-10-25
**Tested On**: Raspberry Pi 5 (8GB), Pi OS Bookworm (64-bit)
