# Rich Feature Set Design for Coral TPU Training

## Philosophy

The AI's visual representation should be an **honest window into its cognitive and sensory state**, not just environmental sensors. Every active sensor and processing stream contributes to the particle visualization.

## Complete Feature Set (50-60 dimensions)

### 1. COGNITIVE STATE (8 features)
What the AI is thinking/doing:

- `cognitive_state`: idle=0, listening=0.2, processing=0.4, speaking=0.6, executing=0.8, reasoning=1.0
- `reasoning_depth`: shallow (0.0) to deep philosophical (1.0)
- `uncertainty_level`: confident (0.0) to highly uncertain (1.0)
- `cognitive_load`: idle (0.0) to maximum processing (1.0)
- `creativity_mode`: routine (0.0) to highly creative/inspired (1.0)
- `attention_focus`: diffuse/monitoring (0.0) to laser-focused (1.0)
- `learning_active`: not learning (0.0) to actively learning/adapting (1.0)
- `memory_access_depth`: recent (0.0) to deep historical (1.0)

### 2. ENVIRONMENTAL SENSORS (10 features)
Physical environment awareness:

- `temperature`: normalized 0-40°C → 0-1
- `humidity`: 0-100% → 0-1
- `atmospheric_pressure`: normalized 900-1100 hPa → 0-1
- `light_level`: dark (0.0) to bright (1.0)
- `ambient_sound_level`: quiet (0.0) to loud (1.0)
- `motion_detected`: boolean 0/1
- `motion_intensity`: if detected, how much (0-1)
- `proximity_human`: no one (0.0) to person very close (1.0)
- `air_quality`: clean (0.0) to poor (1.0) [if available]
- `time_of_day`: normalized 0-24h → 0-1 (circadian rhythm)

### 3. RF SPECTRUM ANALYSIS (12 features)
Radio frequency environmental map:

- `rf_scanner_active`: boolean 0/1
- `rf_433mhz_activity`: signal strength 0-1 (garage doors, sensors)
- `rf_915mhz_activity`: signal strength 0-1 (industrial, medical)
- `rf_2_4ghz_activity`: signal strength 0-1 (WiFi, Bluetooth, ZigBee)
- `rf_5ghz_activity`: signal strength 0-1 (WiFi AC/AX)
- `rf_spectrum_density`: sparse (0.0) to crowded (1.0)
- `rf_known_devices`: count normalized 0-1
- `rf_unknown_signals`: count normalized 0-1
- `rf_signal_diversity`: single type (0.0) to many types (1.0)
- `rf_jamming_detected`: clean (0.0) to jamming present (1.0)
- `rf_protocol_wifi`: activity 0-1
- `rf_protocol_bluetooth`: activity 0-1

### 4. VISUAL PROCESSING (10 features)
Camera/vision system state:

- `vision_active`: boolean 0/1
- `scene_complexity`: simple (0.0) to complex (1.0)
- `objects_detected`: normalized count 0-10 → 0-1
- `faces_detected`: count 0-5 → 0-1
- `dominant_color_hue`: 0-360° → 0-1 (scene color)
- `scene_brightness`: dark (0.0) to bright (1.0)
- `motion_vectors`: scene movement 0-1
- `edge_density`: simple scene (0.0) to high detail (1.0)
- `object_confidence`: low (0.0) to high (1.0) avg detection confidence
- `visual_novelty`: familiar scene (0.0) to novel/unusual (1.0)

### 5. AUDIO PROCESSING (6 features)
Microphone array analysis:

- `audio_active`: boolean 0/1
- `speech_detected`: boolean 0/1
- `speech_clarity`: unclear (0.0) to crystal clear (1.0)
- `audio_frequency_low`: bass energy 0-1
- `audio_frequency_mid`: mid-range energy 0-1
- `audio_frequency_high`: treble energy 0-1

### 6. INTERACTION MODE (7 features)
How AI is engaging:

- `human_interaction`: not interacting (0.0) to active conversation (1.0)
- `personality_mode`: analytical=0.2, friendly=0.4, defensive=0.6, creative=0.8, educational=1.0
- `communication_intent`: inform=0.2, query=0.4, warn=0.6, express=0.8, entertain=1.0
- `empathy_level`: matter-of-fact (0.0) to highly empathetic (1.0)
- `formality_level`: casual (0.0) to formal (1.0)
- `proactivity`: reactive (0.0) to proactive/suggesting (1.0)
- `user_engagement`: user disengaged (0.0) to highly engaged (1.0)

