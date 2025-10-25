# Quick Start: Enhanced 120-Feature Sentient Core

## 🚀 Launch System

```bash
cd /home/mz1312/Sentient-Core-v4
./launch_enhanced.sh --no-voice-input --no-voice-output
```

## 🔌 Hardware Setup (When Ready to Test)

### 1. Coral USB Accelerator
✅ Already connected - Auto-detected at startup

### 2. Flipper Zero (with E07 Sub-GHz Module)
```bash
# Connect to any available USB port (not /dev/ttyACM0 if Arduino is active)
# System will auto-detect on startup
```

### 3. Arduino (Optional - currently conflicts with Flipper)
```bash
# If needed, disconnect Flipper first
# Arduino uses /dev/ttyACM0
```

### 4. Camera (Future)
```bash
# USB camera or Pi Camera
# System will auto-detect when connected
```

## 📊 Check System Status

```bash
# View running system
ps aux | grep sentient_aura_main.py

# Check Coral TPU detection
~/.pyenv/versions/coral-py39/bin/python -c "from pycoral.utils import edgetpu; print(edgetpu.list_edge_tpus())"

# View logs (if needed)
tail -f /tmp/aura.heartbeat
```

## 🛑 Stop System

```bash
# Ctrl+C in the terminal, or:
pkill -f "sentient_aura_main.py"
```

## 📈 Performance Metrics

- **Expected Warmup:** ~35ms
- **Expected Inference:** ~1-2ms per frame
- **Target FPS:** 60
- **Actual Capability:** 877 FPS

## 🎯 GUI Access

```
file:///home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html
```

## ✅ System Health Check

Should see in logs:
```
✓ Enhanced 120-feature model loaded
✓ Coral TPU warmup complete
CORAL VISUALIZATION DAEMON ACTIVE
Target FPS: 60
```

## 🔧 Troubleshooting

**System won't start:**
```bash
# Check Python environment
~/.pyenv/versions/coral-py39/bin/python --version  # Should be 3.9.18

# Check model exists
ls -lh models/sentient_viz_enhanced_edgetpu.tflite  # Should be ~4.0M
```

**Coral TPU not detected:**
```bash
lsusb | grep -i "Google\|Global Unichip"  # Should show USB device
```

**Feature extraction errors:**
- Normal if no environmental sensors connected
- System handles gracefully with default values

## 📝 Next Testing Steps

When peripherals reconnected:
1. **Flipper Zero:** Sub-GHz signal detection and visualization
2. **WiFi Scanner:** Network mapping and visualization
3. **Bluetooth Scanner:** Device detection and proximity
4. **Camera:** People/face detection and tracking

## 🎨 What to Expect

With Flipper connected:
- Orange particles = Sub-GHz signals (433MHz, 315MHz, etc.)
- Particle density increases with signal strength
- Companion "focuses" attention toward signal sources

## ⚡ Performance Tips

For best performance:
- Close unnecessary applications
- Use USB 3.0 port for Coral if available
- Monitor temperature: `vcgencmd measure_temp`
- Check CPU usage: `htop`

---

**Status:** System operational and stable
**Ready for:** Peripheral integration and real-world testing
**Documentation:** SESSION_SUMMARY_120_FEATURE_INTEGRATION.md

**Quick Launch:** `./launch_enhanced.sh --no-voice-input --no-voice-output`
