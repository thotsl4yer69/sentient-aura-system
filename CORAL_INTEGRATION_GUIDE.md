# Coral TPU Integration Guide
## Quick Start for Sentient Core v4

**Status:** Architecture complete, implementation ready for deployment
**Date:** 2025-10-24

---

## Prerequisites

### Hardware
- ✅ Raspberry Pi 500+ (ARM64)
- ✅ Google Coral USB Accelerator
- ✅ USB 3.0 port (recommended for bandwidth)

### Software
- ✅ Raspberry Pi OS (Debian-based)
- ✅ Python 3.11+
- ✅ TensorFlow Lite model (generated from training)

---

## Installation Steps

### 1. Install Coral TPU Runtime

```bash
# Add Coral repository
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | \
  sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

# Add GPG key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

# Update and install
sudo apt-get update
sudo apt-get install -y libedgetpu1-std python3-pycoral
```

### 2. Install Python Dependencies

```bash
cd /home/mz1312/Sentient-Core-v4

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install tflite-runtime numpy psutil
```

### 3. Verify Coral Device

```bash
# Check USB connection
lsusb | grep "Google"
# Expected output: Bus 001 Device 004: ID 1a6e:089a Global Unichip Corp.

# Test Coral detection
python3 -c "from pycoral.utils import edgetpu; print(edgetpu.list_edge_tpus())"
# Expected output: [{'type': 'usb', 'path': '/dev/bus/usb/001/004'}]
```

### 4. Deploy Trained Model

```bash
# After training is complete, copy compiled model
cp coral_training/models/sentient_viz_edgetpu.tflite models/
```

### 5. Update Configuration

Edit `sentient_aura/config.py` and add at the end:

```python
# ============================================================================
# CORAL TPU CONFIGURATION
# ============================================================================

CORAL_ENABLED = True
CORAL_MODEL_PATH = os.path.join(PROJECT_ROOT, "models/sentient_viz_edgetpu.tflite")
CORAL_TARGET_FPS = 60
CORAL_FALLBACK_MODE = 'llm'  # 'llm' or 'static'
CORAL_ENABLE_METRICS = True
CORAL_INTERPOLATION_ALPHA = 0.3  # EMA smoothing (0-1)

# Performance tuning
CORAL_CPU_AFFINITY = [2]  # Pin to core 2
CORAL_FEATURE_CACHE_TTL = 0.1  # 100ms cache for psutil
CORAL_WARMUP_FRAMES = 5

# Monitoring
CORAL_LOG_SLOW_FRAMES = True
CORAL_SLOW_FRAME_THRESHOLD_MS = 20.0
CORAL_METRICS_REPORT_INTERVAL = 5.0  # seconds
```

### 6. Integrate into Main System

Edit `sentient_aura_main.py`:

```python
# Add import at top
from coral_visualization_daemon import CoralVisualizationDaemon
import sentient_aura.config as config

# In SentientAuraSystem.__init__(), add:
self.coral_daemon = None

# In SentientAuraSystem.initialize(), add after WebSocket server:
if config.CORAL_ENABLED:
    logger.info("Initializing Coral visualization daemon...")
    self.coral_daemon = CoralVisualizationDaemon(
        world_state=self.world_state,
        websocket_server=self.websocket_server,
        config={
            'target_fps': config.CORAL_TARGET_FPS,
            'model_path': config.CORAL_MODEL_PATH,
            'fallback_mode': config.CORAL_FALLBACK_MODE,
            'enable_metrics': config.CORAL_ENABLE_METRICS,
            'interpolation_alpha': config.CORAL_INTERPOLATION_ALPHA
        }
    )
    logger.info("✓ Coral daemon initialized")

# In SentientAuraSystem.start(), add after daemon startup:
if self.coral_daemon:
    self.coral_daemon.start()
    logger.info("✓ Coral daemon started")
    time.sleep(0.5)  # Let it initialize

# In SentientAuraSystem.shutdown(), add before daemon shutdown:
if self.coral_daemon:
    logger.info("Stopping Coral daemon...")
    self.coral_daemon.stop()
    self.coral_daemon.join(timeout=3)
```

### 7. Add WorldState Snapshot Method

Edit `world_state.py` and add this method to the `WorldState` class:

```python
def get_snapshot(self) -> dict:
    """
    Get immutable snapshot of current world state.

    Returns:
        dict: Deep copy of state (thread-safe)
    """
    with self._lock:
        return copy.deepcopy(self._state)
```

Add import at top if not already present:
```python
import copy
```

---

## Testing

### Unit Tests

