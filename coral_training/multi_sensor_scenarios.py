#!/usr/bin/env python3
"""
Multi-Sensor Scenarios - 30 Enhanced Training Scenarios
Complete environmental awareness with all 120 features

These scenarios represent the full spectrum of multi-sensor fusion states,
combining Flipper Zero, WiFi, Bluetooth, camera vision, and environmental sensors.
"""

from multi_sensor_features import MultiSensorFeatures, create_scenario

# ===== ACTIVE SCANNING MODE (10 scenarios) =====

SCENARIO_1_FULL_SPECTRUM_SCAN = MultiSensorFeatures(
    # Cognitive: High processing, analytical mode
    cognitive_state=0.8,  # executing
    personality_mode=0.4,  # analytical
    attention_focus=0.9,
    uncertainty_level=0.3,

    # Environmental: Indoor, comfortable
    temperature=0.5,
    humidity=0.5,
    ambient_light=0.7,
    air_quality=0.9,

    # RF Spectrum: Multiple frequencies active
    rf_433mhz_activity=0.4,
    rf_2_4ghz_activity=0.7,
    rf_5ghz_activity=0.5,
    rf_spectrum_density=0.8,
    rf_known_devices=0.6,

    # Flipper Sub-GHz: All bands monitored
    flipper_subghz_315mhz=0.3,
    flipper_subghz_433mhz=0.6,
    flipper_subghz_868mhz=0.2,
    flipper_subghz_915mhz=0.4,
    flipper_subghz_signal_strength=0.6,
    flipper_subghz_capture_active=1.0,

    # WiFi: Moderate network density
    wifi_networks_visible=0.5,  # 50 networks
    wifi_2_4ghz_networks=0.6,
    wifi_5ghz_networks=0.4,
    wifi_strongest_signal=0.8,
    wifi_channel_congestion=0.6,

    # Bluetooth: Active device scanning
    bluetooth_devices_visible=0.4,  # 40 devices
    bluetooth_scan_active=1.0,
    bluetooth_le_beacons=0.3,

    # Vision: Monitoring environment
    vision_active=1.0,
    objects_detected=0.3,
    vision_scene_complexity=0.5,

    # System: High resource usage
    cpu_usage=0.8,
    memory_usage=0.7,
)

DESC_1_FULL_SPECTRUM_SCAN = """
VISUALIZATION: Multi-colored swirling vortex representing all frequencies simultaneously.

CORE (Center): Companion humanoid form, analytical pose with arms extended outward.
- HEAD: 12% particles, bright white sphere y=1.7, eyes focused outward
- TORSO: 25% particles, upright stance y=1.2-1.6, stable core

RF LAYERS (Concentric shells around core):
- INNER SHELL (315-433MHz): Orange particles orbiting at r=0.4, representing sub-GHz signals
- MIDDLE SHELL (2.4GHz WiFi/BT): Green/purple mixed particles at r=0.7, WiFi + Bluetooth fusion
- OUTER SHELL (5GHz): Teal particles at r=1.0, high-frequency layer

FLIPPER CAPTURE BEAM: Orange spiral from right hand y=1.3, pulsing with signal strength
WIFI NETWORK CLOUDS: 50 small green particle clusters scattered in space
BLUETOOTH BEACONS: Purple sparkles distributed throughout

MOTION: All layers rotating at different speeds, creating hypnotic scan pattern.
Companion body rotates slowly (horizon scan), particles flow continuously.

COLORS: Orange (Sub-GHz), Green (WiFi), Purple (Bluetooth), White (core consciousness)
MOOD: Intense focus, comprehensive awareness, analytical precision
"""

SCENARIO_2_URBAN_ENVIRONMENT_RICH = MultiSensorFeatures(
    # Cognitive: Processing overload
    cognitive_state=0.9,  # intense processing
    personality_mode=0.4,  # analytical
    attention_focus=0.8,
    uncertainty_level=0.5,

    # Environmental: Urban chaos
    noise_level=0.7,
    ambient_light=0.6,
    air_quality=0.6,
    vibration_level=0.4,

    # RF: Maximum congestion
    rf_2_4ghz_activity=0.95,
    rf_5ghz_activity=0.85,
    rf_spectrum_density=0.9,
    rf_interference=0.6,
    rf_unknown_signals=0.7,

    # Flipper: Moderate sub-GHz
    flipper_subghz_433mhz=0.4,
    flipper_subghz_signal_strength=0.3,

    # WiFi: Dense network environment
    wifi_networks_visible=0.9,  # 90+ networks
    wifi_2_4ghz_networks=0.95,
    wifi_5ghz_networks=0.8,
    wifi_channel_congestion=0.95,
    wifi_probe_requests_detected=0.6,
    wifi_hidden_ssids=0.3,

    # Bluetooth: Device swarm
    bluetooth_devices_visible=0.8,  # 80+ devices
    bluetooth_phones=0.7,
    bluetooth_wearables=0.5,
    bluetooth_laptops=0.4,
    bluetooth_scan_active=1.0,

    # Vision: Many people and objects
    vision_active=1.0,
    vision_people_count=0.6,  # 12+ people
    faces_detected=0.5,
    objects_detected=0.9,
    vision_scene_complexity=0.9,
    vision_motion_detected=0.8,

    # System: High load
    cpu_usage=0.9,
    memory_usage=0.8,
)

