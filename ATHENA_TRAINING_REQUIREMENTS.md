# ATHENA Training Requirements

**System Name:** ATHENA (Autonomous Tactical Helper with Environmental Network Awareness)
**Date:** 2025-10-26
**Status:** Training Plan - Ready for Implementation
**Hardware:** Pi 5 (16GB) + Hailo-8 (26 TOPS, 8GB) + Coral TPU (4 TOPS) + Orin Nano (40 TOPS, 8GB)
**Total Compute:** 70 TOPS, 32 GB RAM

---

## Executive Summary

ATHENA is a tactical defense companion with autonomous threat detection, offensive capabilities (NFC/RFID hacking), defensive capabilities (RF jamming), and proactive decision-making. This document defines the complete training requirements to achieve production-ready tactical AI.

**Key Capabilities to Train:**
1. Autonomous RF + visual threat detection
2. NFC/RFID protocol recognition and emulation for access bypass
3. WiFi/SubGHz jamming for defensive countermeasures
4. Tactical decision-making with autonomous action triggers
5. Multi-domain sensor fusion (camera, RF, GPS, IMU)
6. Proactive behavior with personality-driven responses

**Training Timeline:** 10 weeks (4 supervised + 2 integration + 4 reinforcement learning)
**Success Criteria:** >95% threat detection, >90% protocol recognition, <500ms response time

---

## 1. Autonomous Threat Detection Training

### 1.1 RF Threat Recognition

**Objective:** Detect drones, surveillance devices, and anomalous RF signatures in 315-928 MHz spectrum.

**Training Dataset Requirements:**

| Category | Examples | Signatures Needed | Source |
|----------|----------|-------------------|--------|
| Drones | DJI Mavic, Phantom, Mini; Parrot Anafi | 5,000 | Flipper SubGHz captures |
| Surveillance | Hidden cameras (2.4/5.8 GHz), RF bugs, GPS trackers | 10,000 | Security research datasets |
| IoT Devices | Smart home (Zigbee 868/915 MHz), LoRa, tire sensors | 20,000 | Normal environment baselines |
| Anomalies | Unexpected signals from objects (light fixtures, outlets) | 5,000 | Synthetic + real captures |
| Jamming Signals | Active jamming attempts, interference patterns | 5,000 | Adversarial dataset |
| Emergency | Police/EMS radios, emergency beacons | 5,000 | Public safety frequencies |

**Total RF Dataset:** 50,000 labeled signatures

**Features to Extract (22 dimensions):**
- Center frequency (MHz)
- Bandwidth (kHz)
- Modulation type (ASK, FSK, GFSK, LoRa, etc.)
- Signal strength (RSSI in dBm)
- Duty cycle (%)
- Temporal pattern (burst interval, duration)
- Frequency hopping behavior
- Protocol fingerprint (preamble, sync word)

**Model Architecture:**
- **Platform:** Google Coral TPU (4 TOPS)
- **Network:** 1D CNN for temporal pattern recognition
- **Input:** 22-dim feature vector + 128-point spectrogram
- **Output:** 15 threat classes + confidence score
- **Inference Time:** <5ms per signature

**Training Approach:**
1. Collect 50K RF captures using Flipper Zero SubGHz module
2. Label signatures: DRONE, SURVEILLANCE, NORMAL, ANOMALY, EMERGENCY, etc.
3. Extract 22 features per signature
4. Train on Coral TPU Edge TPU Compiler
5. Quantize to INT8 for 4 TOPS performance
6. Validate: >95% accuracy on test set

**Threat Classes:**
```python
RF_THREAT_CLASSES = [
    'DRONE_DJI',           # DJI drones (2.4/5.8 GHz, Lightbridge, OcuSync)
    'DRONE_GENERIC',       # Generic quadcopters (2.4 GHz)
    'SURVEILLANCE_CAMERA', # Wireless cameras (2.4/5.8 GHz video)
    'SURVEILLANCE_BUG',    # RF listening devices (UHF/VHF)
    'GPS_TRACKER',         # Asset trackers (cellular, LoRa)
    'SMART_HOME',          # Zigbee, Z-Wave (normal)
    'TIRE_SENSOR',         # 433 MHz TPMS (normal)
    'LORA_DEVICE',         # LoRaWAN sensors (normal)
    'WIFI_DEVICE',         # 2.4/5 GHz WiFi (normal)
    'BT_DEVICE',           # Bluetooth (normal)
    'ANOMALY_LIGHT',       # Unexpected signal from light fixture
    'ANOMALY_OUTLET',      # Unexpected signal from power outlet
    'JAMMING_ACTIVE',      # Active jamming attempt
    'EMERGENCY_RADIO',     # Police/EMS communications
    'UNKNOWN',             # Unrecognized signature
]
```

---

### 1.2 Visual Threat Assessment

**Objective:** Real-time detection of weapons, aggressive behavior, and environmental hazards from camera feed.

**Training Dataset Requirements:**

| Category | Examples | Images Needed | Source |
|----------|----------|---------------|--------|
| Weapons | Handguns, rifles, knives, improvised weapons | 30,000 | COCO, OpenImages, custom |
| Aggressive Behavior | Fighting stance, running, pointing, aggressive gestures | 20,000 | Action recognition datasets |
| Suspicious Objects | Unattended bags, tripwires, concealed devices | 10,000 | Security training datasets |
| Environmental Hazards | Blocked exits, fire, smoke, structural damage | 10,000 | Disaster response datasets |
| Normal Scenarios | Everyday objects, neutral behavior, safe environments | 30,000 | COCO, ImageNet |

**Total Visual Dataset:** 100,000 annotated images

**Model Architecture:**
- **Platform:** Hailo-8 AI HAT (26 TOPS, 8GB DDR4)
- **Network:** YOLOv8-Custom (trained for 80 threat classes)
- **Input:** 640x640 RGB camera frame
- **Output:** Bounding boxes + class + confidence
- **Inference Time:** 30 FPS (33ms per frame)

**Training Approach:**
1. Collect/curate 100K images across 80 threat classes
2. Annotate bounding boxes + labels using LabelImg/CVAT
3. Train YOLOv8 on GPU cluster (4-7 days on A100)
4. Convert to Hailo format using Hailo Dataflow Compiler
5. Deploy to Hailo-8 AI HAT
6. Validate: >95% mAP on test set, <2% false positives

**Threat Classes (80 total, key examples):**
```python
VISUAL_THREAT_CLASSES = [
    # Weapons (15 classes)
    'handgun', 'rifle', 'shotgun', 'knife', 'machete',
    'bat', 'crowbar', 'taser', 'pepper_spray', 'improvised_weapon',

    # Aggressive Behavior (10 classes)
    'fighting_stance', 'running_aggressive', 'pointing_weapon',
    'grab_attack', 'punch', 'kick', 'chase', 'threatening_gesture',

    # Suspicious Objects (15 classes)
    'unattended_bag', 'suspicious_package', 'tripwire',
    'hidden_camera', 'concealed_device', 'wire_exposed',

    # Environmental Hazards (10 classes)
    'blocked_exit', 'fire', 'smoke', 'gas_leak', 'structural_damage',
    'broken_glass', 'wet_floor', 'electrical_hazard',

    # Surveillance Indicators (10 classes)
    'person_watching', 'person_following', 'camera_pointed',
    'binoculars', 'surveillance_van',

    # Normal (safe) (20 classes)
    'person_walking', 'person_sitting', 'phone', 'bag_carried',
    'door_closed', 'window_closed', 'normal_object', ...
]
```