```bash
# Run all tests
python3 tests/test_coral_daemon.py

# Run specific test
python3 tests/test_coral_daemon.py TestFeatureExtractor.test_feature_range

# Run with verbose output
python3 tests/test_coral_daemon.py -v
```

### Performance Benchmarks

```bash
# Run performance benchmarks
python3 tests/test_coral_daemon.py --benchmark

# Expected output:
# Feature Extraction: <2ms average
# Particle Interpolation: <1ms average
```

### Manual Testing

```bash
# Test feature extraction standalone
python3 coral_visualization_daemon.py

# Expected output:
# INFO - Testing feature extraction...
# INFO - Extracted 68 features
# INFO - Feature range: [0.000, 1.000]
# INFO - Health status: {...}
```

### Integration Test

```bash
# Start full system with Coral enabled
python3 sentient_aura_main.py

# Watch logs for:
# INFO - Initializing Coral visualization daemon...
# INFO - Loading Coral TPU model: /home/mz1312/Sentient-Core-v4/models/sentient_viz_edgetpu.tflite
# INFO - Found 1 Coral TPU device(s)
# INFO - Warming up Coral TPU...
# INFO - ✓ Coral TPU warmup complete (XXms)
# INFO - ✓ Coral daemon initialized
# INFO - ✓ Coral daemon started
# INFO - CORAL VISUALIZATION DAEMON ACTIVE
# INFO - Target FPS: 60
```

---

## Monitoring

### Performance Metrics

Coral daemon reports metrics every 5 seconds:

```
INFO - Coral Metrics: FPS=59.8, Frame=13.2ms, Inference=4.1ms, Frames=1234
```

**Key Metrics:**
- **FPS:** Should be ≥55 (target: 60)
- **Frame:** Total frame time, should be <16ms
- **Inference:** Coral TPU inference time, should be <5ms
- **Frames:** Total frames processed

### Health Check

```python
# Get health status (can add to API endpoint)
health = daemon.health_check()
print(health)

# Output:
{
    'status': 'healthy',
    'checks': {
        'coral_device': {'status': 'pass', 'devices': 1},
        'model_file': {'status': 'pass'},
        'performance': {'status': 'pass', 'fps': 59.8, 'target_fps': 60},
        'websocket': {'status': 'pass', 'clients': 1}
    },
    'metrics': {
        'fps': 59.8,
        'avg_frame_ms': 13.2,
        'avg_inference_ms': 4.1,
        'total_frames': 1234
    }
}
```

### Troubleshooting

#### Coral Device Not Found

```bash
# Check USB connection
lsusb | grep "Google"

# Check kernel modules
lsmod | grep apex

# Reconnect device
# Unplug and replug Coral USB Accelerator

# Check permissions
ls -l /dev/bus/usb/001/004
# Should be readable by user or add to plugdev group
```

#### Low FPS Performance

**Possible causes:**
1. **Heavy feature extraction:** Check which features are slow
2. **CPU throttling:** Check temperature with `vcgencmd measure_temp`
3. **Other processes:** Check CPU usage with `htop`
4. **USB bandwidth:** Use USB 3.0 port if available

**Solutions:**
```python
# Reduce target FPS
config.CORAL_TARGET_FPS = 30

# Increase cache TTL for heavy operations
config.CORAL_FEATURE_CACHE_TTL = 0.2  # 200ms

# Disable CPU-intensive features temporarily
# (modify FeatureExtractor to skip psutil calls)
```

#### Model File Issues

```bash
# Verify model exists
ls -lh /home/mz1312/Sentient-Core-v4/models/sentient_viz_edgetpu.tflite

# Check model is Edge TPU compiled (not regular TFLite)
file models/sentient_viz_edgetpu.tflite
# Should contain "edgetpu" in filename

# Verify model architecture
python3 -c "
import tflite_runtime.interpreter as tflite
interpreter = tflite.Interpreter('models/sentient_viz_edgetpu.tflite')
interpreter.allocate_tensors()
print('Input:', interpreter.get_input_details())
print('Output:', interpreter.get_output_details())
"
```

#### Fallback to LLM Mode

If Coral initialization fails, daemon automatically falls back to LLM mode:

```
WARNING - Coral TPU unavailable: [error details]
WARNING - Falling back to LLM mode
INFO - CoralVisualizationDaemon in fallback mode - exiting
```

This is expected behavior. The existing `SentientCore` will continue providing visualizations via LLM.

---

## Advanced Configuration

### CPU Core Pinning

For maximum performance, pin Coral daemon to dedicated CPU core:

```python
# In coral_visualization_daemon.py, add to run() method:
import os
os.sched_setaffinity(0, {2})  # Pin to core 2
```