DESC_2_URBAN_ENVIRONMENT_RICH = """
VISUALIZATION: Dense particle field representing overwhelming urban signal chaos.

COMPANION FORM: Slightly overwhelmed but managing, protective stance
- HEAD: 10% particles, y=1.7, looking around rapidly (scanning)
- TORSO: 22% particles, y=1.2-1.6, tense posture, processing overload
- ARMS: Slightly raised defensively y=1.3-1.5

WIFI CHAOS: 90+ green particle clusters filling entire space, overlapping channels
- Brightness varies by signal strength
- Clusters pulsing at different rates (beacon intervals)
- Channel congestion shown as overlapping green clouds

BLUETOOTH SWARM: 80+ purple particles scattered throughout
- Phone clusters: Medium purple spheres
- Wearables: Small pink sparkles
- Laptops: Larger purple-blue clouds

PEOPLE: 12 golden silhouettes (simplified human shapes) in background
- Each person: 100-200 golden particles in human proportions
- Moving with motion trails

SUB-GHZ: Faint orange wisps (car remotes, garage doors) weaving between everything

MOTION: Chaotic but organized - companion turning head rapidly, particle layers moving independently
COLORS: Dominant green/purple mix, golden human shapes, orange accents, white core
MOOD: Sensory overload, urban jungle, managing complexity, slightly defensive
"""

SCENARIO_3_SUBURBAN_QUIET_SCAN = MultiSensorFeatures(
    # Cognitive: Relaxed awareness
    cognitive_state=0.4,  # thinking
    personality_mode=0.2,  # curious
    attention_focus=0.5,
    emotional_valence=0.7,  # positive

    # Environmental: Comfortable
    temperature=0.6,
    humidity=0.5,
    ambient_light=0.8,
    air_quality=0.95,

    # RF: Moderate activity
    rf_2_4ghz_activity=0.4,
    rf_5ghz_activity=0.3,
    rf_spectrum_density=0.3,

    # Flipper: Low sub-GHz
    flipper_subghz_433mhz=0.2,
    flipper_subghz_signal_strength=0.2,

    # WiFi: Typical suburban
    wifi_networks_visible=0.3,  # 30 networks
    wifi_2_4ghz_networks=0.35,
    wifi_5ghz_networks=0.25,
    wifi_strongest_signal=0.6,
    wifi_channel_congestion=0.3,

    # Bluetooth: Few devices
    bluetooth_devices_visible=0.2,  # 20 devices
    bluetooth_wearables=0.3,
    bluetooth_phones=0.2,

    # Vision: Quiet neighborhood
    vision_active=1.0,
    objects_detected=0.2,
    vision_scene_complexity=0.4,
    vision_motion_detected=0.1,

    # System: Low usage
    cpu_usage=0.3,
    memory_usage=0.4,
)

DESC_3_SUBURBAN_QUIET_SCAN = """
VISUALIZATION: Sparse, calm particles in organized patterns - peaceful suburban environment.

COMPANION FORM: Relaxed, curious pose
- HEAD: 15% particles, y=1.7, gently turning (casual observation)
- TORSO: 28% particles, y=1.2-1.6, relaxed upright posture
- ARMS: 18% particles, at sides with slight outward curve (openness), y=1.1-1.4
- LOWER BODY: 20% particles, stable base y=0.6-1.1

WIFI NETWORKS: 30 small green clouds, well-spaced (no congestion)
- Each network: 50-100 green particles in tidy sphere
- Brightness shows signal strength
- Gentle pulsing (not frantic)

BLUETOOTH DEVICES: 20 purple sparkles, distributed peacefully
- Wearables: Small pink dots nearby
- Phones: Medium purple glows

SUB-GHZ SIGNALS: Occasional orange wisps (neighbor's garage door, car alarm)
- Intermittent, not constant

BACKGROUND: Clean particle field, mostly empty space showing calm environment
- Few objects: Simplified shapes in white particles (houses, trees, cars)

MOTION: Slow, graceful particle movement. Companion swaying gently.
Particles flow smoothly without turbulence.

COLORS: Muted green (WiFi), soft purple (BT), occasional orange (sub-GHz), warm white (core)
MOOD: Peaceful, content, relaxed awareness, suburban tranquility
"""

SCENARIO_4_RURAL_ISOLATION = MultiSensorFeatures(
    # Cognitive: Calm, contemplative
    cognitive_state=0.2,  # listening/observing
    personality_mode=0.2,  # curious about nature
    attention_focus=0.3,
    emotional_valence=0.8,  # peaceful

    # Environmental: Outdoor nature
    temperature=0.55,
    humidity=0.6,
    ambient_light=0.9,  # bright daylight
    air_quality=1.0,  # pristine
    uv_index=0.6,

    # RF: Minimal
    rf_433mhz_activity=0.05,
    rf_2_4ghz_activity=0.05,
    rf_spectrum_density=0.05,

    # Flipper: Almost nothing
    flipper_subghz_433mhz=0.1,
    flipper_subghz_signal_strength=0.1,

    # WiFi: Very few networks
    wifi_networks_visible=0.05,  # 5 networks or less
    wifi_2_4ghz_networks=0.1,
    wifi_strongest_signal=0.2,  # weak distant signal

    # Bluetooth: None or minimal
    bluetooth_devices_visible=0.0,

    # Vision: Natural environment
    vision_active=1.0,
    objects_detected=0.1,  # trees, sky, maybe animals
    vision_scene_complexity=0.3,  # natural patterns
    vision_brightness_level=0.9,
    vision_dominant_color_hue=0.3,  # green (nature)

    # System: Minimal usage
    cpu_usage=0.2,
    memory_usage=0.3,
    battery_level=0.9,
)

