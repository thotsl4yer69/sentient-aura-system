#!/usr/bin/env python3
"""
Sentient Core Cognitive Integration
====================================

This module extends the Coral visualization daemon with:
1. Automatic personality state determination from sensor data
2. Cognitive engine integration for personality-driven particle behavior
3. WebSocket communication for personality state and sensor data
4. User text input handling for GUI interaction

This bridges the gap between the AI backend and the visual frontend.
"""

import logging
import time
import json
from typing import Dict, Optional
import numpy as np

# Import cognitive engine
from sentient_aura.cognitive_engine import CognitiveEngine, COGNITIVE_PROFILES

logger = logging.getLogger("cognitive_integration")


class PersonalityStateDetector:
    """
    Determines appropriate personality state from sensor data and system state.

    Uses heuristics to map sensor inputs to the 40 companion personality states.
    """

    def __init__(self):
        self.logger = logging.getLogger("personality_detector")
        self.last_state = "idle_standing"
        self.state_duration = 0.0
        self.last_update_time = time.time()

    def determine_state(self, world_state_snapshot: Dict) -> str:
        """
        Analyze world state and determine appropriate personality state.

        Args:
            world_state_snapshot: Current world state data

        Returns:
            One of 40 personality state names (e.g., "analyzing_data", "greeting_human")
        """
        now = time.time()
        dt = now - self.last_update_time
        self.last_update_time = now
        self.state_duration += dt

        # Extract sensor data
        wifi_data = world_state_snapshot.get('wifi_scanner', {})
        bt_data = world_state_snapshot.get('bluetooth_scanner', {})
        audio_data = world_state_snapshot.get('audio', {})
        imu_data = world_state_snapshot.get('imu', {})
        vision_data = world_state_snapshot.get('vision', {})

        # Count active sensors
        wifi_networks = len(wifi_data.get('networks', []))
        bt_devices = len(bt_data.get('devices', []))
        audio_amplitude = audio_data.get('amplitude', 0.0)
        motion_detected = imu_data.get('motion_detected', False)
        objects_detected = len(vision_data.get('objects', []))

        # === PRIORITY 1: ALERT STATES (highest priority) ===

        # Threat detection
        if vision_data.get('drone_detected', False):
            return "alert_drone_detected"

        # Unknown person detected
        if vision_data.get('person_detected', False) and vision_data.get('face_unknown', False):
            return "alert_unknown_person"

        # === PRIORITY 2: INTERACTION STATES ===

        # Human conversation (audio input + known person)
        if audio_amplitude > 0.05 and audio_data.get('speech_detected', False):
            if vision_data.get('person_detected', False) and vision_data.get('face_known', False):
                return "engaged_conversation"
            else:
                return "listening"

        # Greeting (person just detected)
        if vision_data.get('person_detected', False) and self.state_duration < 3.0:
            return "greeting_human"

        # Acknowledging presence
        if vision_data.get('person_detected', False):
            return "acknowledging_presence"

        # === PRIORITY 3: ANALYSIS STATES ===

        # Analyzing network traffic (high WiFi + Bluetooth activity)
        if wifi_networks > 5 and bt_devices > 3:
            return "monitoring_network"

        # Processing data (moderate sensor activity)
        if wifi_networks > 0 or bt_devices > 0 or motion_detected:
            return "analyzing_data"

        # === PRIORITY 4: IDLE STATES (default) ===

        # If nothing happening for a while, vary idle animations
        if self.state_duration > 30:
            # Cycle through idle states every 30 seconds
            idle_states = ["idle_standing", "thoughtful_pose", "observing_environment"]
            idx = int((now % 90) / 30)  # Cycle through 3 states over 90 seconds
            return idle_states[idx]

        # Default: awaiting command
        return "awaiting_command"

    def get_state_metadata(self, state_name: str) -> Dict:
        """
        Get metadata about the current personality state.

        Args:
            state_name: Personality state name

        Returns:
            Dictionary with state information
        """
        if state_name not in COGNITIVE_PROFILES:
            self.logger.warning(f"Unknown personality state: {state_name}")
            state_name = "idle_standing"

        profile = COGNITIVE_PROFILES[state_name]

        return {
            "state": state_name,
            "duration": self.state_duration,
            "profile": {
                "cohesion": profile.cohesion,
                "separation": profile.separation,
                "alignment": profile.alignment,
                "wander": profile.wander,
                "breath_rate": profile.breath_rate,
                "breath_depth": profile.breath_depth,
                "glow_intensity": profile.glow_intensity,
                "particle_speed": profile.particle_speed,
                "color_shift": profile.color_shift
            }
        }


