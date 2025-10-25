#!/usr/bin/env python3
"""
Complete Multi-Sensor Dataset Generator
Generates training dataset with all 60 scenarios:
- 30 multi-sensor fusion scenarios (120 features)
- 30 original companion scenarios (120 features, mapped from 68)

This creates the ultimate training set for comprehensive environmental awareness.
"""

import numpy as np
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, List, Tuple

# Import feature definitions
from multi_sensor_features import MultiSensorFeatures
import multi_sensor_scenarios as ms_scenarios

# Import original companion scenarios (we'll adapt them to 120 features)
from companion_scenarios import COMPANION_SCENARIOS, COMPANION_DESCRIPTIONS


def map_68_to_120_features(old_features) -> MultiSensorFeatures:
    """
    Map original 68-feature scenarios to new 120-feature format.
    Preserves all original values, sets new peripheral features based on context.
    Uses getattr with defaults to handle RichFeatures fields that may differ.
    """
    # Extract original features with safe defaults
    old_dict = {
        'cognitive_state': getattr(old_features, 'cognitive_state', 0.0),
        'personality_mode': getattr(old_features, 'personality_mode', 0.5),
        'emotional_valence': 0.5,  # RichFeatures doesn't have this, default neutral
        'attention_focus': getattr(old_features, 'attention_focus', 0.5),
        'uncertainty_level': getattr(old_features, 'uncertainty_level', 0.0),
        'learning_rate': getattr(old_features, 'learning_active', 0.0),
        'memory_access': getattr(old_features, 'memory_access_depth', 0.0),
        'empathy_level': getattr(old_features, 'empathy_level', 0.5),

        'temperature': getattr(old_features, 'temperature', 0.5),
        'humidity': getattr(old_features, 'humidity', 0.5),
        'air_pressure': getattr(old_features, 'atmospheric_pressure', 0.5),
        'ambient_light': getattr(old_features, 'light_level', 0.5),
        'uv_index': 0.0,  # Not in RichFeatures
        'air_quality': getattr(old_features, 'air_quality', 1.0),
        'motion_detected': getattr(old_features, 'motion_detected', 0.0),
        'proximity_sensor': getattr(old_features, 'proximity_human', 0.0),
        'magnetic_field': 0.5,  # Not in RichFeatures
        'vibration_level': 0.0,  # Not in RichFeatures

        'rf_433mhz_activity': getattr(old_features, 'rf_433mhz_activity', 0.0),
        'rf_2_4ghz_activity': getattr(old_features, 'rf_2_4ghz_activity', 0.0),
        'rf_5ghz_activity': getattr(old_features, 'rf_5ghz_activity', 0.0),
        'rf_known_devices': getattr(old_features, 'rf_known_devices', 0.0),
        'rf_unknown_signals': getattr(old_features, 'rf_unknown_signals', 0.0),
        'rf_signal_strength': getattr(old_features, 'rf_signal_diversity', 0.0),
        'rf_spectrum_density': getattr(old_features, 'rf_spectrum_density', 0.0),
        'rf_interference': 0.0,  # Not in RichFeatures
        'rf_jamming_detected': getattr(old_features, 'rf_jamming_detected', 0.0),
        'rf_scan_active': getattr(old_features, 'rf_scanner_active', 0.0),
        'rf_directional_signal': 0.5,  # Not in RichFeatures
        'rf_frequency_hopping': 0.0,  # Not in RichFeatures

        'vision_active': getattr(old_features, 'vision_active', 0.0),
        'faces_detected': getattr(old_features, 'faces_detected', 0.0),
        'objects_detected': getattr(old_features, 'objects_detected', 0.0),
        'motion_in_frame': getattr(old_features, 'motion_intensity', 0.0),
        'scene_brightness': getattr(old_features, 'scene_brightness', 0.5),
        'color_temperature': getattr(old_features, 'dominant_color_hue', 0.5),
        'depth_perception': 0.0,  # Not in RichFeatures
        'visual_complexity': getattr(old_features, 'scene_complexity', 0.0),
        'text_detected': 0.0,  # Not in RichFeatures
        'qr_code_detected': 0.0,  # Not in RichFeatures

        'audio_input_active': getattr(old_features, 'audio_active', 0.0),
        'noise_level': getattr(old_features, 'ambient_sound_level', 0.0),
        'voice_detected': getattr(old_features, 'speech_detected', 0.0),
        'music_detected': 0.0,  # Not in RichFeatures
        'audio_frequency_peak': 0.5,  # Derived from audio_frequency_low/mid/high
        'speech_clarity': getattr(old_features, 'speech_clarity', 0.0),

        'human_interaction': getattr(old_features, 'human_interaction', 0.0),
        'gesture_detected': 0.0,  # Not in RichFeatures
        'touch_input': 0.0,  # Not in RichFeatures
        'voice_command': getattr(old_features, 'speech_detected', 0.0),
        'button_press': 0.0,  # Not in RichFeatures
        'user_proximity': getattr(old_features, 'proximity_human', 0.0),
        'conversation_active': getattr(old_features, 'communication_intent', 0.0),

        'network_connected': getattr(old_features, 'network_connected', 0.0),
        'network_bandwidth': getattr(old_features, 'network_activity', 0.0),
        'devices_on_network': 0.0,  # Not in RichFeatures
        'mqtt_messages': 0.0,  # Not in RichFeatures
        'api_requests': getattr(old_features, 'external_api_active', 0.0),
        'data_sync_active': getattr(old_features, 'data_streaming', 0.0),

        'cpu_usage': getattr(old_features, 'cpu_usage', 0.0),
        'memory_usage': getattr(old_features, 'memory_usage', 0.0),
        'battery_level': 1.0,  # Not in RichFeatures
        'thermal_state': getattr(old_features, 'thermal_state', 0.0),

        'defensive_mode': getattr(old_features, 'defensive_mode', 0.0),
        'threat_level': getattr(old_features, 'threat_level', 0.0),
        'intrusion_detected': getattr(old_features, 'intrusion_attempts', 0.0),
        'encryption_active': 1.0,  # Default secure
        'anomaly_score': getattr(old_features, 'anomaly_detected', 0.0),
    }

    # Infer new peripheral features based on existing RF/vision/network data
    # Flipper Sub-GHz: Map from existing RF features
    old_dict['flipper_subghz_433mhz'] = old_dict['rf_433mhz_activity']
    old_dict['flipper_subghz_signal_strength'] = old_dict['rf_signal_strength']
    old_dict['flipper_subghz_known_devices'] = old_dict['rf_known_devices'] * 0.5
    old_dict['flipper_subghz_unknown_signals'] = old_dict['rf_unknown_signals'] * 0.5
    old_dict['flipper_subghz_capture_active'] = old_dict['rf_scan_active'] * 0.7

    # WiFi: Map from existing 2.4GHz/5GHz + network features
    old_dict['wifi_networks_visible'] = (old_dict['rf_2_4ghz_activity'] + old_dict['rf_5ghz_activity']) * 0.5
    old_dict['wifi_2_4ghz_networks'] = old_dict['rf_2_4ghz_activity']
    old_dict['wifi_5ghz_networks'] = old_dict['rf_5ghz_activity']
    old_dict['wifi_strongest_signal'] = old_dict['rf_signal_strength']
    old_dict['wifi_channel_congestion'] = old_dict['rf_spectrum_density']
    old_dict['wifi_connection_active'] = old_dict['network_connected']
    old_dict['wifi_probe_requests_detected'] = old_dict['rf_unknown_signals'] * 0.3

    # Bluetooth: Estimate from RF 2.4GHz activity
    bt_estimate = old_dict['rf_2_4ghz_activity'] * 0.6
    old_dict['bluetooth_devices_visible'] = bt_estimate
    old_dict['bluetooth_scan_active'] = old_dict['rf_scan_active'] * 0.5
    old_dict['bluetooth_phones'] = bt_estimate * 0.4
    old_dict['bluetooth_wearables'] = bt_estimate * 0.3

    # Enhanced vision: Map from existing vision features
    old_dict['vision_people_count'] = old_dict['faces_detected']
    old_dict['vision_faces_count'] = old_dict['faces_detected']
    old_dict['vision_motion_detected'] = old_dict['motion_in_frame']
    old_dict['vision_brightness_level'] = old_dict['scene_brightness']
    old_dict['vision_scene_complexity'] = old_dict['visual_complexity']
    old_dict['vision_tracking_active'] = old_dict['vision_active'] * old_dict['attention_focus']

    return MultiSensorFeatures(**old_dict)