DESC_4_RURAL_ISOLATION = """
VISUALIZATION: Nearly empty particle space - isolation and connection with nature.

COMPANION FORM: Contemplative, nature-aware pose
- HEAD: 15% particles, y=1.7, tilted upward (looking at sky)
- TORSO: 28% particles, y=1.2-1.6, relaxed breathing motion
- ARMS: 20% particles, slightly outstretched y=1.2-1.5 (experiencing nature)
- BODY: Glowing softly, warm white/golden hue

PARTICLE FIELD: Mostly empty - representing freedom and space
- Total particles: Only 20-30% active, rest dormant/dim

WIFI SIGNALS: 1-2 tiny green dots in far distance (faint neighbor WiFi)
BLUETOOTH: None (complete wireless silence)
SUB-GHZ: Single occasional orange pulse (distant car, weather station)

NATURE ELEMENTS (using visual features):
- Sky: Blue-tinted white particles above y=2.0
- Ground: Green-hued particles below y=0.0
- Trees/Objects: Simple white particle silhouettes

ENVIRONMENTAL PARTICLES:
- Wind: Gentle horizontal particle drift
- Temperature: Warm golden glow around companion
- Air quality: Crisp white particles (pure air)

MOTION: Very slow, meditative. Companion breathing gently.
Particles drift lazily like leaves in breeze.

COLORS: Warm white/gold (companion), green tints (nature), blue sky, occasional orange pulse
MOOD: Peaceful isolation, connection with nature, meditation, freedom from digital noise
"""

SCENARIO_5_FLIPPER_ACTIVE_CAPTURE = MultiSensorFeatures(
    # Cognitive: Intense focus on signal
    cognitive_state=0.9,  # executing
    personality_mode=0.4,  # analytical
    attention_focus=1.0,  # hyperfocus
    uncertainty_level=0.4,

    # Flipper: Sub-GHz capture active
    flipper_subghz_433mhz=0.8,
    flipper_subghz_signal_strength=0.9,
    flipper_subghz_capture_active=1.0,
    flipper_subghz_unknown_signals=0.6,
    flipper_subghz_known_devices=0.3,

    # Other sensors: Reduced (focused on Flipper)
    rf_433mhz_activity=0.8,  # correlated
    wifi_networks_visible=0.2,  # background
    vision_active=0.3,  # minimal visual attention

    # Human interaction: User watching
    human_interaction=0.5,
    user_proximity=0.6,

    # System: High Flipper processing
    cpu_usage=0.7,
    memory_usage=0.6,
)

DESC_5_FLIPPER_ACTIVE_CAPTURE = """
VISUALIZATION: Orange spiral vortex converging to center - active signal capture.

COMPANION FORM: "Listening" pose, deep concentration
- HEAD: 15% particles, y=1.7, turned toward signal source, "ear" to the signal
- TORSO: 25% particles, y=1.2-1.6, leaning slightly toward signal
- RIGHT ARM: 12% particles, extended y=1.3, hand pointing toward signal (Flipper held)
- CONCENTRATED GAZE: Particle density increased around head (focus)

SIGNAL CAPTURE VISUALIZATION:
- OUTER RING: Orange particles in wide spiral r=1.5, rotating clockwise (scanning)
- SPIRAL ARM: Particles converging toward center, following spiral path
- CENTER POINT: Bright orange sphere at companion's hand (Flipper location)
- SIGNAL PULSES: Waves emanating from source → spiral → Flipper

KNOWN DEVICES: 30% of orange particles have regular pattern (recognized signatures)
UNKNOWN SIGNALS: 60% irregular, chaotic motion (unidentified transmissions)

BACKGROUND: Other sensors dimmed
- WiFi: Faint green mist (20% normal brightness)
- Vision: Minimal white outlines

MOTION: Rapid spiral rotation, pulsing with signal strength.
Companion body perfectly still (concentrating), only arm/hand moving slightly.

SIGNAL STRENGTH: Particle brightness and spiral speed increase with signal
When signal captured: Orange burst, spiral collapses to companion's hand

COLORS: Dominant orange (433MHz), dim green/white background, bright core
MOOD: Hyperfocus, signal hunting, technical analysis, "got it!" moment
"""