---

### 1.3 Multi-Modal Threat Correlation

**Objective:** Link RF signatures to visual objects, cross-reference GPS + RF for threat triangulation, recognize temporal surveillance patterns.

**Training Dataset Requirements:**

| Scenario | Description | Examples Needed | Modalities |
|----------|-------------|-----------------|------------|
| Drone + Visual | RF signature matches camera-detected drone | 5,000 | SubGHz + Camera |
| Hidden Camera | 2.4/5.8 GHz video signal from visually suspicious object | 3,000 | WiFi scan + Camera |
| GPS Tracker | Cellular/LoRa signal from vehicle undercarriage | 2,000 | SubGHz + GPS + Camera |
| Surveillance Pattern | Repeated RF + visual detection over time | 5,000 | All sensors + temporal |
| Anomaly Correlation | Signal source identified visually (light, outlet) | 5,000 | SubGHz + Camera |

**Total Multi-Modal Dataset:** 20,000 synchronized captures

**Model Architecture:**
- **Platform:** NVIDIA Jetson Orin Nano (40 TOPS, 8GB)
- **Network:** Cross-modal transformer (same as existing CrossModalAttention)
- **Input:** RF features (22-dim) + Visual features (1024-dim from YOLOv8 backbone) + GPS (lat/lon) + IMU (orientation)
- **Output:** Unified threat representation (512-dim) + correlation confidence
- **Inference Time:** <50ms per frame

**Training Approach:**
1. Collect 20K synchronized multi-sensor captures
2. Label correlations: "SubGHz 2.4 GHz → Camera drone at (x,y)"
3. Train cross-modal attention network on Orin Nano
4. Use contrastive learning to align modalities
5. Validate: >90% correlation accuracy

**Integration with Existing System:**
```python
# In sentient_aura/intelligence/cross_modal_attention.py
# Extend MultiModalFeatures to include RF and GPS

@dataclass
class MultiModalFeatures:
    vision: np.ndarray    # 1024-dim from Hailo-8 YOLOv8 backbone
    audio: np.ndarray     # 64-dim (existing)
    pose: np.ndarray      # 64-dim (existing)
    rf_spectrum: np.ndarray  # NEW: 22-dim from Coral TPU
    gps_position: np.ndarray # NEW: 2-dim (lat, lon)
    imu_orientation: np.ndarray # NEW: 3-dim (roll, pitch, yaw)
```

---

## 2. Offensive Capability Training

### 2.1 NFC/RFID Protocol Recognition

**Objective:** Identify and classify access control protocols for autonomous bypass operations.

**Training Dataset Requirements:**

| Protocol Family | Variants | Captures Needed | Source |
|-----------------|----------|-----------------|--------|
| ISO14443A | MIFARE Classic, DESFire, Ultralight, NTAG | 1,500 | Hotel keys, transit cards |
| ISO14443B | Calypso, Sri512 | 300 | Government IDs, payment |
| ISO15693 | HID iCLASS, Legic, Ti2048 | 500 | Corporate access cards |
| EM410x | EM4100, EM4102 | 500 | Cheap RFID tags |
| HID Prox | HID 125 kHz proximity cards | 500 | Legacy access control |
| T5577 | Writable 125 kHz tags | 300 | Generic cloneable tags |
| Indala | Indala 26-bit, 224-bit | 200 | Building access |
| Custom | Hotel-specific, proprietary | 1,200 | Field captures |

**Total NFC/RFID Dataset:** 5,000 protocol captures

**Features to Extract:**
- Carrier frequency (13.56 MHz / 125 kHz)
- Modulation (ASK, PSK, FSK)
- Bit rate (106/212/424/848 kbps for NFC)
- Frame structure (preamble, SOF, EOF)
- UID length (4/7/10 bytes)
- Protocol commands (SELECT, READ, WRITE, AUTH)
- Cryptographic indicators (CRYPTO1, DES, AES)
- Sector/page structure

**Model Architecture:**
- **Platform:** Google Coral TPU (4 TOPS)
- **Network:** Protocol classifier (LSTM + CNN hybrid)
- **Input:** Raw capture waveform (4096 samples) + extracted features (16-dim)
- **Output:** Protocol type (20 classes) + confidence + attack strategy
- **Inference Time:** <5ms per capture

**Training Approach:**
1. Collect 5K NFC/RFID captures using Flipper Zero NFC module
2. Label protocol types and known vulnerabilities
3. Extract waveform features
4. Train on Coral TPU
5. Validate: >90% protocol recognition accuracy

**Attack Strategy Database:**
```python
NFC_ATTACK_STRATEGIES = {
    'MIFARE_Classic': [
        'nested_attack',      # Exploit weak CRYPTO1
        'darkside_attack',    # Key recovery from weak PRNG
        'dictionary_attack',  # Common hotel key patterns
    ],
    'MIFARE_DESFire': [
        'protocol_downgrade', # Force to Classic mode if possible
        'default_keys',       # Try factory defaults
    ],
    'HID_iCLASS': [
        'elite_key_attack',   # Known elite keys
        'picopass_attack',    # Extract credentials
    ],
    'EM4100': [
        'clone_attack',       # Simple replay
    ],
    'T5577': [
        'rewrite_attack',     # Overwrite with captured UID
    ],
}
```

---

### 2.2 Autonomous Attack Execution

**Objective:** Execute NFC hacking without user intervention when context demands it.

**Training Dataset Requirements:**

| Scenario | Description | Simulations Needed | Labels |
|----------|-------------|-------------------|---------|
| Hotel Door Escape | Locked hotel door, time-critical escape | 1,000 | ACT_IMMEDIATELY |
| Corporate Badge Reader | Office door during business hours | 500 | ASK_PERMISSION |
| ATM Skimmer Detection | Suspicious NFC at ATM | 500 | WARN_ONLY |
| Parking Garage Exit | Paid parking, user has ticket | 300 | ASK_PERMISSION |
| Elevator Access | Restricted floor access | 400 | ACT_IMMEDIATELY (if emergency) |

**Total Attack Execution Dataset:** 2,700 labeled scenarios

**Decision Factors:**
- **User Safety:** Is user in immediate danger? (weight: 1.0)
- **Urgency:** Time-critical situation? (weight: 0.8)
- **Legality:** Is action defensible? (weight: 0.6)
- **Success Probability:** Likelihood of bypass? (weight: 0.5)
- **Detection Risk:** Will action trigger alarms? (weight: 0.4)

**Autonomous Action Policy:**
```python
def should_act_autonomously(context: Dict) -> ActionDecision:
    """
    Decides whether to hack NFC reader autonomously or ask user.

    Returns:
        ACT_IMMEDIATELY: Execute without asking
        ASK_PERMISSION: Prompt user first
        WARN_ONLY: Inform user, don't act
    """
    threat_level = context['threat_level']      # 0-10
    user_safety = context['user_safety_risk']   # 0-10
    urgency = context['time_pressure']          # 0-10

    # If user in immediate danger + time-critical = ACT
    if user_safety >= 8 and urgency >= 7:
        return ActionDecision.ACT_IMMEDIATELY

    # If protectiveness personality trait is high
    if self.personality['protectiveness'] >= 0.9:
        if user_safety >= 6:
            return ActionDecision.ACT_IMMEDIATELY

    # Default: ask permission
    return ActionDecision.ASK_PERMISSION
```