class CognitiveIntegrationMixin:
    """
    Mixin class to add cognitive capabilities to CoralVisualizationDaemon.

    Add this to the daemon's inheritance chain to enable personality-driven behavior.
    """

    def initialize_cognitive_engine(self):
        """
        Initialize cognitive engine and personality detector.

        Call this from the daemon's initialize() method.
        """
        self.logger.info("Initializing Cognitive Integration...")

        # Create cognitive engine
        self.cognitive_engine = CognitiveEngine()

        # Create personality state detector
        self.personality_detector = PersonalityStateDetector()

        # Track cognitive state
        self.current_personality_state = "idle_standing"
        self.last_personality_update = time.time()

        self.logger.info("✓ Cognitive Integration initialized")
        self.logger.info(f"  • {len(COGNITIVE_PROFILES)} personality states available")

    def update_cognitive_state(self):
        """
        Update cognitive state based on current world state.

        Call this at the start of each update cycle.
        """
        # Get world state snapshot
        if hasattr(self.world_state, 'get_snapshot'):
            snapshot = self.world_state.get_snapshot()
        else:
            # Fallback: collect data manually
            snapshot = {
                'wifi_scanner': self.world_state.get('wifi_scanner', {}),
                'bluetooth_scanner': self.world_state.get('bluetooth_scanner', {}),
                'audio': self.world_state.get('audio', {}),
                'imu': self.world_state.get('imu', {}),
                'vision': self.world_state.get('vision', {})
            }

        # Determine new personality state
        new_state = self.personality_detector.determine_state(snapshot)

        # Update cognitive engine if state changed
        if new_state != self.current_personality_state:
            self.logger.info(f"Personality state changed: {self.current_personality_state} → {new_state}")
            self.cognitive_engine.update_state(new_state, transition_time=1.0)
            self.current_personality_state = new_state
            self.last_personality_update = time.time()

        # Update cognitive engine timer
        now = time.time()
        dt = now - self.last_personality_update
        self.cognitive_engine.update(dt)

    def broadcast_cognitive_state(self):
        """
        Send current cognitive state to WebSocket clients.

        Call this after updating particles but before broadcasting.
        """
        if not hasattr(self, 'websocket_server') or self.websocket_server is None:
            return

        # Get current cognitive profile
        profile = self.cognitive_engine.get_current_profile()
        breathing_factor = self.cognitive_engine.get_breathing_factor()

        # Create cognitive state message
        cognitive_message = {
            "type": "cognitive_state",
            "timestamp": time.time(),
            "state": {
                "name": self.current_personality_state,
                "duration": self.personality_detector.state_duration,
                "transition_progress": self.cognitive_engine.transition_progress
            },
            "profile": {
                "cohesion": profile.cohesion,
                "separation": profile.separation,
                "alignment": profile.alignment,
                "wander": profile.wander,
                "breath_rate": profile.breath_rate,
                "breath_depth": profile.breath_depth,
                "glow_intensity": profile.glow_intensity,
                "particle_speed": profile.particle_speed,
                "color_shift": profile.color_shift,
                "breathing_factor": breathing_factor
            }
        }

        # Send as JSON (small payload)
        self.websocket_server.broadcast(json.dumps(cognitive_message))

    def broadcast_sensor_data(self):
        """
        Send current sensor data to WebSocket clients.

        Call this periodically (e.g., every 1-2 seconds) to update the GUI.
        """
        if not hasattr(self, 'websocket_server') or self.websocket_server is None:
            return

        # Collect sensor data from world state
        wifi_data = self.world_state.get('wifi_scanner', {})
        bt_data = self.world_state.get('bluetooth_scanner', {})
        audio_data = self.world_state.get('audio', {})
        imu_data = self.world_state.get('imu', {})

        # Create sensor data message
        sensor_message = {
            "type": "sensor_data",
            "timestamp": time.time(),
            "sensors": {
                "wifi": {
                    "available": wifi_data.get('available', False),
                    "network_count": len(wifi_data.get('networks', [])),
                    "networks": [
                        {
                            "ssid": net.get('ssid', 'Unknown'),
                            "signal": net.get('signal_strength', 0),
                            "frequency": net.get('frequency', 0),
                            "security": net.get('security', 'Unknown')
                        }
                        for net in wifi_data.get('networks', [])[:10]  # Limit to 10
                    ]
                },
                "bluetooth": {
                    "available": bt_data.get('available', False),
                    "device_count": len(bt_data.get('devices', [])),
                    "devices": [
                        {
                            "name": dev.get('name', 'Unknown'),
                            "rssi": dev.get('rssi', -999),
                            "type": dev.get('type', 'unknown')
                        }
                        for dev in bt_data.get('devices', [])[:10]  # Limit to 10
                    ]
                },
                "audio": {
                    "available": audio_data.get('available', False),
                    "amplitude": audio_data.get('amplitude', 0.0),
                    "speech_detected": audio_data.get('speech_detected', False),
                    "music_detected": audio_data.get('music_detected', False)
                },
                "imu": {
                    "available": imu_data.get('available', False),
                    "motion_detected": imu_data.get('motion_detected', False),
                    "heading": imu_data.get('euler', {}).get('heading', 0.0)
                }
            }
        }

        # Send as JSON
        self.websocket_server.broadcast(json.dumps(sensor_message))


# === TESTING ===

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 70)
    print("COGNITIVE INTEGRATION TEST")
    print("=" * 70)

    # Test personality detector
    detector = PersonalityStateDetector()

    test_scenarios = [
        {
            "name": "Idle system",
            "data": {}
        },
        {
            "name": "Person detected",
            "data": {
                "vision": {"person_detected": True, "face_known": True}
            }
        },
        {
            "name": "Speech detected",
            "data": {
                "audio": {"amplitude": 0.1, "speech_detected": True},
                "vision": {"person_detected": True, "face_known": True}
            }
        },
        {
            "name": "Drone detected",
            "data": {
                "vision": {"drone_detected": True}
            }
        },
        {
            "name": "High network activity",
            "data": {
                "wifi_scanner": {"networks": [{}] * 10},
                "bluetooth_scanner": {"devices": [{}] * 5}
            }
        }
    ]

    print("\nTesting personality state detection:\n")
    for scenario in test_scenarios:
        state = detector.determine_state(scenario["data"])
        print(f"  {scenario['name']:30s} → {state}")

    print("\n" + "=" * 70)
    print("✓ Cognitive integration test complete")
    print("=" * 70 + "\n")