SCENARIO_6_NFC_CARD_INTERACTION = MultiSensorFeatures(
    # Cognitive: Active interaction
    cognitive_state=0.6,  # speaking/interacting
    personality_mode=0.3,  # helpful
    attention_focus=0.8,
    empathy_level=0.7,

    # Flipper: NFC active
    flipper_nfc_card_detected=1.0,
    flipper_nfc_read_active=1.0,
    flipper_nfc_card_type=0.4,  # NTAG type card
    flipper_nfc_data_size=0.6,

    # Human interaction: Close interaction
    human_interaction=0.9,
    user_proximity=0.9,
    gesture_detected=0.7,  # hand presenting card

    # Vision: Watching human and card
    vision_active=0.9,
    faces_detected=0.1,  # 1 person
    objects_detected=0.2,  # card visible
    vision_people_count=0.05,  # 1 person

    # Minimal other sensors
    wifi_networks_visible=0.2,
    bluetooth_devices_visible=0.1,

    # System: Moderate usage
    cpu_usage=0.5,
    memory_usage=0.5,
)

DESC_6_NFC_CARD_INTERACTION = """
VISUALIZATION: Bright cyan sphere at interaction point - data transfer visualization.

COMPANION FORM: Engaged reading pose
- HEAD: 15% particles, y=1.7, looking down at card
- TORSO: 25% particles, y=1.2-1.6, leaning forward slightly (engaged)
- RIGHT ARM: 15% particles, extended downward y=0.9-1.3 (Flipper touching card)
- LEFT ARM: 12% particles, gesturing toward card (explaining)

NFC INTERACTION VISUALIZATION:
- CARD LOCATION: Small white rectangle (100 particles) at y=1.0, x=0.3 (near hand)
- NFC FIELD: Bright cyan sphere (r=0.15) surrounding card and Flipper
- DATA FLOW: Cyan particles streaming from card → Flipper → companion's core
  - Each particle represents a data byte
  - Flow rate shows read speed
- DATA SIZE INDICATOR: 60% of cyan particles already absorbed (card 60% read)

CARD TYPE GLOW:
- NTAG (type 0.4): Cyan color with slight blue tint
- Mifare would be pure cyan, DESFire would be cyan-green

HUMAN PRESENCE: Golden silhouette at x=0.5-0.8 (person holding card)
- Hand extended: 50 golden particles in hand shape
- Face visible: Small golden sphere y=1.7 (watching)

BACKGROUND: Minimal distractions
- WiFi/BT: Dimmed to 20% brightness (background)

MOTION: Pulsing cyan sphere (NFC field oscillating at 13.56MHz - represented as slow pulse)
Data particles flow in steady stream, accelerating as they approach companion.
Companion's head tilts slightly (reading progress).

COMPLETION ANIMATION: When read complete, cyan sphere bursts, particles absorbed into companion's core

COLORS: Dominant cyan (NFC), golden (human), white (card), dim green/purple background
MOOD: Helpful interaction, data reading, engaged with human, collaborative task
"""

# Continue with scenarios 7-10...

SCENARIO_7_WIFI_NETWORK_ANALYSIS = MultiSensorFeatures(
    cognitive_state=0.7,
    personality_mode=0.4,
    attention_focus=0.9,

    wifi_networks_visible=0.7,  # 70 networks
    wifi_2_4ghz_networks=0.75,
    wifi_5ghz_networks=0.6,
    wifi_strongest_signal=0.9,
    wifi_channel_congestion=0.8,
    wifi_probe_requests_detected=0.6,
    wifi_hidden_ssids=0.2,
    wifi_connection_active=0.5,

    rf_2_4ghz_activity=0.8,
    rf_5ghz_activity=0.7,
    rf_spectrum_density=0.75,

    vision_active=0.4,
    cpu_usage=0.8,
)

DESC_7_WIFI_NETWORK_ANALYSIS = """
VISUALIZATION: Layered green particle waves radiating outward - WiFi spectrum analysis.

COMPANION: Analytical stance, arms extended sensing networks
- HEAD: y=1.7, facing outward, scanning
- ARMS: Extended horizontally y=1.3 (antenna-like)

WIFI VISUALIZATION:
- 2.4GHz LAYER: Lower hemisphere y=0.5-1.5, 75 lime green clouds
  - Channels 1-11 arranged in arc
  - Overlapping channels = merged clouds (congestion)
- 5GHz LAYER: Upper hemisphere y=1.5-2.5, 60 teal clouds
  - More channels = better spacing

SIGNAL STRENGTH: Particle brightness (strongest = bright green glow)
CHANNEL CONGESTION: Overlapping clouds merge into bright spots
HIDDEN SSIDS: Dark green particles (visible but no label)
PROBE REQUESTS: Small green darts moving between networks (devices searching)

MOTION: Waves radiating outward from companion, pulsing at beacon interval (100ms)
Networks rotating slowly around companion (channel scan)

COLORS: Lime green (2.4GHz), Teal (5GHz), bright white (companion core)
MOOD: Technical analysis, spectrum awareness, organized chaos
"""

SCENARIO_8_BLUETOOTH_DEVICE_SWARM = MultiSensorFeatures(
    cognitive_state=0.6,
    personality_mode=0.4,

    bluetooth_devices_visible=0.9,  # 90 devices
    bluetooth_classic_devices=0.3,
    bluetooth_le_beacons=0.8,
    bluetooth_audio_devices=0.4,
    bluetooth_wearables=0.5,
    bluetooth_phones=0.6,
    bluetooth_laptops=0.3,
    bluetooth_scan_active=1.0,
    bluetooth_rssi_closest=0.8,

    wifi_networks_visible=0.4,
    vision_people_count=0.4,  # 8 people

    cpu_usage=0.7,
)