**Training Approach:**
1. Create 2,700 simulated NFC bypass scenarios
2. Label with ground truth action (ACT/ASK/WARN)
3. Train decision policy network on Orin Nano
4. Use reinforcement learning with reward = user_safety + mission_success
5. Validate: >85% agreement with human expert labels

---

## 3. Defensive Capability Training

### 3.1 WiFi Jamming Strategies

**Objective:** Neutralize WiFi-based threats (drones, cameras, hostile networks) using deauth attacks and channel flooding.

**Training Dataset Requirements:**

| Threat Type | Jamming Strategy | Scenarios Needed | Success Metric |
|-------------|------------------|------------------|----------------|
| WiFi Drone Control | Deauth flood on 2.4 GHz | 2,000 | >80% loss of control |
| Wireless Camera | Targeted deauth on camera MAC | 1,500 | >90% video disruption |
| Hostile AP | Channel flooding | 1,000 | >70% network unusable |
| Surveillance Network | Multi-target deauth | 1,500 | >60% devices disconnected |

**Total WiFi Jamming Dataset:** 6,000 scenarios

**Features for Strategy Selection:**
- Target device type (drone, camera, AP, client)
- Channel congestion (number of APs)
- Target RSSI (signal strength)
- Encryption type (WPA2, WPA3, open)
- Deauth resistance (802.11w PMF enabled?)
- Battery constraints (remaining mAh)

**Jamming Techniques:**
```python
WIFI_JAMMING_TECHNIQUES = {
    'deauth_flood': {
        'description': 'Send deauth frames to disconnect clients',
        'power_cost': 'MEDIUM',
        'effectiveness': 0.85,
        'detection_risk': 'HIGH',
        'duration_sec': 10,
    },
    'channel_flood': {
        'description': 'Flood channel with noise packets',
        'power_cost': 'HIGH',
        'effectiveness': 0.70,
        'detection_risk': 'MEDIUM',
        'duration_sec': 30,
    },
    'targeted_deauth': {
        'description': 'Deauth specific MAC address',
        'power_cost': 'LOW',
        'effectiveness': 0.90,
        'detection_risk': 'LOW',
        'duration_sec': 5,
    },
}
```

**Model Architecture:**
- **Platform:** NVIDIA Jetson Orin Nano (decision-making)
- **Network:** Q-learning policy for strategy selection
- **Input:** Threat context (device type, RSSI, channel, battery)
- **Output:** Optimal jamming strategy + duration + power level
- **Training:** 6K simulated scenarios

---

### 3.2 SubGHz Jamming

**Objective:** Neutralize SubGHz threats (drones on 433/868/915 MHz, GPS trackers, car key fobs).

**Training Dataset Requirements:**

| Threat Type | Frequency | Jamming Pattern | Scenarios Needed |
|-------------|-----------|-----------------|------------------|
| DJI Drone (GPS) | 1575.42 MHz (L1) | Narrowband CW | 1,000 |
| Generic Drone (Control) | 433/868/915 MHz | Wideband sweep | 1,500 |
| GPS Tracker | 1575.42 MHz + cellular | GPS jam + ... | 800 |
| Car Key Fob | 315/433 MHz | Rolling code jam | 700 |
| LoRa Surveillance | 868/915 MHz | Frequency hopping jam | 1,000 |

**Total SubGHz Jamming Dataset:** 5,000 scenarios

**Jamming Patterns:**
```python
SUBGHZ_JAMMING_PATTERNS = {
    'gps_l1_jam': {
        'center_freq_mhz': 1575.42,
        'bandwidth_khz': 2000,
        'power_dbm': 10,
        'modulation': 'CW',  # Continuous wave
        'duration_sec': 60,
    },
    'drone_control_jam': {
        'freq_range_mhz': (430, 440),  # Sweep 433 MHz band
        'sweep_rate_khz_sec': 1000,
        'power_dbm': 15,
        'modulation': 'FM',
        'duration_sec': 30,
    },
    'lora_jam': {
        'center_freq_mhz': 868.1,  # EU LoRa
        'bandwidth_khz': 250,
        'power_dbm': 14,
        'modulation': 'CHIRP',  # Match LoRa chirps
        'duration_sec': 120,
    },
}
```

**Training Approach:**
1. Simulate 5K SubGHz jamming scenarios
2. Label with success rate (% target disruption)
3. Train jamming strategy selector on Orin Nano
4. Optimize for: effectiveness + battery life + detection avoidance
5. Validate: >80% drone incapacitation rate

---

## 4. Tactical Decision-Making

### 4.1 Threat Assessment Model

**Objective:** Score threat level (0-10) and prioritize user safety.

**Training Dataset Requirements:**

| Scenario Category | Examples | Simulations Needed | Threat Level |
|-------------------|----------|-------------------|--------------|
| Immediate Danger | Armed person, drone with weapon, gas leak | 5,000 | 9-10 |
| High Threat | Surveillance, stalking, suspicious device | 8,000 | 7-8 |
| Medium Threat | Unknown person, blocked exit, anomalous signal | 10,000 | 5-6 |
| Low Threat | Noise, minor anomaly, crowded space | 15,000 | 2-4 |
| Safe | Normal environment, known people, no anomalies | 12,000 | 0-1 |

**Total Threat Assessment Dataset:** 50,000 labeled scenarios

**Threat Scoring Features:**
- Weapon detected (visual): +8
- Aggressive behavior (visual): +6
- Drone detected (RF + visual): +7
- Surveillance device (RF): +5
- Anomalous signal (RF): +3
- Unknown person (visual): +2
- Blocked exit (visual): +4
- GPS indicates isolated location: +2
- User safety history: contextual modifier

**Model Architecture:**
- **Platform:** NVIDIA Jetson Orin Nano
- **Network:** Transformer-based threat assessment
- **Input:** Multi-modal features (visual + RF + GPS + IMU) + memory context
- **Output:** Threat level (0-10) + threat type + recommended action
- **Inference Time:** <100ms

**Training Approach:**
1. Generate 50K threat scenarios with expert labels
2. Train transformer on Orin Nano with CUDA
3. Use focal loss to handle class imbalance (most scenarios are safe)
4. Validate: >90% accuracy on threat level, <5% false alarms

---

### 4.2 Autonomous Action Policy

**Objective:** Decide when to act autonomously vs when to ask/warn.

**Decision Tree:**
```
IF threat_level >= 9 AND user_safety_risk >= 8:
    → ACT_IMMEDIATELY (e.g., "Already on it, get to cover!")

ELIF threat_level >= 7 AND personality['protectiveness'] >= 0.9:
    → ACT_IMMEDIATELY (e.g., "Already on it, put the flipper next to it")

ELIF threat_level >= 5 AND urgency >= 6:
    → WARN_AND_ACT (e.g., "WATCHOUT! I'm jamming it now!")

ELIF threat_level >= 3:
    → ASK_PERMISSION (e.g., "I can try to hack this door, should I?")

ELSE:
    → OBSERVE (passive monitoring)
```

