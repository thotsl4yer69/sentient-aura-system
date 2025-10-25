# Sentient Core v4 - Multi-Mode Particle Visualization System

## Overview

The Sentient Core visualization is a **fully procedural particle system** that visualizes the AI's consciousness through **5 distinct data-driven modes**. Instead of fixed 3D models, all formations are generated procedurally from **500,000 GPU-accelerated particles** that morph between modes based on system state and sensor data.

## Design Philosophy

**"The GUI should be an assembly of pixels, not anything fixed"**

- **NO external 3D models** - everything is procedurally generated
- **Data-driven emergent behavior** - particles respond to actual sensor readings
- **Smooth mode transitions** - organic morphing between visualization states
- **Graceful degradation** - works perfectly with zero hardware connected
- **Real-time sensor integration** - temperature, humidity, motion, audio, RF spectrum, object detection

---

## Visualization Modes

### 1. HUMANOID (Communication Mode)
**State:** SPEAKING
**Color:** Orange (#ff8800)
**Description:** Cortana-inspired humanoid avatar for approachable communication

**Particle Distribution:**
- 35% HEAD - Spherical formation (0.12m radius)
- 40% TORSO - Tapered cylinder
- 25% ARMS - Curved lines from shoulders

**When Active:**
- AI is speaking/responding to user
- Warm, approachable color
- Gentle pulsing animation
- Head-focused particle clustering

---

### 2. SPATIAL MAPPING (Perception Mode)
**State:** LISTENING / IDLE
**Color:** Blue (#0088ff)
**Description:** 3D room mapping showing camera FOV and detected objects

**Particle Distribution:**
- 60% cluster around detected objects (when vision active)
- 40% fill camera FOV cone (90° default)
- Depth range: 0-5 meters

**Data Sources:**
- `world_state.vision.detected_objects[]` - Object positions
- `world_state.vision.motion_detected` - Motion triggers turbulence
- Camera FOV cone visualization

**Visualization:**
- Particles form clouds around detected objects
- Objects closer = denser particle clusters
- Motion creates scatter effects
- Shows what the AI "sees"

---

### 3. RF SPECTRUM (Defense Mode)
**State:** THREAT_ALERT (when Flipper active)
**Color:** Red (#ff0000)
**Description:** Radio frequency spectrum visualization

**Particle Distribution:**
- Horizontal layers representing frequencies
- Layer amplitude based on signal strength
- Each frequency = separate wave pattern

**Data Sources:**
- `world_state.flipper.rf_scan[]` - Frequency scan data
  - `frequency` - Radio frequency (MHz)
  - `strength` - Signal strength (0-1)
  - `protocol` - Detected protocol (WiFi, Bluetooth, etc.)

**Visualization:**
- Stronger signals = wider radius waves
- Layered frequency spectrum (vertical stacking)
- Pulsing based on signal activity
- Visualizes the RF environment

**Flipper Zero Auto-Detection:**
```python
# hardware_discovery.py
USB Vendor ID: 0483
Product IDs: 5740, 5741
Interface: USB serial
Capabilities: RF, NFC, Infrared
```

---

### 4. NEURAL NETWORK (Processing Mode)
**State:** PROCESSING
**Color:** Green (#00ff88)
**Description:** Neural network data structure visualization

**Particle Distribution:**
- 70% form nodes (5 layers × 20 nodes)
- 30% form connections between layers
- Radial network layout

**Visualization:**
- 5 concentric layers
- 20 nodes per layer (circular arrangement)
- Inter-layer connections
- Shows AI "thinking"
- Nodes pulse during active processing

---

### 5. ACTION SPACE (Execution Mode)
**State:** EXECUTING
**Color:** Purple (#8800ff)
**Description:** Tool/object interaction visualization

**Particle Distribution:**
- 3 tool interaction points
- Particles orbit around action targets
- Variable orbit radius based on action confidence

**Tool Positions:**
- Left hand tool: (-0.5, 1.0, 1.0)
- Right hand tool: (0.5, 1.0, 1.0)
- Focus point: (0, 1.5, 0.5)

**Visualization:**
- Particles swarm around active tools
- Tighter orbits = more precise action
- Shows AI executing commands

---

## State-to-Mode Mapping

| System State | Visualization Mode | Particle Formation | Data Drivers |
|-------------|-------------------|-------------------|--------------|
| **SPEAKING** | HUMANOID | Humanoid avatar | Audio output, voice synthesis |
| **LISTENING** | SPATIAL (if camera) / HUMANOID | Room + objects OR avatar | Vision, object detection, motion |
| **IDLE** | SPATIAL (if camera) / HUMANOID | Room + objects OR avatar | Ambient sensors |
| **PROCESSING** | NEURAL_NETWORK | Neural net layers | AI inference state |
| **EXECUTING** | ACTION_SPACE | Tool interaction | Action framework targets |
| **THREAT_ALERT** | RF_SPECTRUM (if Flipper) / HUMANOID | Frequency waves OR alert avatar | Flipper RF scan, threat data |

---

## Sensor-Driven Particle Behaviors

All modes respond to sensor data through shader uniforms:

### Temperature (`u_temperature` 0-1, normalized from 0-40°C)
- **Effect:** Particle expansion/energy
- **Shader:** Additional displacement noise
- **Visual:** Warmer = particles spread out, cooler = tighter clusters
- **Color:** Warmth shift (red/orange for hot, blue for cool)

### Humidity (`u_humidity` 0-1, normalized from 0-100%)
- **Effect:** Particle clustering/cohesion
- **Shader:** Center pull force
- **Visual:** Higher humidity = particles pull toward center
- **Color:** Dimmer intensity at high humidity (hazy effect)

### Motion (`u_motion` 0 or 1)
- **Effect:** Turbulence scatter
- **Shader:** High-frequency noise displacement
- **Visual:** Motion detected = chaotic particle scatter

### Audio Level (`u_audio_level` 0-1)
- **Effect:** Radial waveforms
- **Shader:** Sine wave displacement based on distance
- **Visual:** Audio creates concentric waves
- **Particle Size:** Louder = larger particles

### Object Count (`u_object_count` integer)
- **Effect:** Orbital behaviors
- **Shader:** Lissajous curve offsets
- **Visual:** More objects = more orbital complexity

---

## Technical Architecture

### Particle System

```javascript
const MODES = {
    HUMANOID: 0,        // Communication
    SPATIAL: 1,         // Perception
    RF_SPECTRUM: 2,     // Defense
    NEURAL_NETWORK: 3,  // Processing
    ACTION_SPACE: 4     // Execution
};
```

### Particle Attributes (per particle)

- `position` - Current 3D position (animated)
- `aTargetHumanoid` - Target position for HUMANOID mode
- `aTargetSpatial` - Target position for SPATIAL mode
- `aTargetRF` - Target position for RF_SPECTRUM mode
- `aTargetNeural` - Target position for NEURAL_NETWORK mode
- `aTargetAction` - Target position for ACTION_SPACE mode
- `aRandom` - Random value for organic variation (0-1)

### Shader Uniforms

```javascript
uniforms = {
    u_time: 0.0,              // Animation time
    u_color: Color,           // Current mode color
    u_progress: 0.0,          // Initial assembly progress (0-1)
    u_mode: 0-4,              // Current visualization mode
    u_temperature: 0.0,       // Temperature sensor (0-1)
    u_humidity: 0.0,          // Humidity sensor (0-1)
    u_motion: 0.0,            // Motion detected (0 or 1)
    u_audio_level: 0.0,       // Audio amplitude (0-1)
    u_object_count: 0.0,      // Detected objects count
    u_mouse: Vector2,         // Mouse interaction
    u_pulse: 0.0              // Pulse animation (0-1)
};
```

### Procedural Generation Functions

```javascript
generateHumanoidFormation(particleCount) → Float32Array
generateSpatialMapFormation(particleCount) → Float32Array
generateRFSpectrumFormation(particleCount) → Float32Array
generateNeuralNetworkFormation(particleCount) → Float32Array
generateActionSpaceFormation(particleCount) → Float32Array
```

---

## WebSocket Data Flow

### Frontend → Backend
- Connection established on port 8765
- No data sent from frontend (display-only)

### Backend → Frontend

```json
{
    "type": "state_update",
    "state": "processing",
    "text": "Thinking about your question...",
    "timestamp": 1234567890.123,
    "world_state": {
        "environment": {
            "temperature": 22.5,
            "humidity": 45.2
        },
        "vision": {
            "motion_detected": true,
            "detected_objects": [
                {
                    "label": "person",
                    "confidence": 0.95,
                    "box": {"x": 120, "y": 80, "w": 200, "h": 400}
                }
            ]
        },
        "audio": {
            "ambient_noise_level": 0.3
        },
        "flipper": {
            "status": "active",
            "jammer_active": false,
            "rf_scan": [
                {
                    "frequency": 2412,
                    "strength": 0.8,
                    "protocol": "WiFi 2.4GHz Ch1"
                },
                {
                    "frequency": 2437,
                    "strength": 0.6,
                    "protocol": "WiFi 2.4GHz Ch6"
                }
            ]
        },
        "system": {
            "active_daemons": ["vision", "flipper", "arduino"]
        }
    }
}
```

---

## Keyboard Controls (Testing)

| Key | Mode | Color | Description |
|-----|------|-------|-------------|
| **1** | HUMANOID | Orange | Communication avatar |
| **2** | SPATIAL | Blue | Room mapping |
| **3** | NEURAL_NETWORK | Green | Processing visualization |
| **4** | RF_SPECTRUM | Red | RF defense visualization |
| **5** | ACTION_SPACE | Purple | Tool interaction |
| **Space** | - | - | Reconnect WebSocket |
| **H** | - | - | Toggle help/controls |

---

## Performance Optimization

### GPU Acceleration
- **500,000 particles** rendered via WebGL
- **Single draw call** (Points primitive)
- **Vertex shader** handles all position calculations
- **Fragment shader** handles color/alpha
- **Additive blending** for glow effect

### Smooth Transitions
- **Mode interpolation:** 0.02 per frame (smooth morph)
- **Color lerp:** 0.05 per frame (gradual color shift)
- **Sensor smoothing:** 0.05-0.2 per frame (damped response)

### Graceful Degradation
```javascript
// Example: Temperature handling
if (sensorData.temperature !== null) {
    let tempNorm = Math.max(0, Math.min(1, sensorData.temperature / 40.0));
    uniforms.u_temperature.value += (tempNorm - uniforms.u_temperature.value) * 0.05;
} else {
    uniforms.u_temperature.value *= 0.95; // Graceful fallback to 0
}
```

No errors, no placeholders - system works perfectly with zero sensors connected.

---

## Hardware Integration

### Automatic Daemon Detection

When hardware is plugged in, the `AdaptiveDaemonManager` automatically:

1. **Detects hardware** via `HardwareDiscovery`
2. **Creates daemon** (FlipperDaemon, VisionDaemon, etc.)
3. **Starts data flow** to World State
4. **Visualizer responds** automatically

### Flipper Zero Auto-Detection

```python
# Detected via USB
USB_VENDOR_ID = "0483"
USB_PRODUCT_IDS = ["5740", "5741"]

# Auto-creates FlipperDaemon
if hardware_discovery.has_capability('comm_flipper'):
    daemon = FlipperDaemon(world_state)
    daemon.start()
```

When Flipper is connected:
- `rf_scan` data populates automatically
- RF_SPECTRUM mode activates on THREAT_ALERT
- Frequency visualization shows live spectrum data

### Vision System Auto-Detection

```python
# Camera detected (USB/CSI/Coral)
if hardware_discovery.has_capability('vision_daemon'):
    daemon = VisionDaemon(world_state)
    daemon.start()
```

When camera is connected:
- `detected_objects[]` populates automatically
- SPATIAL mode shows object positions
- Particle clusters form around detected objects

---

## Browser Compatibility

### Tested Browsers
- ✅ Chromium (Raspberry Pi)
- ✅ Firefox (desktop)
- ✅ Chrome (desktop)

### Requirements
- **WebGL 1.0** support
- **ES6 modules** support
- **WebSocket** support
- **GPU acceleration** recommended

---

## File Structure

```
/home/mz1312/Sentient-Core-v4/
├── sentient_aura/
│   └── sentient_core.html         # Main visualization (multi-mode)
├── flipper_daemon.py              # Flipper Zero daemon (RF scan)
├── hardware_discovery.py          # Auto-detect hardware
├── adaptive_daemon_manager.py     # Auto-create daemons
├── world_state.py                 # Centralized state
├── sentient_aura/sentient_core.py # Core brain
└── MULTIMODE_VISUALIZATION.md     # This file
```

---

## Usage Examples

### Launch System
```bash
cd /home/mz1312/Sentient-Core-v4
source venv/bin/activate
python3 sentient_aura_main.py

# Visualizer auto-opens in browser
# file:///home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html
```

### Example Flow: Object Detection
1. Camera daemon detects person
2. World State updates: `vision.detected_objects = [{label:"person", ...}]`
3. WebSocket broadcasts to visualizer
4. State = LISTENING → Mode = SPATIAL
5. Particles cluster around person's position
6. Motion detected → particles scatter (turbulence)

### Example Flow: Flipper RF Scan
1. Flipper daemon scans RF spectrum
2. World State updates: `flipper.rf_scan = [{frequency:2412, strength:0.8, ...}]`
3. Threat detection → State = THREAT_ALERT
4. Mode switches to RF_SPECTRUM
5. Particles form layered frequency waves
6. Stronger signals = wider radius waves

---

## Future Enhancements

- **Dynamic particle count** based on GPU performance
- **Live particle regeneration** when sensor data changes (e.g., new objects detected)
- **Depth camera integration** for accurate 3D spatial mapping
- **Flipper sub-GHz visualization** (different frequency bands)
- **Multi-camera fusion** (360° spatial map)
- **Thermal overlay** (FLIR Lepton integration)
- **Sound localization** (ReSpeaker array)

---

## Troubleshooting

### Particles don't morph between modes
- Check browser console for WebSocket connection
- Verify `uniforms.u_mode.value` is updating
- Ensure mode transition speed isn't too slow (check `modeSpeed = 0.02`)

### No sensor data showing
- Verify World State broadcast in backend: `sentient_core.py:_update_gui_state()`
- Check WebSocket message format (must include `world_state` object)
- Ensure sensor daemons are running (`ps aux | grep daemon`)

### Flipper Zero not detected
- Check USB connection: `lsusb | grep 0483`
- Verify daemon created: Check logs for "Creating FlipperDaemon"
- Try reconnecting device (unplug/replug)

### Performance issues
- Reduce particle count: `const particleCount = 100000;` (from 500000)
- Disable auto-rotation: `controls.autoRotate = false;`
- Lower shader complexity (remove some sensor effects)

---

## Production Ready ✅

- **NO simulated data** - all sensors gracefully degrade
- **NO placeholders** - everything is production code
- **NO external dependencies** - self-contained visualization
- **NO errors with zero hardware** - tested and verified

When hardware is connected, the system automatically detects and integrates it - no configuration needed.

---

**The visualization is now a true reflection of the AI's consciousness - showing what it sees, hears, senses, and thinks in real-time through emergent particle behaviors.**