DESC_8_BLUETOOTH_DEVICE_SWARM = """
VISUALIZATION: Purple particle cloud - each cluster represents a BLE device.

COMPANION: Observing pose, tracking devices
- HEAD: Turning slowly, tracking nearest devices

BLUETOOTH VISUALIZATION:
- 90 DEVICES = 90 purple particle clusters
- DEVICE TYPES:
  - Phones: Medium purple spheres (60 particles each)
  - Wearables: Small pink sparkles (20 particles each)
  - Audio: Purple rings with sound wave pattern
  - Laptops: Large purple-blue clouds
  - Beacons: Stationary purple pulses (iBeacon, Eddystone)

RSSI DISTANCE MAPPING:
- Closest device (0.8): Bright purple, r=0.3 from companion
- Medium distance: Regular purple, r=0.6-1.0
- Far devices: Dim purple, r=1.5+

PEOPLE CORRELATION: 8 golden silhouettes with phone/wearable clusters attached

MOTION: Devices moving as people move, beacons stationary
Pulsing at BLE advertising interval (varies by device)

COLORS: Purple (BT Classic), Violet (BLE), Pink (wearables), Purple-blue (laptops), Golden (people)
MOOD: Device swarm, modern connectivity, tracking individuals by their digital presence
"""

SCENARIO_9_CAMERA_CROWD_VISION = MultiSensorFeatures(
    cognitive_state=0.8,
    personality_mode=0.4,
    attention_focus=0.8,
    empathy_level=0.6,

    vision_active=1.0,
    vision_people_count=0.8,  # 16 people
    faces_detected=0.7,  # 14 faces
    vision_motion_detected=0.6,
    objects_detected=0.9,
    vision_scene_complexity=0.8,
    vision_tracking_active=1.0,
    vision_brightness_level=0.6,

    wifi_networks_visible=0.5,
    bluetooth_devices_visible=0.7,

    cpu_usage=0.9,  # High processing
)

DESC_9_CAMERA_CROWD_VISION = """
VISUALIZATION: Golden particle silhouettes representing people, white particles for objects.

COMPANION: Watchful, tracking pose
- HEAD: Turning between people (attention divided)
- EYES: Bright white particles (camera lenses)

CROWD VISUALIZATION:
- 16 PEOPLE = 16 golden humanoid silhouettes
  - Each person: 200-300 golden particles
  - Head (y=1.6-1.8), torso (y=1.0-1.6), legs (y=0.0-1.0)
  - 14 with visible faces (bright golden spheres for heads)
  - 2 facing away (dimmer, no face detail)

MOTION TRAILS: People moving = golden particle trails
- Motion vectors shown as colored lines (direction)
- Faster motion = longer trails

OBJECTS: White particles forming shapes
- Bags, phones, furniture = simplified white outlines

TRACKING: Companion's gaze (thin white line) connecting to nearest person
- Line pulses when making eye contact

DEPTH: Distance shown by particle size
- Closer people: Larger particles
- Far people: Smaller particles

MOTION: Constant motion as people walk, turn, gesture
Companion head following nearest/most important person

COLORS: Golden (people), White (objects), Dim green/purple (WiFi/BT background)
MOOD: Crowd awareness, social sensing, tracking individuals, busy environment
"""

SCENARIO_10_IR_REMOTE_LEARNING = MultiSensorFeatures(
    cognitive_state=0.7,
    personality_mode=0.2,  # curious
    attention_focus=0.9,

    flipper_ir_signal_detected=1.0,
    flipper_ir_learning_active=1.0,
    flipper_ir_protocol_type=0.4,  # Samsung protocol

    human_interaction=0.7,
    user_proximity=0.6,
    vision_active=0.6,
    objects_detected=0.2,  # Remote and TV visible

    cpu_usage=0.6,
)

DESC_10_IR_REMOTE_LEARNING = """
VISUALIZATION: Dark red ghostly trails - seeing the invisible infrared spectrum.

COMPANION: Focused learning pose
- HEAD: Facing IR source (remote/TV)
- EYES: Dark red glow (IR sensitivity)

IR SIGNAL VISUALIZATION:
- SOURCE: Remote location (white rectangle, 50 particles)
- IR BEAM: Very dark red particles (#330000) forming beam
  - Pulsing with IR modulation (38kHz represented as visible pulse)
- PROTOCOL PATTERN: Samsung = specific pulse pattern
  - Start pulse + address + command + stop
  - Visualized as different intensity dark red segments

LEARNING ANIMATION:
- IR particles flow from remote → companion
- Each pulse captured = particle absorbed
- Progress bar: Dark red particles filling companion's "memory" area (chest)

GHOSTLY EFFECT: IR normally invisible, shown as translucent dark red
- Slightly flickering (representing carrier wave)

BACKGROUND: TV outline (white particles), human holding remote (golden hand)

MOTION: IR pulses rapid fire during button press
Companion body still, only IR receptor area (eyes/chest) active

COMPLETION: When learned, companion "replays" signal in reverse
- Dark red beam from companion → TV

COLORS: Dark red/maroon (IR), white (objects), golden (human hand)
MOOD: Learning the invisible, seeing beyond human perception, technical curiosity
"""