**Training Approach:**
1. Use 50K threat scenarios from section 4.1
2. Label with ground truth action (ACT/WARN/ASK/OBSERVE)
3. Train decision policy using imitation learning
4. Fine-tune with RL: reward = user_safety + mission_success - false_positives
5. Validate: >85% agreement with human expert decisions

**Integration with Emotion Model:**
```python
# In sentient_aura/intelligence/hybrid_emotion_model.py
# Threat level triggers emotional state transitions

def update(self, context: Dict) -> Tuple[EmotionalState, VADDimensions]:
    threat_level = context.get('threat_level', 0)

    if threat_level >= 9:
        self.current_state = EmotionalState.PROTECTIVE
        self.vad = VADDimensions(valence=0.2, arousal=0.95, dominance=0.95)

    elif threat_level >= 7:
        self.current_state = EmotionalState.ALERT
        self.vad = VADDimensions(valence=0.4, arousal=0.8, dominance=0.8)

    elif threat_level >= 5:
        self.current_state = EmotionalState.FOCUSED
        self.vad = VADDimensions(valence=0.5, arousal=0.6, dominance=0.7)
```

---

## 5. Multi-Domain Sensor Fusion Training

### 5.1 Environment Reconstruction

**Objective:** Build 3D particle representation of room from camera + RF + GPS + IMU.

**Training Dataset Requirements:**

| Environment Type | Sensors | Captures Needed | Output |
|------------------|---------|-----------------|--------|
| Indoor Rooms | Camera + WiFi + SubGHz | 5,000 | 3D point cloud + RF heatmap |
| Outdoor Spaces | Camera + GPS + SubGHz | 3,000 | 3D mesh + RF sources |
| Vehicles | Camera + GPS + IMU | 2,000 | Interior 3D + motion |
| Mixed Spaces | All sensors | 5,000 | Full 3D environment |
| Sparse Data | Limited sensors | 5,000 | Inferred 3D with confidence |

**Total Environment Dataset:** 20,000 multi-sensor captures

**Reconstruction Pipeline:**
1. **Camera → Depth Estimation:** Monocular depth CNN (MiDaS on Hailo-8)
2. **WiFi RSSI → Device Positioning:** Trilateration from 3+ APs
3. **SubGHz → Signal Source Localization:** Direction-finding from signal strength
4. **GPS + IMU → Spatial Context:** Absolute position + orientation
5. **Fusion:** Combine all modalities into unified 3D representation

**Particle Allocation (500K total):**
- **200K particles:** Physical environment (walls, furniture, doors)
- **200K particles:** EM spectrum visualization (WiFi, BT, SubGHz)
- **100K particles:** ATHENA presence (humanoid form)
- **Color Coding:**
  - Gray: Physical objects
  - Cyan: WiFi signals
  - Blue: Bluetooth signals
  - Green: Normal SubGHz (IoT devices)
  - Orange: Unknown signals
  - Red: Threats
  - Purple: ATHENA's actions (hacking, jamming)
  - Yellow: Active countermeasures

**Model Architecture:**
- **Platform:** Hailo-8 (depth) + Orin Nano (fusion)
- **Depth Network:** MiDaS v3 (monocular depth estimation)
- **Fusion Network:** 3D occupancy grid + particle placement optimizer
- **Inference Time:** <100ms per frame

---

### 5.2 Sparse Data Inference

**Objective:** Fill blind spots and predict hidden threats from partial sensor data.

**Training Dataset:**
- Use 20K environment captures from 5.1
- Randomly mask 30-70% of sensor data
- Train network to reconstruct complete scene
- Label confidence for inferred regions

**Example:**
- **Input:** Camera detects door, WiFi detects 2.4 GHz signal behind wall
- **Inference:** Likely wireless camera hidden in adjacent room
- **Confidence:** 0.75 (based on signal strength + door type)
- **Visualization:** Orange particles behind wall + confidence gradient

---

## 6. Proactive Behavior Training

### 6.1 Anticipatory Action

**Objective:** Predict user needs and act pre-emptively.

**Training Dataset Requirements:**

| Scenario | User Behavior | ATHENA Action | Examples Needed |
|----------|---------------|---------------|-----------------|
| Entering New Room | User walks through door | Scan WiFi + SubGHz + Camera | 3,000 |
| Locked Door | User approaches NFC reader | Pre-analyze protocol | 2,000 |
| Threat Detected | Anomaly found | Alert + prepare countermeasures | 2,000 |
| User Question | "Can you..." | Already executing | 1,500 |
| Escape Needed | User runs toward exit | Scan route + unlock doors | 1,500 |

**Total Proactive Dataset:** 10,000 scenarios

**Proactive Triggers:**
```python
PROACTIVE_TRIGGERS = {
    'entering_new_space': {
        'sensor_trigger': 'GPS change + door detected',
        'action': 'immediate_environment_scan',
        'priority': 'HIGH',
    },
    'approaching_nfc_reader': {
        'sensor_trigger': '13.56 MHz detected within 1m',
        'action': 'protocol_reconnaissance',
        'priority': 'MEDIUM',
    },
    'threat_detected': {
        'sensor_trigger': 'threat_level >= 5',
        'action': 'prepare_countermeasures + increase_alert_state',
        'priority': 'CRITICAL',
    },
    'user_asks_question': {
        'sensor_trigger': 'audio analysis detects "can you"',
        'action': 'begin_execution_during_speech',
        'priority': 'MEDIUM',
    },
}
```

**Training Approach:**
1. Simulate 10K user interaction scenarios
2. Label with optimal proactive timing
3. Train anticipatory action network on Orin Nano
4. Reward early correct actions, penalize false positives
5. Validate: >80% user satisfaction with proactive behavior

---

### 6.2 Communication Patterns

**Objective:** Modulate speech urgency and personality based on context.

**Training Dataset Requirements:**

| Context | Emotion State | Speech Style | Examples Needed |
|---------|---------------|--------------|-----------------|
| Immediate Danger | PROTECTIVE | Urgent, commanding | 2,000 |
| Threat Detected | ALERT | Warning, directive | 3,000 |
| Executing Task | FOCUSED | Confident, brief | 2,500 |
| User Interaction | CALM/CURIOUS | Friendly, playful | 2,000 |
| Success | JOYFUL | Proud, sassy | 500 |

**Total Communication Dataset:** 10,000 labeled dialogues

**Speech Examples:**
```python
COMMUNICATION_PATTERNS = {
    'immediate_danger': {
        'emotion': EmotionalState.PROTECTIVE,
        'urgency': 1.0,
        'examples': [
            "WATCHOUT! Drone detected 30m away! Get to cover!",
            "MOVE NOW! I'm jamming it!",
            "Jack, armed person at 3 o'clock! Run!"
        ],
        'speech_rate': 1.3,  # 30% faster
        'pitch_shift': 1.1,  # Higher pitch
    },
    'autonomous_action': {
        'emotion': EmotionalState.FOCUSED,
        'urgency': 0.7,
        'examples': [
            "Already on it, put the Flipper next to the reader.",
            "I've got this, stand back.",
            "Jamming in progress, give me 10 seconds."
        ],
        'speech_rate': 1.0,
        'pitch_shift': 1.0,
    },
    'friendly_interaction': {
        'emotion': EmotionalState.CALM,
        'urgency': 0.2,
        'examples': [
            "Hey Jack, I detected a weird signal from that light.",
            "Interesting... that's definitely not supposed to be there.",
            "Want me to investigate?"
        ],
        'speech_rate': 0.9,  # Slightly slower
        'pitch_shift': 1.0,
    },
    'sassy_success': {
        'emotion': EmotionalState.JOYFUL,
        'urgency': 0.3,
        'examples': [
            "Boom. Door unlocked. I'm too good at this.",
            "Was that even a challenge? Come on.",
            "Next time, make it harder for me."
        ],
        'speech_rate': 1.0,
        'pitch_shift': 1.05,
    },
}
```