### Binary WebSocket Protocol

For reduced bandwidth (7.3 MB/s instead of 10.8 MB/s), implement binary protocol:

```python
# In _broadcast_particles(), replace JSON with binary:
particles_binary = particles.tobytes()
self.websocket_server.broadcast_binary(particles_binary)

# Frontend (sentient_core.html):
ws.binaryType = 'arraybuffer';
ws.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    const particles = new Float32Array(event.data);
    updateParticles(particles);
  }
};
```

### Custom Interpolation

Adjust smoothing factor based on use case:

```python
# More responsive (less smooth)
config.CORAL_INTERPOLATION_ALPHA = 0.5

# More smooth (less responsive)
config.CORAL_INTERPOLATION_ALPHA = 0.1

# No interpolation
config.CORAL_INTERPOLATION_ALPHA = 1.0
```

---

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/sentient-core.service`:

```ini
[Unit]
Description=Sentient Core AI Companion with Coral TPU
After=network.target

[Service]
Type=simple
User=mz1312
WorkingDirectory=/home/mz1312/Sentient-Core-v4
ExecStart=/home/mz1312/Sentient-Core-v4/venv/bin/python3 sentient_aura_main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryLimit=2G
CPUQuota=300%

# Environment
Environment="CORAL_ENABLED=1"
Environment="CORAL_TARGET_FPS=60"

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable sentient-core
sudo systemctl start sentient-core
sudo systemctl status sentient-core
```

View logs:
```bash
sudo journalctl -u sentient-core -f
```

### Performance Tuning

For 24/7 production operation:

```python
# config.py adjustments for stability

# Slightly lower FPS for reliability
CORAL_TARGET_FPS = 55

# Longer cache for system metrics
CORAL_FEATURE_CACHE_TTL = 0.2

# More aggressive smoothing for stability
CORAL_INTERPOLATION_ALPHA = 0.25

# Enable all monitoring
CORAL_ENABLE_METRICS = True
CORAL_LOG_SLOW_FRAMES = True
```

---

## Maintenance

### Daily Checks

```bash
# Check Coral daemon status
sudo systemctl status sentient-core | grep "Coral"

# Check performance metrics
sudo journalctl -u sentient-core | grep "Coral Metrics" | tail -5

# Check for errors
sudo journalctl -u sentient-core | grep "ERROR" | tail -10
```

### Weekly Maintenance

```bash
# Restart service to clear any memory leaks
sudo systemctl restart sentient-core

# Check disk usage (logs)
du -sh /home/mz1312/Sentient-Core-v4/logs/

# Rotate logs if needed
find /home/mz1312/Sentient-Core-v4/logs/ -name "*.log" -mtime +7 -delete
```

### Model Updates

When retraining model:

```bash
# Stop service
sudo systemctl stop sentient-core

# Backup old model
cp models/sentient_viz_edgetpu.tflite models/sentient_viz_edgetpu.tflite.backup

# Deploy new model
cp coral_training/models/sentient_viz_edgetpu.tflite models/

# Restart service
sudo systemctl start sentient-core

# Monitor startup
sudo journalctl -u sentient-core -f
```

---

## Next Steps

1. ✅ Architecture designed (CORAL_TPU_ARCHITECTURE.md)
2. ✅ Implementation complete (coral_visualization_daemon.py)
3. ✅ Tests written (tests/test_coral_daemon.py)
4. ⏳ **Complete dataset generation** (14/20 done)
5. ⏳ **Train model** (coral_training/train_model.py)
6. ⏳ **Compile for Edge TPU** (Google Colab)
7. ⏳ **Deploy and test** (this guide)
8. ⏳ **Production deployment** (systemd service)

---

## Support & Resources

**Documentation:**
- Full architecture: `/home/mz1312/Sentient-Core-v4/CORAL_TPU_ARCHITECTURE.md`
- Training guide: `/home/mz1312/Sentient-Core-v4/coral_training/README.md`
- Feature design: `/home/mz1312/Sentient-Core-v4/coral_training/RICH_FEATURE_DESIGN.md`

**Key Files:**
- Daemon: `/home/mz1312/Sentient-Core-v4/coral_visualization_daemon.py`
- Tests: `/home/mz1312/Sentient-Core-v4/tests/test_coral_daemon.py`
- Config: `/home/mz1312/Sentient-Core-v4/sentient_aura/config.py`

**Coral Resources:**
- Official docs: https://coral.ai/docs/
- Model compilation: https://coral.ai/docs/edgetpu/compiler/
- TFLite guide: https://www.tensorflow.org/lite

---

**Status:** Ready for deployment once training is complete.