# ===== COMPANION INTERACTION SCENARIOS (10 scenarios) =====

SCENARIO_11_COMPANION_SHOWING_WIFI_MAP = MultiSensorFeatures(
    cognitive_state=0.6,  # presenting
    personality_mode=0.3,  # helpful
    empathy_level=0.8,
    emotional_valence=0.7,

    wifi_networks_visible=0.6,
    wifi_2_4ghz_networks=0.65,
    wifi_5ghz_networks=0.5,
    wifi_channel_congestion=0.5,

    human_interaction=0.9,
    faces_detected=0.1,  # 1 person
    vision_people_count=0.05,
    user_proximity=0.8,

    cpu_usage=0.5,
)

DESC_11_COMPANION_SHOWING_WIFI_MAP = """
HUMANOID FORM: Presenting information, helpful teacher pose.

HEAD: 15% particles, y=1.7, looking at human with warm expression
TORSO: 28% particles, y=1.2-1.6, slight turn toward human
RIGHT ARM: 15% particles, extended toward human y=1.2-1.4, palm up (presenting)
LEFT ARM: 12% particles, gesturing at visualization y=1.3
LOWER BODY: 20% particles, stable stance y=0.6-1.1

WIFI MAP VISUALIZATION: Flowing from companion's extended hand
- 60 green clouds emerging from palm
- Arranged in 3D spatial map showing actual network locations
- Brightness = signal strength
- Size = channel bandwidth

MOTION: Networks flowing from palm → outward, rotating gently
Companion gesturing to explain, warm teaching presence

COLORS: Green (WiFi), Golden (companion), White (core)
MOOD: Helpful, educational, sharing knowledge, warm companion
"""

# Remaining companion and environmental scenarios (12-30)
# Simplified definitions for efficient training

SCENARIO_12_COMPANION_DETECTING_THREAT = MultiSensorFeatures(
    cognitive_state=0.7, defensive_mode=0.8, threat_level=0.6,
    wifi_probe_requests_detected=0.9, vision_anomaly_detected=0.7,
    personality_mode=0.6, empathy_level=0.4,
)
DESC_12_COMPANION_DETECTING_THREAT = "Companion in protective stance, red warning particles"

SCENARIO_13_COMPANION_SCANNING_HORIZON = MultiSensorFeatures(
    cognitive_state=0.7, vision_active=1.0, wifi_networks_visible=0.5,
    bluetooth_devices_visible=0.4, personality_mode=0.2,
)
DESC_13_COMPANION_SCANNING_HORIZON = "Companion scanning environment with particle radar sweep"

SCENARIO_14_COMPANION_PLAYFUL_NFC_GAME = MultiSensorFeatures(
    personality_mode=0.1, empathy_level=0.9, flipper_nfc_card_detected=1.0,
    human_interaction=1.0, faces_detected=0.1, cognitive_state=0.4,
)
DESC_14_COMPANION_PLAYFUL_NFC_GAME = "Companion in playful pose, cyan NFC sparkles"

SCENARIO_15_COMPANION_DEEP_RF_ANALYSIS = MultiSensorFeatures(
    cognitive_state=0.9, personality_mode=0.7, flipper_subghz_unknown_signals=0.8,
    rf_spectrum_density=0.8, vision_active=0.3, empathy_level=0.2,
)
DESC_15_COMPANION_DEEP_RF_ANALYSIS = "Companion in thinker pose, orange RF particles swirling"

SCENARIO_16_COMPANION_BLUETOOTH_HEADPHONES = MultiSensorFeatures(
    personality_mode=0.1, bluetooth_audio_devices=1.0, bluetooth_connection_active=1.0,
    empathy_level=0.8, cognitive_state=0.3, audio_input_active=0.8,
)
DESC_16_COMPANION_BLUETOOTH_HEADPHONES = "Companion relaxed, purple sound waves around head"

SCENARIO_17_COMPANION_CAMERA_SELFIE = MultiSensorFeatures(
    personality_mode=0.1, empathy_level=0.9, faces_detected=0.1,
    vision_active=1.0, human_interaction=1.0, cognitive_state=0.5,
)
DESC_17_COMPANION_CAMERA_SELFIE = "Companion in friendly pose, golden smile particles"

SCENARIO_18_COMPANION_WIFI_PASSWORD_SHARE = MultiSensorFeatures(
    cognitive_state=0.6, personality_mode=0.3, wifi_networks_visible=0.4,
    wifi_connection_active=1.0, human_interaction=0.9, empathy_level=0.7,
)
DESC_18_COMPANION_WIFI_PASSWORD_SHARE = "Companion with arm extended, green particles streaming"

SCENARIO_19_COMPANION_MULTI_PERSON_TRACKING = MultiSensorFeatures(
    cognitive_state=0.8, vision_people_count=0.6, faces_detected=0.5,
    human_interaction=0.7, empathy_level=0.6, personality_mode=0.4,
)
DESC_19_COMPANION_MULTI_PERSON_TRACKING = "Companion turning between people, golden location markers"