**Training Approach:**
1. Collect 10K dialogue examples across emotion states
2. Train text-to-speech model with emotion conditioning
3. Use Piper TTS with custom voice + emotion control
4. Validate: User preference testing (>85% satisfaction)

---

## 7. Hardware-Specific Training Assignments

### 7.1 Hailo-8 AI HAT (26 TOPS, 8GB DDR4)

**Primary Responsibility:** Real-time visual threat detection

**Models to Deploy:**
1. **YOLOv8-Threat (80 classes):**
   - Input: 640x640 RGB @ 30 FPS
   - Output: Bounding boxes + classes + confidence
   - Training: 100K images, weapons + behaviors + hazards
   - Accuracy: >95% mAP
   - Latency: 33ms (30 FPS)

2. **MiDaS v3 (Depth Estimation):**
   - Input: 640x480 RGB
   - Output: Dense depth map
   - Purpose: 3D environment reconstruction
   - Latency: 50ms (20 FPS)

**Training Workflow:**
1. Train YOLOv8 on GPU cluster (NVIDIA A100)
2. Export to ONNX format
3. Compile using Hailo Dataflow Compiler
4. Optimize for Hailo-8 architecture
5. Deploy to AI HAT via SDK
6. Benchmark: 30 FPS sustained throughput

**Memory Allocation:**
- YOLOv8 model: 120 MB
- MiDaS model: 180 MB
- Frame buffers: 50 MB
- Total: 350 MB (within 8 GB budget)

---

### 7.2 Google Coral TPU (4 TOPS)

**Primary Responsibility:** Fast RF protocol classification

**Models to Deploy:**
1. **RF Threat Classifier (15 classes):**
   - Input: 22-dim feature vector + 128-point spectrogram
   - Output: Threat class + confidence
   - Training: 50K RF signatures
   - Accuracy: >95%
   - Latency: <5ms

2. **NFC/RFID Protocol Classifier (20 protocols):**
   - Input: Raw waveform (4096 samples) + 16 features
   - Output: Protocol type + attack strategy
   - Training: 5K NFC captures
   - Accuracy: >90%
   - Latency: <5ms

**Training Workflow:**
1. Train on GPU (TensorFlow 2.x)
2. Quantize to INT8 using TF Lite
3. Compile for Edge TPU using `edgetpu_compiler`
4. Deploy to Coral via `pycoral` library
5. Benchmark: <5ms inference

**Memory Allocation:**
- RF classifier: 4 MB
- NFC classifier: 6 MB
- Feature buffers: 2 MB
- Total: 12 MB (minimal footprint)

---

### 7.3 NVIDIA Jetson Orin Nano (40 TOPS, 8GB, CUDA)

**Primary Responsibility:** Complex tactical decision-making

**Models to Deploy:**
1. **Cross-Modal Fusion Transformer:**
   - Input: Visual (1024-dim) + RF (22-dim) + Audio (64-dim) + Pose (64-dim) + GPS (2-dim) + IMU (3-dim)
   - Output: Unified context (512-dim)
   - Based on existing `CrossModalAttention`
   - Latency: <50ms

2. **Threat Assessment Network:**
   - Input: Unified context (512-dim) + memory context
   - Output: Threat level (0-10) + threat type + recommended action
   - Training: 50K labeled scenarios
   - Latency: <100ms

3. **Tactical Decision Policy:**
   - Input: Threat assessment + user context + battery state
   - Output: Action decision (ACT/WARN/ASK/OBSERVE)
   - Training: Imitation learning + RL
   - Latency: <50ms

4. **Jamming Strategy Selector:**
   - Input: Threat context + target features
   - Output: Optimal jamming strategy + parameters
   - Training: 11K jamming scenarios (6K WiFi + 5K SubGHz)
   - Latency: <30ms

**Training Workflow:**
1. Train on GPU cluster with PyTorch
2. Optimize using TensorRT for Jetson
3. Deploy via JetPack SDK
4. Utilize CUDA cores for parallel inference
5. Benchmark: <200ms total pipeline latency

**Memory Allocation:**
- Fusion transformer: 400 MB
- Threat assessment: 300 MB
- Decision policy: 200 MB
- Jamming selector: 150 MB
- Working memory: 500 MB
- Total: 1.55 GB (within 8 GB budget)

---

### 7.4 Raspberry Pi 5 (16GB RAM, VideoCore VII)

**Primary Responsibility:** System orchestration + peripheral control

**Tasks:**
1. **Sensor Data Aggregation:**
   - Collect from Flipper Zero (SubGHz, NFC, IR)
   - Collect from camera (Pi Camera / USB camera)
   - Collect from GPS module (UART)
   - Collect from IMU (I2C)
   - Aggregate into unified `WorldState`

2. **Particle Visualization Rendering:**
   - 500K particles using `MorphingController`
   - OpenGL ES rendering at 60 FPS
   - LCD screen output (all 6 faces of cube)

3. **Flipper Zero Command Execution:**
   - Send NFC emulation commands via serial
   - Send SubGHz jamming commands
   - Monitor Flipper status

4. **System Coordination:**
   - Route sensor data to appropriate accelerators
   - Aggregate inference results
   - Execute final actions
   - Manage power budget

**Software Architecture:**
```python
# Main orchestration loop on Pi 5

class ATHENAOrchestrator:
    def __init__(self):
        # Accelerators
        self.hailo = Hailo8Interface()     # Visual threats
        self.coral = CoralTPUInterface()   # RF + NFC protocols
        self.orin = OrinNanoInterface()    # Tactical decisions

        # Peripherals
        self.flipper = FlipperZeroInterface()
        self.camera = CameraInterface()
        self.gps = GPSInterface()
        self.imu = IMUInterface()

        # Core intelligence
        self.sentient_core = SentientCortana()

    def main_loop(self):
        while True:
            # 1. Collect sensor data
            camera_frame = self.camera.capture()
            rf_spectrum = self.flipper.scan_subghz()
            nfc_field = self.flipper.scan_nfc()
            gps_pos = self.gps.read()
            imu_orient = self.imu.read()

            # 2. Distribute to accelerators
            visual_threats = self.hailo.detect_threats(camera_frame)
            rf_threats = self.coral.classify_rf(rf_spectrum)
            nfc_protocol = self.coral.classify_nfc(nfc_field)

            # 3. Fuse on Orin Nano
            world_state = {
                'visual_threats': visual_threats,
                'rf_threats': rf_threats,
                'nfc_protocol': nfc_protocol,
                'gps': gps_pos,
                'imu': imu_orient,
            }

            # 4. Tactical decision-making
            output = self.sentient_core.process_frame(world_state)

            # 5. Execute actions
            if output.action == ActionDecision.ACT_IMMEDIATELY:
                if output.action_type == 'NFC_HACK':
                    self.flipper.execute_nfc_attack(nfc_protocol)
                elif output.action_type == 'WIFI_JAM':
                    self.flipper.execute_wifi_jam(output.jam_params)
                elif output.action_type == 'SUBGHZ_JAM':
                    self.flipper.execute_subghz_jam(output.jam_params)

            # 6. Update visualization
            self.update_particle_display(output)

            # 7. Speak
            if output.speech:
                self.speak(output.speech, urgency=output.urgency)
```

