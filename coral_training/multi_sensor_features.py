#!/usr/bin/env python3
"""
Multi-Sensor Feature Set - 120 Features
Complete environmental awareness for Sentient Core
"""

from dataclasses import dataclass, fields
from typing import Dict


@dataclass
class MultiSensorFeatures:
    """
    Complete 120-feature set for comprehensive peripheral integration.
    All values normalized to 0.0-1.0 range.
    """

    # ===== ORIGINAL 68 FEATURES =====

    # Cognitive State (8 features)
    cognitive_state: float = 0.0        # 0.0=idle, 0.2=listening, 0.4=thinking, 0.6=speaking, 0.8=executing, 1.0=learning
    personality_mode: float = 0.5       # 0.0=playful, 0.2=curious, 0.4=analytical, 0.6=defensive, 0.8=empathetic, 1.0=assertive
    emotional_valence: float = 0.5      # 0.0=negative, 0.5=neutral, 1.0=positive
    attention_focus: float = 0.5        # 0.0=unfocused, 1.0=hyperfocused
    uncertainty_level: float = 0.0      # 0.0=certain, 1.0=maximum uncertainty
    learning_rate: float = 0.0          # Current learning intensity
    memory_access: float = 0.0          # Accessing long-term memory
    empathy_level: float = 0.5          # Emotional awareness and response

    # Environmental Sensors (10 features)
    temperature: float = 0.5            # Normalized -10°C to 40°C
    humidity: float = 0.5               # 0% to 100%
    air_pressure: float = 0.5           # Normalized barometric pressure
    ambient_light: float = 0.5          # 0.0=dark, 1.0=bright
    uv_index: float = 0.0               # 0.0 to 1.0 (UV 0-11+)
    air_quality: float = 1.0            # 1.0=excellent, 0.0=hazardous
    motion_detected: float = 0.0        # Motion sensor activation
    proximity_sensor: float = 0.0       # Object proximity (0.0=far, 1.0=touching)
    magnetic_field: float = 0.5         # Magnetometer (deviation from baseline)
    vibration_level: float = 0.0        # Accelerometer vibration intensity

    # RF Spectrum Analysis (12 features)
    rf_433mhz_activity: float = 0.0     # 433MHz band activity
    rf_2_4ghz_activity: float = 0.0     # 2.4GHz WiFi/BT activity
    rf_5ghz_activity: float = 0.0       # 5GHz WiFi activity
    rf_known_devices: float = 0.0       # Recognized RF signatures
    rf_unknown_signals: float = 0.0     # Unidentified RF activity
    rf_signal_strength: float = 0.0     # Strongest RF signal
    rf_spectrum_density: float = 0.0    # Overall RF congestion
    rf_interference: float = 0.0        # Noise/interference level
    rf_jamming_detected: float = 0.0    # Potential jamming
    rf_scan_active: float = 0.0         # Actively scanning RF
    rf_directional_signal: float = 0.5  # Signal direction (if array available)
    rf_frequency_hopping: float = 0.0   # Frequency hopping detected

    # Visual Processing (10 features)
    vision_active: float = 0.0          # Camera/vision system active
    faces_detected: float = 0.0         # Number of faces (normalized 0-10+)
    objects_detected: float = 0.0       # Objects in frame
    motion_in_frame: float = 0.0        # Visual motion detection
    scene_brightness: float = 0.5       # Scene luminosity
    color_temperature: float = 0.5      # Warm (0.0) to Cool (1.0)
    depth_perception: float = 0.0       # Depth map available
    visual_complexity: float = 0.0      # Scene detail/edges
    text_detected: float = 0.0          # OCR text presence
    qr_code_detected: float = 0.0       # QR/barcode detected

    # Audio Processing (6 features)
    audio_input_active: float = 0.0     # Microphone active
    noise_level: float = 0.0            # Ambient noise
    voice_detected: float = 0.0         # Human voice present
    music_detected: float = 0.0         # Music playing
    audio_frequency_peak: float = 0.5   # Dominant frequency (normalized)
    speech_clarity: float = 0.0         # Voice clarity for STT

    # Human Interaction (7 features)
    human_interaction: float = 0.0      # Active human interaction
    gesture_detected: float = 0.0       # Hand gesture recognition
    touch_input: float = 0.0            # Touch sensor active
    voice_command: float = 0.0          # Voice command received
    button_press: float = 0.0           # Physical button interaction
    user_proximity: float = 0.0         # Human nearby
    conversation_active: float = 0.0    # Two-way conversation

    # Network Activity (6 features)
    network_connected: float = 0.0      # Internet connectivity
    network_bandwidth: float = 0.0      # Current bandwidth usage
    devices_on_network: float = 0.0     # Network device count
    mqtt_messages: float = 0.0          # MQTT activity level
    api_requests: float = 0.0           # API call frequency
    data_sync_active: float = 0.0       # Cloud sync in progress

    # System Resources (4 features)
    cpu_usage: float = 0.0              # CPU utilization
    memory_usage: float = 0.0           # RAM usage
    battery_level: float = 1.0          # Battery charge (1.0=full)
    thermal_state: float = 0.0          # Device temperature

    # Security/Defense (5 features)
    defensive_mode: float = 0.0         # Security posture
    threat_level: float = 0.0           # Perceived threat
    intrusion_detected: float = 0.0     # Security breach
    encryption_active: float = 1.0      # Data encryption status
    anomaly_score: float = 0.0          # Behavioral anomaly detection

    # ===== NEW: 52 PERIPHERAL FEATURES =====

    # Flipper Zero - Sub-GHz Radio (8 features)
    flipper_subghz_315mhz: float = 0.0          # 315MHz activity (garage doors, car keys)
    flipper_subghz_433mhz: float = 0.0          # 433MHz activity (weather stations, remotes)
    flipper_subghz_868mhz: float = 0.0          # 868MHz activity (EU smart home)
    flipper_subghz_915mhz: float = 0.0          # 915MHz activity (US smart home)
    flipper_subghz_signal_strength: float = 0.0 # Current signal strength
    flipper_subghz_known_devices: float = 0.0   # Recognized device signatures
    flipper_subghz_unknown_signals: float = 0.0 # Unidentified transmissions
    flipper_subghz_capture_active: float = 0.0  # Actively capturing signal

    # Flipper Zero - RFID/NFC (6 features)
    flipper_rfid_125khz_detected: float = 0.0   # Low-frequency RFID card present
    flipper_nfc_card_detected: float = 0.0      # NFC card/tag present
    flipper_nfc_card_type: float = 0.0          # Card type (0.0=none, 0.2=Mifare, 0.4=NTAG, etc.)
    flipper_nfc_read_active: float = 0.0        # Currently reading card
    flipper_nfc_emulation_active: float = 0.0   # Emulating a card
    flipper_nfc_data_size: float = 0.0          # Amount of data on card (normalized)

    # Flipper Zero - Infrared (3 features)
    flipper_ir_signal_detected: float = 0.0     # IR transmission detected
    flipper_ir_protocol_type: float = 0.0       # Protocol (0.0=none, 0.2=NEC, 0.4=Samsung, etc.)
    flipper_ir_learning_active: float = 0.0     # Learning new IR signal

    # Flipper Zero - GPIO/Hardware (3 features)
    flipper_gpio_active_pins: float = 0.0       # Number of active GPIO pins (normalized)
    flipper_ibutton_detected: float = 0.0       # iButton/Dallas key detected
    flipper_badusb_active: float = 0.0          # BadUSB script running

    # WiFi Scanning (12 features)
    wifi_networks_visible: float = 0.0          # Number of WiFi networks detected (normalized 0-100+)
    wifi_2_4ghz_networks: float = 0.0           # 2.4GHz network count
    wifi_5ghz_networks: float = 0.0             # 5GHz network count
    wifi_strongest_signal: float = 0.0          # Strongest RSSI (normalized -100dBm to -30dBm)
    wifi_weakest_signal: float = 0.0            # Weakest RSSI
    wifi_open_networks: float = 0.0             # Unsecured networks count
    wifi_wpa2_networks: float = 0.0             # WPA2 secured networks
    wifi_wpa3_networks: float = 0.0             # WPA3 secured networks
    wifi_hidden_ssids: float = 0.0              # Hidden network count
    wifi_channel_congestion: float = 0.0        # Channel overlap/congestion level
    wifi_connection_active: float = 0.0         # Currently connected to WiFi
    wifi_probe_requests_detected: float = 0.0   # Nearby device probes (wardriving)

    # Bluetooth Scanning (10 features)
    bluetooth_devices_visible: float = 0.0      # BLE devices detected
    bluetooth_classic_devices: float = 0.0      # Classic Bluetooth devices
    bluetooth_le_beacons: float = 0.0           # BLE beacon count (iBeacon, Eddystone)
    bluetooth_audio_devices: float = 0.0        # Audio devices (headphones, speakers)
    bluetooth_wearables: float = 0.0            # Fitness trackers, smartwatches
    bluetooth_phones: float = 0.0               # Mobile phones detected
    bluetooth_laptops: float = 0.0              # Laptops/computers
    bluetooth_rssi_closest: float = 0.0         # Closest device signal strength
    bluetooth_connection_active: float = 0.0    # Currently connected devices
    bluetooth_scan_active: float = 0.0          # Active scanning mode

    # Enhanced Computer Vision (10 features)
    vision_people_count: float = 0.0            # Number of people detected (normalized 0-20+)
    vision_faces_count: float = 0.0             # Face detection count
    vision_motion_detected: float = 0.0         # Motion in frame (0.0-1.0)
    vision_motion_direction: float = 0.5        # Primary motion vector (0.0=still, 0.25=left, 0.5=right, etc.)
    vision_brightness_level: float = 0.5        # Scene brightness
    vision_dominant_color_hue: float = 0.5      # Dominant color (HSV hue 0.0-1.0)
    vision_scene_complexity: float = 0.0        # Edge density/detail level
    vision_depth_estimate: float = 0.0          # Estimated depth of scene
    vision_anomaly_detected: float = 0.0        # Unusual objects/patterns
    vision_tracking_active: float = 0.0         # Object tracking engaged

    def to_array(self):
        """Convert features to numpy-compatible list in consistent order."""
        return [getattr(self, field.name) for field in fields(self)]

    @classmethod
    def feature_names(cls):
        """Return ordered list of all 120 feature names."""
        return [field.name for field in fields(cls)]

    @classmethod
    def num_features(cls):
        """Return total feature count (120)."""
        return len(fields(cls))

    def __post_init__(self):
        """Validate all features are in 0.0-1.0 range."""
        for field in fields(self):
            value = getattr(self, field.name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{field.name} must be in range [0.0, 1.0], got {value}")


# Convenience function for creating scenarios
def create_scenario(name: str, **kwargs) -> Dict[str, MultiSensorFeatures]:
    """Create a named scenario with specified feature values."""
    return {name: MultiSensorFeatures(**kwargs)}


if __name__ == "__main__":
    # Test feature dataclass
    features = MultiSensorFeatures()
    print(f"Total features: {MultiSensorFeatures.num_features()}")
    print(f"Feature vector length: {len(features.to_array())}")
    print(f"\nFirst 10 features: {MultiSensorFeatures.feature_names()[:10]}")
    print(f"Last 10 features: {MultiSensorFeatures.feature_names()[-10:]}")

    # Test scenario creation
    test_scenario = create_scenario(
        "test",
        cognitive_state=0.8,
        wifi_networks_visible=0.5,
        vision_people_count=0.3,
        flipper_nfc_card_detected=1.0
    )
    print(f"\nTest scenario features: {test_scenario['test'].to_array()[:5]}...")