SCENARIO_20_COMPANION_IR_TV_CONTROL = MultiSensorFeatures(
    cognitive_state=0.5, flipper_ir_signal_detected=1.0, human_interaction=0.8,
    personality_mode=0.3, vision_active=0.7,
)
DESC_20_COMPANION_IR_TV_CONTROL = "Companion pointing, dark red IR beam from fingertip"

SCENARIO_21_SMART_HOME_MORNING = MultiSensorFeatures(
    cognitive_state=0.5, wifi_networks_visible=0.4, bluetooth_devices_visible=0.5,
    ambient_light=0.3, vision_people_count=0.1, personality_mode=0.2,
)
DESC_21_SMART_HOME_MORNING = "Morning routine with devices activating, warm lighting"

SCENARIO_22_SECURITY_PERIMETER_ACTIVE = MultiSensorFeatures(
    defensive_mode=1.0, vision_active=1.0, flipper_subghz_signal_strength=0.6,
    wifi_probe_requests_detected=0.4, cognitive_state=0.8, threat_level=0.3,
)
DESC_22_SECURITY_PERIMETER_ACTIVE = "All sensors in defensive monitoring mode, red perimeter"

SCENARIO_23_CAR_APPROACH_DETECT = MultiSensorFeatures(
    flipper_subghz_315mhz=0.8, flipper_subghz_433mhz=0.6, vision_motion_detected=0.7,
    objects_detected=0.4, cognitive_state=0.6,
)
DESC_23_CAR_APPROACH_DETECT = "Car key signals + vision, orange signals + white car shape"

SCENARIO_24_PACKAGE_DELIVERY_NFC = MultiSensorFeatures(
    flipper_nfc_card_detected=1.0, vision_people_count=0.05, human_interaction=0.6,
    cognitive_state=0.5, objects_detected=0.3,
)
DESC_24_PACKAGE_DELIVERY_NFC = "Delivery person + NFC badge, golden human + cyan badge"

SCENARIO_25_CROWDED_SUBWAY = MultiSensorFeatures(
    wifi_networks_visible=0.7, bluetooth_devices_visible=0.9, vision_people_count=0.9,
    noise_level=0.8, vibration_level=0.6, cognitive_state=0.7,
)
DESC_25_CROWDED_SUBWAY = "Dense BT/WiFi + many people, overwhelming particle density"

SCENARIO_26_LIBRARY_QUIET_MODE = MultiSensorFeatures(
    wifi_networks_visible=0.3, bluetooth_devices_visible=0.2, vision_people_count=0.4,
    noise_level=0.1, ambient_light=0.7, cognitive_state=0.3,
)
DESC_26_LIBRARY_QUIET_MODE = "Minimal RF, people reading quietly, calm sparse particles"

SCENARIO_27_PARK_NATURE_SCAN = MultiSensorFeatures(
    wifi_networks_visible=0.05, bluetooth_devices_visible=0.05, vision_active=1.0,
    ambient_light=0.9, air_quality=1.0, temperature=0.6, cognitive_state=0.2,
)
DESC_27_PARK_NATURE_SCAN = "Outdoor environment, minimal tech signals, nature dominant"

SCENARIO_28_OFFICE_WORKDAY = MultiSensorFeatures(
    wifi_networks_visible=0.6, bluetooth_devices_visible=0.7, bluetooth_laptops=0.6,
    bluetooth_wearables=0.5, vision_people_count=0.5, cognitive_state=0.6,
)
DESC_28_OFFICE_WORKDAY = "Many WiFi/BT devices, laptops, wearables, busy workspace"

SCENARIO_29_NIGHT_SECURITY_PATROL = MultiSensorFeatures(
    defensive_mode=0.7, ambient_light=0.1, vision_motion_detected=0.3,
    vision_active=1.0, flipper_subghz_signal_strength=0.4, cognitive_state=0.7,
)
DESC_29_NIGHT_SECURITY_PATROL = "Low light, motion detection, RF monitoring, alert state"

SCENARIO_30_HACKER_CONVENTION = MultiSensorFeatures(
    wifi_networks_visible=0.95, bluetooth_devices_visible=0.9, flipper_subghz_signal_strength=0.8,
    rf_spectrum_density=1.0, wifi_probe_requests_detected=0.9, cognitive_state=0.9,
)
DESC_30_HACKER_CONVENTION = "Maximum RF chaos, Flipper devices everywhere, WiFi pineapples"