### 7. NETWORK & DATA STREAMS (6 features)
Digital connectivity:

- `network_connected`: boolean 0/1
- `network_activity`: idle (0.0) to high traffic (1.0)
- `external_api_active`: none (0.0) to multiple APIs querying (1.0)
- `database_activity`: idle (0.0) to heavy queries (1.0)
- `websocket_connections`: count normalized 0-1
- `data_streaming`: no streams (0.0) to multiple active streams (1.0)

### 8. SYSTEM RESOURCES (4 features)
Hardware state awareness:

- `cpu_usage`: 0-100% → 0-1
- `memory_usage`: 0-100% → 0-1
- `gpu_usage`: 0-100% → 0-1 (if Coral TPU active)
- `thermal_state`: cool (0.0) to thermal throttling (1.0)

### 9. SECURITY & THREAT AWARENESS (5 features)
Defensive posture:

- `threat_level`: none (0.0) to critical (1.0)
- `anomaly_detected`: normal (0.0) to anomalies present (1.0)
- `defensive_mode`: passive (0.0) to active defense (1.0)
- `sensor_tampering`: clean (0.0) to potential tampering (1.0)
- `intrusion_attempts`: none (0.0) to active attempts (1.0)

## Total: ~68 features

## Output (unchanged):
- 10,000 particles × 3D coordinates (x, y, z) = 30,000 values

## Example Scenarios

### Scenario 1: "Quiet idle monitoring"
```
cognitive_state: 0.0 (idle)
temperature: 0.73, humidity: 0.45
rf_2_4ghz_activity: 0.3 (normal WiFi)
vision_active: 0
network_connected: 1
threat_level: 0.0
→ Calm, symmetrical sphere with gentle pulse
```

### Scenario 2: "Analyzing unknown RF signal with high uncertainty"
```
cognitive_state: 0.4 (processing)
reasoning_depth: 0.8 (deep analysis)
uncertainty_level: 0.9 (very uncertain)
rf_unknown_signals: 0.7 (several unknowns)
rf_jamming_detected: 0.4 (possible interference)
threat_level: 0.5 (elevated)
→ Asymmetric formation with probing tendrils, pulsing uncertainty
```

### Scenario 3: "Friendly conversation with human"
```
cognitive_state: 0.6 (speaking)
human_interaction: 0.9 (active conversation)
personality_mode: 0.4 (friendly)
faces_detected: 0.2 (1 face)
speech_clarity: 0.8 (clear audio)
empathy_level: 0.7 (empathetic)
→ Open, welcoming formation facing toward human
```

### Scenario 4: "Creative problem-solving with visual + RF analysis"
```
cognitive_state: 1.0 (deep reasoning)
creativity_mode: 0.9 (highly creative)
vision_active: 1, scene_complexity: 0.8
rf_scanner_active: 1, rf_spectrum_density: 0.6
cognitive_load: 0.85 (high)
→ Complex, dynamic formation with multiple processing centers
```

### Scenario 5: "Building rich environmental model from all sensors"
```
cognitive_state: 0.4 (processing)
attention_focus: 0.3 (monitoring multiple streams)
vision: active, scene_complexity: 0.6, objects: 5
rf_2_4ghz: 0.7, rf_5ghz: 0.4, known_devices: 8
audio: active, speech_detected: 0, ambient: 0.3
temperature: 22°C, humidity: 48%, motion: 1
network_activity: 0.5, websocket_connections: 3
→ Multi-layered formation showing sensor fusion,
   with dedicated zones for each active sense
```

## Implementation Notes

1. **Feature Normalization**: All features 0-1 for consistent neural network input
2. **Sparse Features**: Many features will be 0 when inactive (e.g., vision_active=0 means all visual features are 0)
3. **Feature Grouping**: Model can learn relationships between related features
4. **Temporal Context**: Could extend to include "delta" features (rate of change) in future versions
5. **LLM Prompts**: Must describe ALL active features to LLM for visualization generation

## Next Steps

1. Review and approve this feature set
2. Update dataset generator to use rich features
3. Generate diverse scenarios covering feature combinations
4. Train model to learn feature→visualization mappings
5. Real-time inference uses actual sensor/cognitive state