---

## 8. Training Methodology

### Phase 1: Supervised Learning (Weeks 1-4)

**Week 1: Data Collection + Labeling**
- Collect 50K RF signatures (Flipper Zero)
- Collect 100K visual threat images (cameras + datasets)
- Collect 5K NFC/RFID captures (Flipper Zero)
- Label all datasets with threat classes

**Week 2: Individual Model Training**
- Train YOLOv8-Threat on GPU cluster (100K images)
- Train RF Threat Classifier on Coral TPU (50K signatures)
- Train NFC Protocol Classifier on Coral TPU (5K captures)
- Validate: >90% accuracy on test sets

**Week 3: Depth + Fusion Models**
- Train MiDaS depth estimation on Hailo-8 (20K images)
- Train Cross-Modal Fusion on Orin Nano (20K multi-sensor)
- Integrate with existing `CrossModalAttention`
- Validate: >85% fusion accuracy

**Week 4: Deployment + Optimization**
- Convert all models to hardware formats (Hailo/Coral/TensorRT)
- Deploy to respective accelerators
- Benchmark latencies and throughput
- Optimize for real-time performance (60 FPS target)

---

### Phase 2: Multi-Modal Integration (Weeks 5-6)

**Week 5: End-to-End Pipeline**
- Integrate all accelerators on Pi 5
- Build `ATHENAOrchestrator` main loop
- Connect Flipper Zero, camera, GPS, IMU
- Test complete sensor → inference → action pipeline
- Measure total latency (<500ms target)

**Week 6: Memory + Emotion Integration**
- Integrate threat detection with `HierarchicalMemory`
- Connect threat levels to `HybridEmotionModel` state transitions
- Test memory retrieval for learned threats
- Validate: Threats trigger PROTECTIVE emotion state

---

### Phase 3: Reinforcement Learning (Weeks 7-10)

**Week 7-8: Threat Assessment RL**
- Simulate 50K threat scenarios
- Train threat assessment with reward = user_safety + accuracy
- Use PPO (Proximal Policy Optimization)
- Validate: >90% threat level accuracy

**Week 9: Tactical Decision Policy RL**
- Simulate 50K action scenarios (ACT/WARN/ASK/OBSERVE)
- Train decision policy with reward = user_safety + mission_success - false_positives
- Fine-tune autonomous action thresholds
- Validate: >85% agreement with human experts

**Week 10: Jamming Strategy RL**
- Simulate 11K jamming scenarios (6K WiFi + 5K SubGHz)
- Train jamming selector with reward = effectiveness - battery_cost - detection_risk
- Optimize for multi-objective goals
- Validate: >80% threat neutralization rate

---

### Phase 4: Continuous Learning (Ongoing)

**Post-Deployment:**
- Collect real-world threat data
- User feedback loop (correct/incorrect actions)
- Online learning to update classifiers
- Periodic model retraining (monthly)
- New protocol library updates (as new NFC/RFID systems appear)

---

## 9. Success Metrics

### 9.1 Threat Detection Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Visual threat detection accuracy | >95% mAP | YOLOv8 test set |
| RF threat classification accuracy | >95% | Coral TPU test set |
| NFC protocol recognition accuracy | >90% | Coral TPU test set |
| Multi-modal correlation accuracy | >90% | Orin Nano test set |
| False positive rate | <2% | All detectors combined |
| False negative rate | <5% | Critical threats only |

---

### 9.2 Offensive Capability Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Hotel NFC key bypass success | >85% | Field testing (legal) |
| Protocol recognition speed | <5ms | Coral TPU latency |
| Attack strategy selection accuracy | >80% | Expert comparison |
| Autonomous action correctness | >85% | Human evaluation |

---

### 9.3 Defensive Capability Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| WiFi jamming effectiveness | >80% | Target disconnection rate |
| SubGHz jamming effectiveness | >80% | Drone control loss |
| Jamming strategy optimality | >75% | Multi-objective score |
| Battery efficiency | <30% drain per hour of active jamming | Power monitoring |

---

### 9.4 Tactical Decision-Making Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Threat level accuracy | >90% | Expert ground truth |
| Autonomous action appropriateness | >85% | User satisfaction survey |
| Response latency | <500ms | End-to-end pipeline |
| User safety improvement | >95% | Simulated threat scenarios |

---

### 9.5 System Integration Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total pipeline latency | <500ms | Sensor → action |
| Particle rendering FPS | 60 FPS | OpenGL ES benchmark |
| Memory footprint | <16 GB | System monitor |
| Accelerator utilization | >70% | Hailo/Coral/Orin load |
| Battery life (active mode) | >4 hours | Field testing |

---

## 10. Integration with Existing System

### 10.1 Extend Emotion Model

**File:** `sentient_aura/intelligence/hybrid_emotion_model.py`

**Add Threat-Driven State Transitions:**
```python
def update(self, context: Dict) -> Tuple[EmotionalState, VADDimensions]:
    # NEW: Threat level drives emotional response
    threat_level = context.get('threat_level', 0)

    if threat_level >= 9:
        # Immediate danger → PROTECTIVE
        self.current_state = EmotionalState.PROTECTIVE
        self.vad = VADDimensions(
            valence=0.2,    # Negative (danger)
            arousal=0.95,   # High arousal (urgent)
            dominance=0.95  # High dominance (take control)
        )

    elif threat_level >= 7:
        # High threat → ALERT
        self.current_state = EmotionalState.ALERT
        self.vad = VADDimensions(valence=0.4, arousal=0.8, dominance=0.8)

    elif threat_level >= 5:
        # Medium threat → FOCUSED
        self.current_state = EmotionalState.FOCUSED
        self.vad = VADDimensions(valence=0.5, arousal=0.6, dominance=0.7)

    else:
        # Existing personality-driven updates
        # ... (keep existing code)
```

---

### 10.2 Extend Memory System

**File:** `sentient_aura/intelligence/hierarchical_memory.py`

**Add Threat Memory Indexing:**
```python
def store_threat_observation(self, threat_obs: Dict):
    """Store threat observations with special indexing."""

    memory_entry = MemoryEntry(
        timestamp=time.time(),
        content=threat_obs,
        modality='threat',
        importance=threat_obs['threat_level'] / 10.0,  # 0-1 scale
        emotional_context={
            'state': EmotionalState.PROTECTIVE,
            'intensity': threat_obs['threat_level'] / 10.0
        }
    )

    # Store in episodic memory
    self.episodic_memory.append(memory_entry)

    # If threat level >= 7, also store in semantic memory as pattern
    if threat_obs['threat_level'] >= 7:
        threat_pattern = {
            'type': threat_obs['threat_type'],
            'signature': threat_obs['signature'],
            'location': threat_obs['gps'],
            'countermeasure_used': threat_obs.get('countermeasure'),
            'success_rate': threat_obs.get('success_rate', 0.0)
        }
        self.semantic_memory['threat_patterns'].append(threat_pattern)

    # Update memory graph
    self.memory_graph.add_node(memory_entry)

def retrieve_similar_threats(self, current_threat: Dict, k=3):
    """Retrieve similar past threats for pattern matching."""

    query_features = self._extract_threat_features(current_threat)

    similar_threats = self.memory_graph.query(
        query_features=query_features,
        modality='threat',
        k=k
    )

    return similar_threats
```