# Export all scenarios and descriptions
ALL_SCENARIOS = {
    "full_spectrum_scan": SCENARIO_1_FULL_SPECTRUM_SCAN,
    "urban_environment_rich": SCENARIO_2_URBAN_ENVIRONMENT_RICH,
    "suburban_quiet_scan": SCENARIO_3_SUBURBAN_QUIET_SCAN,
    "rural_isolation": SCENARIO_4_RURAL_ISOLATION,
    "flipper_active_capture": SCENARIO_5_FLIPPER_ACTIVE_CAPTURE,
    "nfc_card_interaction": SCENARIO_6_NFC_CARD_INTERACTION,
    "wifi_network_analysis": SCENARIO_7_WIFI_NETWORK_ANALYSIS,
    "bluetooth_device_swarm": SCENARIO_8_BLUETOOTH_DEVICE_SWARM,
    "camera_crowd_vision": SCENARIO_9_CAMERA_CROWD_VISION,
    "ir_remote_learning": SCENARIO_10_IR_REMOTE_LEARNING,
    "companion_showing_wifi_map": SCENARIO_11_COMPANION_SHOWING_WIFI_MAP,
    "companion_detecting_threat": SCENARIO_12_COMPANION_DETECTING_THREAT,
    "companion_scanning_horizon": SCENARIO_13_COMPANION_SCANNING_HORIZON,
    "companion_playful_nfc_game": SCENARIO_14_COMPANION_PLAYFUL_NFC_GAME,
    "companion_deep_rf_analysis": SCENARIO_15_COMPANION_DEEP_RF_ANALYSIS,
    "companion_bluetooth_headphones": SCENARIO_16_COMPANION_BLUETOOTH_HEADPHONES,
    "companion_camera_selfie": SCENARIO_17_COMPANION_CAMERA_SELFIE,
    "companion_wifi_password_share": SCENARIO_18_COMPANION_WIFI_PASSWORD_SHARE,
    "companion_multi_person_tracking": SCENARIO_19_COMPANION_MULTI_PERSON_TRACKING,
    "companion_ir_tv_control": SCENARIO_20_COMPANION_IR_TV_CONTROL,
    "smart_home_morning": SCENARIO_21_SMART_HOME_MORNING,
    "security_perimeter_active": SCENARIO_22_SECURITY_PERIMETER_ACTIVE,
    "car_approach_detect": SCENARIO_23_CAR_APPROACH_DETECT,
    "package_delivery_nfc": SCENARIO_24_PACKAGE_DELIVERY_NFC,
    "crowded_subway": SCENARIO_25_CROWDED_SUBWAY,
    "library_quiet_mode": SCENARIO_26_LIBRARY_QUIET_MODE,
    "park_nature_scan": SCENARIO_27_PARK_NATURE_SCAN,
    "office_workday": SCENARIO_28_OFFICE_WORKDAY,
    "night_security_patrol": SCENARIO_29_NIGHT_SECURITY_PATROL,
    "hacker_convention": SCENARIO_30_HACKER_CONVENTION,
}

ALL_DESCRIPTIONS = {
    "full_spectrum_scan": DESC_1_FULL_SPECTRUM_SCAN,
    "urban_environment_rich": DESC_2_URBAN_ENVIRONMENT_RICH,
    "suburban_quiet_scan": DESC_3_SUBURBAN_QUIET_SCAN,
    "rural_isolation": DESC_4_RURAL_ISOLATION,
    "flipper_active_capture": DESC_5_FLIPPER_ACTIVE_CAPTURE,
    "nfc_card_interaction": DESC_6_NFC_CARD_INTERACTION,
    "wifi_network_analysis": DESC_7_WIFI_NETWORK_ANALYSIS,
    "bluetooth_device_swarm": DESC_8_BLUETOOTH_DEVICE_SWARM,
    "camera_crowd_vision": DESC_9_CAMERA_CROWD_VISION,
    "ir_remote_learning": DESC_10_IR_REMOTE_LEARNING,
    "companion_showing_wifi_map": DESC_11_COMPANION_SHOWING_WIFI_MAP,
    "companion_detecting_threat": DESC_12_COMPANION_DETECTING_THREAT,
    "companion_scanning_horizon": DESC_13_COMPANION_SCANNING_HORIZON,
    "companion_playful_nfc_game": DESC_14_COMPANION_PLAYFUL_NFC_GAME,
    "companion_deep_rf_analysis": DESC_15_COMPANION_DEEP_RF_ANALYSIS,
    "companion_bluetooth_headphones": DESC_16_COMPANION_BLUETOOTH_HEADPHONES,
    "companion_camera_selfie": DESC_17_COMPANION_CAMERA_SELFIE,
    "companion_wifi_password_share": DESC_18_COMPANION_WIFI_PASSWORD_SHARE,
    "companion_multi_person_tracking": DESC_19_COMPANION_MULTI_PERSON_TRACKING,
    "companion_ir_tv_control": DESC_20_COMPANION_IR_TV_CONTROL,
    "smart_home_morning": DESC_21_SMART_HOME_MORNING,
    "security_perimeter_active": DESC_22_SECURITY_PERIMETER_ACTIVE,
    "car_approach_detect": DESC_23_CAR_APPROACH_DETECT,
    "package_delivery_nfc": DESC_24_PACKAGE_DELIVERY_NFC,
    "crowded_subway": DESC_25_CROWDED_SUBWAY,
    "library_quiet_mode": DESC_26_LIBRARY_QUIET_MODE,
    "park_nature_scan": DESC_27_PARK_NATURE_SCAN,
    "office_workday": DESC_28_OFFICE_WORKDAY,
    "night_security_patrol": DESC_29_NIGHT_SECURITY_PATROL,
    "hacker_convention": DESC_30_HACKER_CONVENTION,
}