def parse_multi_sensor_description(description: str, features: MultiSensorFeatures, num_particles: int = 10000) -> np.ndarray:
    """
    Parse multi-sensor visualization description into particle positions.
    Extends the original humanoid parsing with multi-sensor-specific patterns.
    """
    positions = np.zeros((num_particles, 3), dtype=np.float32)
    idx = 0

    # Core humanoid form (30% of particles for companion scenarios)
    is_companion = "HUMANOID FORM" in description or "COMPANION" in description

    if is_companion:
        # HEAD (15% particles)
        n_head = int(num_particles * 0.15)
        head_y = 1.7
        head_radius = 0.12
        for i in range(n_head):
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.pi)
            r = np.random.uniform(0, head_radius)
            x = r * np.sin(phi) * np.cos(theta)
            y = head_y + r * np.sin(phi) * np.sin(theta) * 0.5
            z = r * np.cos(phi)
            positions[idx] = [x, y, z]
            idx += 1

        # TORSO (25% particles)
        n_torso = int(num_particles * 0.25)
        for i in range(n_torso):
            theta = np.random.uniform(0, 2 * np.pi)
            y = np.random.uniform(1.2, 1.6)
            r = np.random.uniform(0, 0.15) * (1.8 - y)  # Narrower at top
            x = r * np.cos(theta)
            z = r * np.sin(theta)
            positions[idx] = [x, y, z]
            idx += 1

        # ARMS (20% particles total, 10% each)
        n_arms = int(num_particles * 0.20)
        for i in range(n_arms):
            # Randomize left or right
            side = 1 if i < n_arms // 2 else -1
            t = (i % (n_arms // 2)) / (n_arms // 2)
            x = side * (0.15 + t * 0.25)  # Extend outward
            y = 1.4 - t * 0.3  # Angled downward
            z = np.random.uniform(-0.05, 0.05)
            positions[idx] = [x, y, z]
            idx += 1

        # LOWER BODY (10% particles)
        n_lower = int(num_particles * 0.10)
        for i in range(n_lower):
            theta = np.random.uniform(0, 2 * np.pi)
            y = np.random.uniform(0.6, 1.1)
            r = np.random.uniform(0, 0.12)
            x = r * np.cos(theta)
            z = r * np.sin(theta)
            positions[idx] = [x, y, z]
            idx += 1

    # Sensor visualizations (remaining particles)
    remaining = num_particles - idx

    # WiFi networks (green clouds)
    wifi_count = int(features.wifi_networks_visible * 100)  # 0-100 networks
    if wifi_count > 0 and "WiFi" in description or "WIFI" in description:
        particles_per_network = min(50, remaining // wifi_count if wifi_count > 0 else 50)
        n_wifi = min(remaining, wifi_count * particles_per_network)

        for i in range(n_wifi):
            network_idx = i // particles_per_network
            # Arrange networks in 3D space around companion
            theta = (network_idx / wifi_count) * 2 * np.pi
            phi = np.random.uniform(0, np.pi)
            r = np.random.uniform(0.6, 1.2)

            # Add some randomness for cloud effect
            x = r * np.sin(phi) * np.cos(theta) + np.random.normal(0, 0.05)
            y = 1.0 + r * np.cos(phi) + np.random.normal(0, 0.05)
            z = r * np.sin(phi) * np.sin(theta) + np.random.normal(0, 0.05)

            if idx < num_particles:
                positions[idx] = [x, y, z]
                idx += 1

    # Bluetooth devices (purple sparkles)
    bt_count = int(features.bluetooth_devices_visible * 100)
    if bt_count > 0 and "Bluetooth" in description or "BLUETOOTH" in description:
        particles_per_device = min(30, (num_particles - idx) // bt_count if bt_count > 0 else 30)
        n_bt = min(num_particles - idx, bt_count * particles_per_device)

        for i in range(n_bt):
            # Scatter in 3D space
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.pi)
            r = np.random.uniform(0.4, 1.0)

            x = r * np.sin(phi) * np.cos(theta)
            y = 1.0 + r * np.cos(phi) * 0.5
            z = r * np.sin(phi) * np.sin(theta)

            if idx < num_particles:
                positions[idx] = [x, y, z]
                idx += 1

    # Flipper Sub-GHz signals (orange spiral/vortex)
    if features.flipper_subghz_signal_strength > 0.3 and ("FLIPPER" in description or "Sub-GHz" in description or "ORANGE" in description.upper()):
        n_subghz = min(num_particles - idx, int(features.flipper_subghz_signal_strength * 1500))

        for i in range(n_subghz):
            # Spiral pattern
            t = i / n_subghz
            theta = t * 6 * np.pi  # 3 rotations
            r = 0.3 + t * 0.8  # Expanding spiral

            x = r * np.cos(theta)
            y = 1.3 + np.random.normal(0, 0.1)
            z = r * np.sin(theta)

            if idx < num_particles:
                positions[idx] = [x, y, z]
                idx += 1

    # NFC interaction (cyan sphere)
    if features.flipper_nfc_card_detected > 0.5 and ("NFC" in description or "CYAN" in description.upper()):
        n_nfc = min(num_particles - idx, 800)
        nfc_center = [0.3, 1.0, 0.0]  # Card location
        nfc_radius = 0.15

        for i in range(n_nfc):
            theta = np.random.uniform(0, 2 * np.pi)
            phi = np.random.uniform(0, np.pi)
            r = np.random.uniform(0, nfc_radius)

            x = nfc_center[0] + r * np.sin(phi) * np.cos(theta)
            y = nfc_center[1] + r * np.cos(phi)
            z = nfc_center[2] + r * np.sin(phi) * np.sin(theta)

            if idx < num_particles:
                positions[idx] = [x, y, z]
                idx += 1

    # People/faces (golden silhouettes)
    people_count = int(features.vision_people_count * 20)  # 0-20 people
    if people_count > 0 and ("PEOPLE" in description or "CROWD" in description or "GOLDEN" in description.upper()):
        particles_per_person = min(200, (num_particles - idx) // people_count if people_count > 0 else 200)

        for person_idx in range(people_count):
            # Arrange people in background
            theta = (person_idx / people_count) * 2 * np.pi
            distance = np.random.uniform(0.8, 1.5)
            person_x = distance * np.cos(theta)
            person_z = distance * np.sin(theta)

            # Simple human silhouette
            for i in range(particles_per_person):
                # Head
                if i < particles_per_person * 0.15:
                    y = 1.6 + np.random.uniform(-0.1, 0.1)
                    x = person_x + np.random.uniform(-0.08, 0.08)
                    z = person_z + np.random.uniform(-0.08, 0.08)
                # Torso
                elif i < particles_per_person * 0.45:
                    y = np.random.uniform(1.0, 1.5)
                    x = person_x + np.random.uniform(-0.12, 0.12)
                    z = person_z + np.random.uniform(-0.08, 0.08)
                # Legs
                else:
                    y = np.random.uniform(0.0, 1.0)
                    x = person_x + np.random.uniform(-0.1, 0.1)
                    z = person_z + np.random.uniform(-0.08, 0.08)

                if idx < num_particles:
                    positions[idx] = [x, y, z]
                    idx += 1

    # Fill remaining with ambient particles (environmental)
    while idx < num_particles:
        # Random ambient particles in larger sphere
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.random.uniform(0, np.pi)
        r = np.random.uniform(0.5, 2.0)

        x = r * np.sin(phi) * np.cos(theta)
        y = 1.0 + r * np.cos(phi)
        z = r * np.sin(phi) * np.sin(theta)

        positions[idx] = [x, y, z]
        idx += 1

    return positions


def generate_complete_dataset(output_dir: Path, num_particles: int = 10000):
    """
    Generate complete 60-scenario dataset with 120 features.
    """
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Collect all scenarios
    all_scenarios = {}

    # 1. Multi-sensor scenarios (30 scenarios with 120 features)
    print("Loading multi-sensor scenarios...")
    ms_scenario_dict = {}
    for attr_name in dir(ms_scenarios):
        if attr_name.startswith('SCENARIO_'):
            scenario_obj = getattr(ms_scenarios, attr_name)
            if isinstance(scenario_obj, MultiSensorFeatures):
                # Get corresponding description
                desc_name = attr_name.replace('SCENARIO_', 'DESC_')
                description = getattr(ms_scenarios, desc_name, "")

                # Generate scenario name
                scenario_num = attr_name.split('_')[1]
                scenario_name = f"multi_sensor_{scenario_num}"

                ms_scenario_dict[scenario_name] = (scenario_obj, description)

    print(f"Loaded {len(ms_scenario_dict)} multi-sensor scenarios")

    # 2. Original companion scenarios (30 scenarios, mapped to 120 features)
    print("Loading and mapping original companion scenarios...")
    companion_mapped = {}
    for scenario_name, old_features in COMPANION_SCENARIOS.items():
        new_features = map_68_to_120_features(old_features)
        description = COMPANION_DESCRIPTIONS.get(scenario_name, "")
        companion_mapped[f"companion_{scenario_name}"] = (new_features, description)

    print(f"Mapped {len(companion_mapped)} companion scenarios to 120 features")

    # Combine all scenarios
    all_scenarios.update(ms_scenario_dict)
    all_scenarios.update(companion_mapped)

    num_scenarios = len(all_scenarios)
    num_features = 120

    print(f"\nGenerating complete dataset:")
    print(f"  Total scenarios: {num_scenarios}")
    print(f"  Features per scenario: {num_features}")
    print(f"  Particles per scenario: {num_particles}")
    print(f"  Particle dimensions: 3 (x, y, z)")

    # Initialize arrays
    inputs = np.zeros((num_scenarios, num_features), dtype=np.float32)
    outputs = np.zeros((num_scenarios, num_particles, 3), dtype=np.float32)
    scenario_names = []

    # Generate data for each scenario
    print("\nGenerating particle visualizations...")
    for idx, (scenario_name, (features, description)) in enumerate(all_scenarios.items()):
        print(f"  [{idx+1}/{num_scenarios}] {scenario_name}")

        # Input features
        inputs[idx] = features.to_array()

        # Output particle positions
        outputs[idx] = parse_multi_sensor_description(description, features, num_particles)

        scenario_names.append(scenario_name)

    # Save dataset
    input_file = output_dir / f"inputs_complete_{timestamp}.npy"
    output_file = output_dir / f"outputs_complete_{timestamp}.npy"
    metadata_file = output_dir / f"metadata_complete_{timestamp}.json"

    np.save(input_file, inputs)
    np.save(output_file, outputs)

    metadata = {
        "timestamp": timestamp,
        "num_scenarios": num_scenarios,
        "num_features": num_features,
        "num_particles": num_particles,
        "scenario_names": scenario_names,
        "input_shape": list(inputs.shape),
        "output_shape": list(outputs.shape),
        "description": "Complete 60-scenario dataset: 30 multi-sensor + 30 companion (all 120 features)",
        "multi_sensor_count": len(ms_scenario_dict),
        "companion_count": len(companion_mapped),
        "feature_names": MultiSensorFeatures.feature_names(),
    }

    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Dataset generated successfully!")
    print(f"  Input features: {input_file}")
    print(f"  Output particles: {output_file}")
    print(f"  Metadata: {metadata_file}")
    print(f"\n  Input shape: {inputs.shape}")
    print(f"  Output shape: {outputs.shape}")

    return inputs, outputs, metadata


if __name__ == "__main__":
    dataset_dir = Path(__file__).parent / 'dataset'
    generate_complete_dataset(dataset_dir)
