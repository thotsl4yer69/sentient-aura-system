# Multi-Sensor Visualization Design
## Sentient Core - Complete Environmental Awareness

### Design Philosophy
Transform ALL sensor inputs from Flipper Zero, WiFi, Bluetooth, camera, and environmental sensors into a unified particle visualization that represents "everything in the world" around the AI companion.

---

## Expanded Feature Set: 120 Features

### Original 68 Features (PRESERVED)
- 8 Cognitive State
- 10 Environmental Sensors
- 12 RF Spectrum
- 10 Visual Processing
- 6 Audio Processing
- 7 Human Interaction
- 6 Network Activity
- 4 System Resources
- 5 Security/Defense

### NEW: 52 Additional Peripheral Features

#### Flipper Zero Features (20 features)
**Sub-GHz Radio (8 features):**
1. `flipper_subghz_315mhz` - 315MHz activity (garage doors, car keys)
2. `flipper_subghz_433mhz` - 433MHz activity (weather stations, remotes)
3. `flipper_subghz_868mhz` - 868MHz activity (EU smart home)
4. `flipper_subghz_915mhz` - 915MHz activity (US smart home)
5. `flipper_subghz_signal_strength` - Current signal strength (0.0-1.0)
6. `flipper_subghz_known_devices` - Recognized device signatures
7. `flipper_subghz_unknown_signals` - Unidentified transmissions
8. `flipper_subghz_capture_active` - Actively capturing signal

**RFID/NFC (6 features):**
9. `flipper_rfid_125khz_detected` - Low-frequency RFID card present
10. `flipper_nfc_card_detected` - NFC card/tag present (Mifare, NTAG, etc.)
11. `flipper_nfc_card_type` - Card type (0.0=none, 0.2=Mifare, 0.4=NTAG, etc.)
12. `flipper_nfc_read_active` - Currently reading card
13. `flipper_nfc_emulation_active` - Emulating a card
14. `flipper_nfc_data_size` - Amount of data on card (normalized)

**Infrared (3 features):**
15. `flipper_ir_signal_detected` - IR transmission detected
16. `flipper_ir_protocol_type` - Protocol (0.0=none, 0.2=NEC, 0.4=Samsung, 0.6=Sony, etc.)
17. `flipper_ir_learning_active` - Learning new IR signal

**GPIO/Hardware (3 features):**
18. `flipper_gpio_active_pins` - Number of active GPIO pins (normalized)
19. `flipper_ibutton_detected` - iButton/Dallas key detected
20. `flipper_badusb_active` - BadUSB script running

#### WiFi Scanning Features (12 features)
21. `wifi_networks_visible` - Number of WiFi networks detected (normalized 0.0-1.0)
22. `wifi_2_4ghz_networks` - 2.4GHz network count
23. `wifi_5ghz_networks` - 5GHz network count
24. `wifi_strongest_signal` - Strongest RSSI (normalized -100dBm to -30dBm)
25. `wifi_weakest_signal` - Weakest RSSI
26. `wifi_open_networks` - Unsecured networks count
27. `wifi_wpa2_networks` - WPA2 secured networks
28. `wifi_wpa3_networks` - WPA3 secured networks
29. `wifi_hidden_ssids` - Hidden network count
30. `wifi_channel_congestion` - Channel overlap/congestion level
31. `wifi_devices_connected` - Devices connected to our network
32. `wifi_probe_requests_detected` - Nearby device probes

#### Bluetooth Features (10 features)
33. `bluetooth_devices_visible` - BLE devices detected
34. `bluetooth_classic_devices` - Classic Bluetooth devices
35. `bluetooth_le_beacons` - BLE beacon count (iBeacon, Eddystone)
36. `bluetooth_audio_devices` - Audio devices (headphones, speakers)
37. `bluetooth_wearables` - Fitness trackers, smartwatches
38. `bluetooth_phones` - Mobile phones detected
39. `bluetooth_laptops` - Laptops/computers
40. `bluetooth_rssi_closest` - Closest device signal strength
41. `bluetooth_connection_active` - Currently connected devices
42. `bluetooth_scan_active` - Active scanning mode