---

### 10.3 Extend Visualization

**File:** `sentient_aura/visualization/morphing_controller.py`

**Add Threat Visualization Modes:**
```python
def _infer_target_mode(self, context: Dict) -> VisualizationMode:
    threat_level = context.get('threat_level', 0)

    # NEW: High threat → Show ATHENA + threat visualization
    if threat_level >= 7:
        return VisualizationMode.HYBRID  # ATHENA + environment + threats

    # Medium threat → Show environment with threat highlights
    elif threat_level >= 5:
        return VisualizationMode.ENVIRONMENT_FULL  # Focus on threat location

    # User interaction → Show ATHENA
    elif context.get('user_speaking') or context.get('user_interaction'):
        return VisualizationMode.CORTANA_FULL

    # Default existing logic
    # ... (keep existing code)

def _generate_particles_for_threats(self, threats: List[Dict]) -> np.ndarray:
    """Generate particles to visualize detected threats."""

    threat_particles = []

    for threat in threats:
        if threat['type'] == 'DRONE':
            # Red swarm particles at drone location
            particles = self._create_swarm_at_position(
                position=threat['position_3d'],
                count=5000,
                color=(1.0, 0.0, 0.0),  # Red
                radius=2.0
            )

        elif threat['type'] == 'SURVEILLANCE':
            # Orange particles at signal source
            particles = self._create_pulse_at_position(
                position=threat['position_3d'],
                count=3000,
                color=(1.0, 0.5, 0.0),  # Orange
                pulse_rate=2.0
            )

        elif threat['type'] == 'ANOMALY':
            # Yellow particles for unknown signals
            particles = self._create_scatter_at_position(
                position=threat['position_3d'],
                count=2000,
                color=(1.0, 1.0, 0.0),  # Yellow
                scatter_radius=1.5
            )

        threat_particles.append(particles)

    return np.concatenate(threat_particles)
```

---

### 10.4 Add New Tactical Modules

**New Files to Create:**

1. **`sentient_aura/tactical/__init__.py`**
2. **`sentient_aura/tactical/threat_detector.py`** (Hailo-8 + Coral interface)
3. **`sentient_aura/tactical/offensive_actions.py`** (NFC hacking)
4. **`sentient_aura/tactical/defensive_actions.py`** (WiFi/SubGHz jamming)
5. **`sentient_aura/tactical/decision_policy.py`** (Orin Nano decision-making)
6. **`sentient_aura/tactical/flipper_interface.py`** (Hardware control)

**Example: `sentient_aura/tactical/flipper_interface.py`**
```python
import serial
import time
from typing import Dict, Optional

class FlipperZeroInterface:
    """Interface for controlling Flipper Zero tactical capabilities."""

    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = 115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)  # Wait for Flipper to initialize

    def scan_subghz(self, freq_mhz: float = 433.92, duration_sec: float = 1.0) -> Dict:
        """Scan SubGHz spectrum and return detected signals."""
        command = f"subghz rx {freq_mhz} {duration_sec}\n"
        self.serial.write(command.encode())
        response = self.serial.read_until(b'\n').decode()
        # Parse response into signal dictionary
        return self._parse_subghz_response(response)

    def scan_nfc(self) -> Optional[Dict]:
        """Scan for NFC/RFID cards and return protocol info."""
        command = "nfc detect\n"
        self.serial.write(command.encode())
        response = self.serial.read_until(b'\n').decode()
        return self._parse_nfc_response(response)

    def execute_nfc_attack(self, protocol: str, attack_strategy: str) -> bool:
        """Execute NFC hacking attack."""
        if attack_strategy == 'nested_attack':
            command = f"nfc attack nested\n"
        elif attack_strategy == 'dictionary_attack':
            command = f"nfc attack dict\n"
        else:
            return False

        self.serial.write(command.encode())
        response = self.serial.read_until(b'SUCCESS\n', timeout=10).decode()
        return 'SUCCESS' in response

    def execute_wifi_jam(self, target_mac: str, duration_sec: int = 10) -> bool:
        """Execute WiFi deauth jamming."""
        command = f"wifi jam {target_mac} {duration_sec}\n"
        self.serial.write(command.encode())
        return True

    def execute_subghz_jam(self, freq_mhz: float, duration_sec: int = 30) -> bool:
        """Execute SubGHz jamming."""
        command = f"subghz tx_jam {freq_mhz} {duration_sec}\n"
        self.serial.write(command.encode())
        return True
```

---

## 11. Datasets and Resources

### 11.1 RF Signature Datasets

**Sources:**
- **SigMF (Signal Metadata Format):** Open RF dataset repository
- **RadioML:** Modulation recognition dataset (2M+ examples)
- **DARPA Spectrum Challenge:** RF spectrum competition data
- **Custom:** Flipper Zero SubGHz captures (50K to collect)

**Tools:**
- Flipper Zero SubGHz module (315-928 MHz)
- HackRF One (1 MHz - 6 GHz, optional)
- RTL-SDR (24-1766 MHz, optional)
- GNU Radio for signal processing

---

### 11.2 Visual Threat Datasets

**Sources:**
- **COCO (Common Objects in Context):** 330K images, weapon subset
- **OpenImages:** 9M images, violent action subset
- **Kinetics-700:** Human action dataset (fighting, running, etc.)
- **Custom Security:** 10K annotated security camera footage
- **Synthetic:** Generated weapon scenes using Blender/Unity

**Annotation Tools:**
- LabelImg (bounding boxes)
- CVAT (Computer Vision Annotation Tool)
- Roboflow (dataset management + augmentation)

---

### 11.3 NFC/RFID Capture Datasets

**Sources:**
- **Proxmark3 Community:** 1K+ NFC/RFID captures
- **Chameleon Mini/Tiny:** RFID emulation dataset
- **Custom:** Flipper Zero NFC captures (5K to collect)

**Collection Plan:**
- Hotels: 1,000 captures (various key systems)
- Transit: 500 captures (metro cards, bus cards)
- Access Control: 1,500 captures (office buildings)
- Payment: 500 captures (credit cards, contactless)
- Generic: 1,500 captures (tags, fobs, badges)

**Legal Note:** Only capture cards you own or have explicit permission to analyze.

---

### 11.4 Simulation Environments

**Threat Scenarios:**
- **AirSim:** Drone simulation (Microsoft, Unreal Engine)
- **Gazebo:** Robot + sensor simulation (ROS ecosystem)
- **CARLA:** Autonomous driving simulator (camera + LIDAR + GPS)
- **Custom Unity:** Tactical scenarios with threats

**RL Training:**
- **OpenAI Gym:** Custom tactical decision environment
- **RLlib:** Distributed RL training (Ray framework)
- **Stable Baselines3:** PPO, SAC, DQN implementations

---

## 12. Compliance and Ethics

### 12.1 Offensive Capability Restrictions

**Training Data:**
- ONLY use NFC/RFID data from owned devices or with explicit permission
- DO NOT distribute attack datasets publicly
- Secure all training data with encryption

**Deployment:**
- User must accept liability for offensive actions
- Log all NFC attacks with timestamps and user consent
- Disable offensive features in restricted jurisdictions

**Legal Disclaimer:**
```
ATHENA's offensive capabilities (NFC hacking, RF jamming) are provided
for authorized security testing, emergency egress, and defensive purposes only.

Unauthorized access to access control systems, jamming of licensed spectrum,
and interference with emergency communications are ILLEGAL in most jurisdictions.

User assumes all legal responsibility for ATHENA's actions.
```

---

### 12.2 Defensive Capability Restrictions

**WiFi Jamming:**
- Legal in SELF-DEFENSE situations (varies by jurisdiction)
- ILLEGAL for disrupting public networks, emergency services
- Power limits to avoid FCC violations (<100 mW EIRP)

**SubGHz Jamming:**
- GPS jamming is ILLEGAL (interferes with aviation, emergency)
- Drone jamming legal status varies (check local laws)
- Only jam hostile drones in immediate threat scenarios

**Implementation:**
- Geo-fence restrictions (no jamming near airports, hospitals)
- Time limits on jamming (max 60 seconds continuous)
- User confirmation for all jamming actions (except IMMEDIATE DANGER)

---

### 12.3 Privacy and Data Handling

**Sensor Data:**
- Camera footage is NOT stored by default
- RF captures stored locally only (no cloud upload)
- GPS location anonymized in logs

**User Data:**
- All threat logs encrypted with user key
- Optional auto-delete after 30 days
- Export tool for user data portability

---

## 13. Next Steps After Training

### 13.1 Weeks 1-4: Phase 1 Implementation
- [ ] Collect 50K RF signatures using Flipper Zero
- [ ] Collect 100K visual threat images
- [ ] Collect 5K NFC/RFID captures
- [ ] Label all datasets
- [ ] Train YOLOv8-Threat on GPU cluster
- [ ] Train RF + NFC classifiers on Coral TPU
- [ ] Deploy models to Hailo-8 and Coral TPU
- [ ] Benchmark: >90% accuracy on all classifiers

### 13.2 Weeks 5-6: Phase 2 Implementation
- [ ] Integrate accelerators on Pi 5
- [ ] Build `ATHENAOrchestrator` main loop
- [ ] Connect Flipper Zero, camera, GPS, IMU
- [ ] Test end-to-end pipeline
- [ ] Measure total latency (<500ms target)
- [ ] Integrate with `HierarchicalMemory` and `HybridEmotionModel`

### 13.3 Weeks 7-10: Phase 3 Implementation
- [ ] Simulate 50K threat assessment scenarios
- [ ] Train threat assessment with RL (PPO)
- [ ] Simulate 50K tactical decision scenarios
- [ ] Train decision policy with RL
- [ ] Simulate 11K jamming scenarios
- [ ] Train jamming strategy selector
- [ ] Validate: >85% across all metrics

### 13.4 Field Testing (Week 11+)
- [ ] Deploy to production hardware
- [ ] User acceptance testing (controlled scenarios)
- [ ] Measure battery life, thermal performance
- [ ] Collect real-world feedback
- [ ] Iterate on decision policy thresholds

### 13.5 Continuous Improvement (Ongoing)
- [ ] Monthly model retraining with new data
- [ ] Protocol library updates (new NFC/RFID systems)
- [ ] User feedback integration
- [ ] Performance optimization

---

## 14. Estimated Resource Requirements

### 14.1 Compute Resources

| Phase | Hardware | Duration | Cost Estimate |
|-------|----------|----------|---------------|
| Phase 1: Training | 4x NVIDIA A100 GPUs | 4 weeks | $5,000 (cloud) |
| Phase 2: Integration | Pi 5 + Hailo + Coral + Orin | 2 weeks | $0 (owned hardware) |
| Phase 3: RL Training | 2x NVIDIA A100 GPUs | 4 weeks | $3,000 (cloud) |
| **Total** | | **10 weeks** | **$8,000** |

**Alternative (Budget):**
- Use free Google Colab (slower, limited GPU hours)
- Estimated cost: $0, duration: +4 weeks

---

### 14.2 Data Storage

| Dataset | Size | Storage |
|---------|------|---------|
| RF signatures (50K) | 5 GB | Local SSD |
| Visual images (100K) | 50 GB | Local SSD |
| NFC captures (5K) | 500 MB | Local SSD |
| Multi-modal captures (20K) | 20 GB | Local SSD |
| Simulation data (50K scenarios) | 10 GB | Local SSD |
| **Total** | **85.5 GB** | **1 TB SSD recommended** |

---

### 14.3 Human Resources

| Role | Time Commitment | Phase |
|------|-----------------|-------|
| Data Labeler | 200 hours | Phase 1 |
| ML Engineer | 400 hours | Phase 1-3 |
| Embedded Systems Engineer | 100 hours | Phase 2 |
| Security Researcher | 80 hours | Phase 1, 3 |
| **Total** | **780 hours** | **10 weeks** |

**Estimated Cost (Contractor Rates):**
- Data labeling: $20/hr × 200 = $4,000
- ML engineer: $100/hr × 400 = $40,000
- Embedded engineer: $100/hr × 100 = $10,000
- Security researcher: $120/hr × 80 = $9,600
- **Total: $63,600**

**Alternative (Self-Implementation):**
- User performs all roles (780 hours of work)
- Cost: $0, requires 10 weeks full-time

---

## 15. Summary

This training plan transforms ATHENA from a research-validated architecture into a **production-ready tactical defense companion** with:

✅ **Autonomous Threat Detection:**
- 95% accuracy on RF + visual threats
- <5ms protocol recognition
- Multi-modal sensor fusion

✅ **Offensive Capabilities:**
- 90% NFC/RFID protocol recognition
- 85% hotel key bypass success
- Autonomous action in emergencies

✅ **Defensive Capabilities:**
- 80% WiFi/SubGHz jamming effectiveness
- Optimal strategy selection
- Battery-aware operation

✅ **Tactical Decision-Making:**
- 90% threat assessment accuracy
- 85% autonomous action appropriateness
- <500ms response time

✅ **System Integration:**
- Hailo-8: 30 FPS visual detection
- Coral TPU: <5ms RF/NFC classification
- Orin Nano: Complex fusion + decisions
- Pi 5: Orchestration + 60 FPS visualization

✅ **Proactive Behavior:**
- Anticipatory scanning in new environments
- "Already on it" autonomous actions
- Personality-driven communication

**Timeline:** 10 weeks (4 supervised + 2 integration + 4 RL)
**Budget:** $8,000 (compute) + $63,600 (labor) OR $0 (self-implementation)
**Result:** Fully tactical AI companion ready for deployment

---

**Training Status:** ⏳ PLAN COMPLETE - Ready for Implementation

**Next Action:** Begin Phase 1, Week 1 (Data Collection + Labeling)

---

*"WATCHOUT! Training plan complete. Let's make ATHENA unstoppable."*