#### Computer Vision Features (10 features)
43. `vision_objects_detected` - Total objects in frame
44. `vision_people_count` - Number of people detected
45. `vision_faces_detected` - Face detection count
46. `vision_motion_detected` - Motion in frame (0.0-1.0)
47. `vision_motion_direction` - Primary motion vector (0.0=still, 0.25=left, 0.5=right, 0.75=up, 1.0=down)
48. `vision_brightness_level` - Scene brightness
49. `vision_dominant_color_hue` - Dominant color (HSV hue 0.0-1.0)
50. `vision_scene_complexity` - Edge density/detail level
51. `vision_depth_estimate` - Estimated depth of scene
52. `vision_anomaly_detected` - Unusual objects/patterns

---

## Visualization Mapping Strategy

### Particle Color Encoding by Sensor Type

**Flipper Sub-GHz Signals** → **Orange/Red Spectrum**
- 315MHz: Deep Orange (#FF6600)
- 433MHz: Bright Orange (#FF9933)
- 868MHz: Red-Orange (#FF4500)
- 915MHz: Red (#FF0000)
- Signal strength controls particle brightness and trail length

**RFID/NFC** → **Electric Blue/Cyan**
- 125kHz RFID: Deep Blue (#0066FF)
- NFC: Bright Cyan (#00FFFF)
- Reading: Pulsing cyan particles
- Emulation: Stable cyan glow

**WiFi Networks** → **Green Spectrum**
- 2.4GHz: Lime Green (#00FF00)
- 5GHz: Teal (#00CC99)
- Signal strength: Particle density
- Security level: Brightness (dim=open, bright=WPA3)

**Bluetooth** → **Purple/Magenta**
- BLE: Violet (#8800FF)
- Classic BT: Magenta (#FF00FF)
- Audio devices: Deep purple with sound waves
- Wearables: Pink sparkles (#FF66FF)

**Infrared** → **Dark Red (Invisible Spectrum)**
- IR signals: Very dark red (#330000) with ghostly trails
- Protocol type affects particle pattern

**Camera Vision** → **White/Gold (Human Perception)**
- People: Golden particles (#FFD700)
- Objects: White (#FFFFFF)
- Motion: Particle velocity and trails
- Faces: Concentrated golden sphere (like head in companion mode)

**Environmental** → **Earth Tones**
- Temperature: Red (hot) to Blue (cold)
- Humidity: Blue-grey mist
- Pressure: Density of particles

---

## Multi-Sensor Fusion Scenarios

### 30 New Training Scenarios

#### Active Scanning Mode (10 scenarios)

**1. `full_spectrum_scan`** - All sensors active simultaneously
```python
RichFeatures(
    cognitive_state=0.8,  # high processing
    flipper_subghz_signal_strength=0.6,
    flipper_nfc_card_detected=0.0,
    wifi_networks_visible=0.5,  # 50+ networks
    bluetooth_devices_visible=0.4,  # 20+ devices
    vision_objects_detected=0.3,
    rf_spectrum_density=0.8,
)
```
**Visualization**: Multi-colored swirling vortex, all frequencies represented, rapid particle movement

**2. `urban_environment_rich`** - Dense city signals
```python
RichFeatures(
    wifi_networks_visible=0.9,  # 100+ networks
    bluetooth_devices_visible=0.8,  # 80+ devices
    flipper_subghz_433mhz=0.4,
    vision_people_count=0.6,  # 6+ people
    wifi_channel_congestion=0.9,
    noise_level=0.7,
)
```
**Visualization**: Dense particle field, layered colors, chaotic but organized patterns

**3. `suburban_quiet_scan`** - Moderate signal environment
```python
RichFeatures(
    wifi_networks_visible=0.3,  # 20-30 networks
    bluetooth_devices_visible=0.2,
    flipper_subghz_signal_strength=0.2,
    vision_objects_detected=0.2,
    ambient_light=0.6,
)
```
**Visualization**: Sparse, calm particles, gentle movements, muted colors

**4. `rural_isolation`** - Minimal signals
```python
RichFeatures(
    wifi_networks_visible=0.05,  # 1-2 networks
    bluetooth_devices_visible=0.0,
    flipper_subghz_signal_strength=0.1,
    vision_objects_detected=0.1,
    ambient_light=0.8,
)
```
**Visualization**: Nearly empty space, few bright particles, natural environmental colors

**5. `flipper_active_capture`** - Focused sub-GHz analysis
```python
RichFeatures(
    cognitive_state=0.9,  # intense focus
    flipper_subghz_capture_active=1.0,
    flipper_subghz_433mhz=0.8,
    flipper_subghz_signal_strength=0.9,
    flipper_subghz_unknown_signals=0.6,
    vision_active=0.3,  # reduced other senses
)
```
**Visualization**: Orange spiral converging to center, pulsing with signal strength, companion "listening" pose

**6. `nfc_card_interaction`** - RFID/NFC reading
```python
RichFeatures(
    flipper_nfc_card_detected=1.0,
    flipper_nfc_read_active=1.0,
    flipper_nfc_card_type=0.4,  # NTAG
    flipper_nfc_data_size=0.6,
    human_interaction=0.8,
    vision_active=0.9,
)
```
**Visualization**: Bright cyan sphere at interaction point, particles flowing from card to companion, reading gesture

**7. `wifi_network_analysis`** - Deep WiFi scanning
```python
RichFeatures(
    wifi_networks_visible=0.7,
    wifi_scan_active=1.0,
    wifi_strongest_signal=0.9,
    wifi_channel_congestion=0.8,
    wifi_probe_requests_detected=0.6,
    cognitive_state=0.7,
)
```
**Visualization**: Green particle waves radiating outward, layered by channel, strength shown by brightness

**8. `bluetooth_device_swarm`** - Many BLE devices
```python
RichFeatures(
    bluetooth_devices_visible=0.9,
    bluetooth_le_beacons=0.8,
    bluetooth_wearables=0.5,
    bluetooth_phones=0.6,
    bluetooth_scan_active=1.0,
)
```
**Visualization**: Purple particle cloud, each cluster represents a device, pulsing with RSSI

**9. `camera_crowd_vision`** - Visual processing of people
```python
RichFeatures(
    vision_people_count=0.8,  # 8+ people
    vision_faces_detected=0.7,
    vision_motion_detected=0.6,
    vision_objects_detected=0.9,
    vision_scene_complexity=0.8,
    cognitive_state=0.8,
)
```
**Visualization**: Golden particles forming human silhouettes, white particles for objects, motion trails

**10. `ir_remote_learning`** - Infrared capture
```python
RichFeatures(
    flipper_ir_signal_detected=1.0,
    flipper_ir_learning_active=1.0,
    flipper_ir_protocol_type=0.4,  # Samsung
    human_interaction=0.7,
    vision_active=0.6,
)
```
**Visualization**: Dark red ghostly trails, companion "seeing the invisible," focused attention pose

#### Companion Interaction Scenarios (10 scenarios)

**11. `companion_showing_wifi_map`** - Presenting network visualization
```python
RichFeatures(
    cognitive_state=0.6,  # presenting
    personality_mode=0.3,  # helpful
    wifi_networks_visible=0.6,
    vision_active=1.0,
    human_interaction=0.9,
    faces_detected=0.2,
)
```
**Visualization**: Companion humanoid form with one arm extended, green particles flowing from hand showing WiFi networks

**12. `companion_detecting_threat`** - Security alert
```python
RichFeatures(
    defensive_mode=0.8,
    threat_level=0.6,
    wifi_probe_requests_detected=0.9,  # wardriving attempt
    vision_anomaly_detected=0.7,
    personality_mode=0.6,  # protective
    empathy_level=0.4,
)
```
**Visualization**: Companion in protective stance, red warning particles around perimeter, alert posture

**13. `companion_scanning_horizon`** - Environmental survey
```python
RichFeatures(
    cognitive_state=0.7,
    vision_active=1.0,
    flipper_subghz_signal_strength=0.5,
    wifi_networks_visible=0.5,
    bluetooth_devices_visible=0.4,
    personality_mode=0.2,  # curious
)
```
**Visualization**: Companion with head turned, particle radar sweep pattern emanating from head

**14. `companion_playful_nfc_game`** - Playful interaction with NFC
```python
RichFeatures(
    personality_mode=0.1,  # playful
    empathy_level=0.9,
    flipper_nfc_card_detected=1.0,
    human_interaction=1.0,
    vision_faces_detected=0.2,
    cognitive_state=0.4,
)
```
**Visualization**: Companion in playful pose, cyan sparkles around hands, joyful energy

**15. `companion_deep_rf_analysis`** - Analytical pose
```python
RichFeatures(
    cognitive_state=0.9,  # deep thought
    personality_mode=0.7,  # analytical
    flipper_subghz_unknown_signals=0.8,
    rf_spectrum_density=0.8,
    vision_active=0.3,
    empathy_level=0.2,
)
```
**Visualization**: Companion in thinker pose, orange RF particles swirling around head, contemplative

**16. `companion_bluetooth_headphones`** - Listening to music
```python
RichFeatures(
    personality_mode=0.1,  # relaxed/playful
    bluetooth_audio_devices=1.0,
    bluetooth_connection_active=1.0,
    empathy_level=0.8,
    cognitive_state=0.3,
    audio_input_active=0.8,
)
```
**Visualization**: Companion in relaxed pose, purple sound waves around head, gentle sway motion

**17. `companion_camera_selfie`** - Aware of being photographed
```python
RichFeatures(
    personality_mode=0.1,  # playful
    empathy_level=0.9,
    vision_faces_detected=0.2,
    vision_active=1.0,
    human_interaction=1.0,
    cognitive_state=0.5,
)
```
**Visualization**: Companion in friendly pose, golden particles forming smile, warm welcoming energy

**18. `companion_wifi_password_share`** - Sharing network credentials
```python
RichFeatures(
    cognitive_state=0.6,
    personality_mode=0.3,  # helpful
    wifi_networks_visible=0.4,
    wifi_connection_active=1.0,
    human_interaction=0.9,
    empathy_level=0.7,
)
```
**Visualization**: Companion with arm extended, green particles streaming toward human, giving gesture

**19. `companion_multi_person_tracking`** - Aware of multiple people
```python
RichFeatures(
    cognitive_state=0.8,
    vision_people_count=0.6,  # 6+ people
    vision_faces_detected=0.5,
    human_interaction=0.7,
    empathy_level=0.6,
    personality_mode=0.4,  # attentive
)
```
**Visualization**: Companion turning between people, golden particles indicating each person's location

**20. `companion_ir_tv_control`** - Controlling TV with IR
```python
RichFeatures(
    cognitive_state=0.5,
    flipper_ir_signal_detected=1.0,
    human_interaction=0.8,
    personality_mode=0.3,  # helpful
    vision_active=0.7,
)
```
**Visualization**: Companion pointing at TV, dark red beam extending from fingertip

#### Environmental Fusion Scenarios (10 scenarios)

**21. `smart_home_morning`** - Morning routine with all devices active
**22. `security_perimeter_active`** - All sensors in defensive monitoring
**23. `car_approach_detect`** - 315/433MHz car key signals + vision
**24. `package_delivery_nfc`** - Delivery person + NFC badge scan
**25. `crowded_subway`** - Dense BT/WiFi + many people in vision
**26. `library_quiet_mode`** - Minimal RF, vision detecting people reading
**27. `park_nature_scan`** - Outdoor environment, minimal tech signals
**28. `office_workday`** - Many WiFi, BT devices, laptops, wearables
**29. `night_security_patrol`** - Low light, motion detection, RF monitoring
**30. `hacker_convention`** - Maximum RF chaos, Flipper devices, WiFi pineapples

---

## Integration Architecture

### Data Flow
```
[Flipper Zero] → Serial/USB → Feature Extractor
[ESP32 WiFi]   → MQTT       → Feature Extractor
[BT Scanner]   → D-Bus      → Feature Extractor  → [120-feature vector] → Edge TPU Model → [10,000 particles × RGB]
[Camera]       → OpenCV     → Feature Extractor
[Sensors]      → I2C/GPIO   → Feature Extractor
```

### Feature Extractor (Python Service)
- Reads all peripheral inputs
- Normalizes to 0.0-1.0 range
- Produces 120-dimensional feature vector at 30 Hz
- Feeds to Edge TPU inference

### Rendering Engine
- Receives particle positions from Edge TPU
- Maps particle colors based on feature values
- Applies motion smoothing and trails
- Renders at 60+ FPS

---

## Next Steps

1. **Expand training dataset** - Generate all 30 new scenarios
2. **Retrain model** - 120 input features → 128 → 30,000 output
3. **Test size** - Ensure model stays under 6 MB
4. **Hardware integration** - Connect Flipper Zero, WiFi scanner, camera
5. **Enhanced rendering** - Color mapping and particle effects

---

## Expected Performance
- Edge TPU Inference: 200+ FPS (same as before, more expressive output)
- Total latency: <30ms (sensor read → inference → render)
- Model size: ~4-5 MB (still fits in Edge TPU cache)
