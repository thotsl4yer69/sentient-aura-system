#!/usr/bin/env python3
"""
Cognitive Engine - Bridges Personality States to Particle Motion
================================================

Maps 40 companion personality states to particle behavior profiles.
Creates the "nervous system" that makes particles breathe, pulse, and flow
in patterns that mirror consciousness itself.

This is where the visualization becomes SENTIENT.
"""

import numpy as np
from dataclasses import dataclass
from typing import Tuple, Dict, Optional, List
import time


@dataclass
class CognitiveProfile:
    """
    Defines particle behavior for a cognitive state.

    Each profile controls how particles move, cluster, and respond to stimuli.
    These parameters create the visual "personality" of the AI.
    """
    state_name: str

    # Particle motion parameters (0-1 normalized)
    cohesion: float = 0.5      # How strongly particles attract to center
    separation: float = 0.3    # How strongly particles repel each other
    alignment: float = 0.4     # How much particles align their velocities
    wander: float = 0.2        # Random motion factor

    # Breathing parameters (makes visualization feel alive)
    breath_rate: float = 1.0   # Breaths per second
    breath_depth: float = 0.3  # Expansion/contraction amount (0-1)

    # Visual parameters
    glow_intensity: float = 0.7
    particle_speed: float = 1.0
    color_shift: Tuple[float, float, float] = (0, 0, 0)  # RGB adjustment (-1 to 1)

    # Sensor response weights
    wifi_response: float = 0.5
    bluetooth_response: float = 0.5
    audio_response: float = 0.5


# === COGNITIVE PROFILES FOR ALL 40 COMPANION STATES ===

COGNITIVE_PROFILES = {
    # === IDLE STATES ===
    "idle_standing": CognitiveProfile(
        "idle_standing",
        cohesion=0.3, separation=0.5, alignment=0.2, wander=0.4,
        breath_rate=0.5, breath_depth=0.2,
        glow_intensity=0.4, particle_speed=0.3,
        color_shift=(0, 0, 0.1)  # Slight blue calm
    ),

    "thoughtful_pose": CognitiveProfile(
        "thoughtful_pose",
        cohesion=0.6, separation=0.3, alignment=0.7, wander=0.2,
        breath_rate=0.7, breath_depth=0.3,
        glow_intensity=0.6, particle_speed=0.5,
        color_shift=(0.1, 0, 0.2)  # Purple contemplation
    ),

    "awaiting_command": CognitiveProfile(
        "awaiting_command",
        cohesion=0.5, separation=0.4, alignment=0.5, wander=0.3,
        breath_rate=1.0, breath_depth=0.25,
        glow_intensity=0.7, particle_speed=0.6,
        color_shift=(0, 0.1, 0.1)  # Cyan readiness
    ),

    # === INTERACTION STATES ===
    "greeting_human": CognitiveProfile(
        "greeting_human",
        cohesion=0.4, separation=0.6, alignment=0.3, wander=0.5,
        breath_rate=1.5, breath_depth=0.5,
        glow_intensity=0.9, particle_speed=1.2,
        color_shift=(0.2, 0.2, 0)  # Warm yellow greeting
    ),

    "acknowledging_presence": CognitiveProfile(
        "acknowledging_presence",
        cohesion=0.5, separation=0.4, alignment=0.4, wander=0.3,
        breath_rate=1.2, breath_depth=0.3,
        glow_intensity=0.8, particle_speed=0.9
    ),

    "engaged_conversation": CognitiveProfile(
        "engaged_conversation",
        cohesion=0.6, separation=0.3, alignment=0.6, wander=0.4,
        breath_rate=1.8, breath_depth=0.4,
        glow_intensity=0.85, particle_speed=1.5,
        audio_response=1.0  # Highly responsive to voice
    ),

    "listening_intently": CognitiveProfile(
        "listening_intently",
        cohesion=0.7, separation=0.2, alignment=0.8, wander=0.1,
        breath_rate=0.8, breath_depth=0.2,
        glow_intensity=0.75, particle_speed=0.7,
        audio_response=0.9
    ),

    # === COGNITIVE STATES ===
    "analyzing_data": CognitiveProfile(
        "analyzing_data",
        cohesion=0.8, separation=0.2, alignment=0.9, wander=0.1,
        breath_rate=2.0, breath_depth=0.5,
        glow_intensity=1.0, particle_speed=2.5,
        color_shift=(0, 0.3, 0.5)  # Intense cyan processing
    ),

    "processing_request": CognitiveProfile(
        "processing_request",
        cohesion=0.7, separation=0.3, alignment=0.8, wander=0.2,
        breath_rate=2.2, breath_depth=0.6,
        glow_intensity=0.95, particle_speed=2.0
    ),

    "calculating": CognitiveProfile(
        "calculating",
        cohesion=0.85, separation=0.15, alignment=0.95, wander=0.05,
        breath_rate=2.5, breath_depth=0.4,
        glow_intensity=1.0, particle_speed=3.0,
        color_shift=(0, 0.4, 0.6)  # Bright cyan computation
    ),

    "reasoning": CognitiveProfile(
        "reasoning",
        cohesion=0.75, separation=0.25, alignment=0.85, wander=0.15,
        breath_rate=1.5, breath_depth=0.45,
        glow_intensity=0.9, particle_speed=1.8,
        color_shift=(0.2, 0, 0.3)  # Purple logic
    ),

    # === EMOTIONAL STATES ===
    "excited_discovery": CognitiveProfile(
        "excited_discovery",
        cohesion=0.1, separation=0.9, alignment=0.3, wander=0.8,
        breath_rate=3.0, breath_depth=0.8,
        glow_intensity=1.0, particle_speed=4.0,
        color_shift=(0.5, 0.3, 0)  # Golden excitement
    ),

    "curious_investigation": CognitiveProfile(
        "curious_investigation",
        cohesion=0.4, separation=0.5, alignment=0.4, wander=0.7,
        breath_rate=1.8, breath_depth=0.5,
        glow_intensity=0.85, particle_speed=2.2,
        color_shift=(0.1, 0.3, 0.2)  # Green curiosity
    ),

    "concerned_attention": CognitiveProfile(
        "concerned_attention",
        cohesion=0.8, separation=0.2, alignment=0.7, wander=0.2,
        breath_rate=1.3, breath_depth=0.35,
        glow_intensity=0.8, particle_speed=1.1,
        color_shift=(0.4, 0.2, 0)  # Orange concern
    ),

    "empathetic_response": CognitiveProfile(
        "empathetic_response",
        cohesion=0.6, separation=0.3, alignment=0.6, wander=0.3,
        breath_rate=1.0, breath_depth=0.4,
        glow_intensity=0.75, particle_speed=0.8,
        color_shift=(0.2, 0, 0.3)  # Soft purple empathy
    ),

    # === ALERT STATES ===
    "protective_stance": CognitiveProfile(
        "protective_stance",
        cohesion=0.95, separation=0.1, alignment=0.95, wander=0.05,
        breath_rate=1.5, breath_depth=0.4,
        glow_intensity=0.9, particle_speed=1.8,
        color_shift=(0.5, 0, 0)  # Red alert
    ),

    "scanning_environment": CognitiveProfile(
        "scanning_environment",
        cohesion=0.5, separation=0.4, alignment=0.5, wander=0.5,
        breath_rate=1.8, breath_depth=0.4,
        glow_intensity=0.85, particle_speed=2.0,
        wifi_response=0.9, bluetooth_response=0.9
    ),

    "threat_detected": CognitiveProfile(
        "threat_detected",
        cohesion=0.9, separation=0.1, alignment=0.9, wander=0.1,
        breath_rate=2.5, breath_depth=0.6,
        glow_intensity=1.0, particle_speed=3.5,
        color_shift=(0.7, 0, 0)  # Intense red warning
    ),

    "defensive_mode": CognitiveProfile(
        "defensive_mode",
        cohesion=0.95, separation=0.05, alignment=0.95, wander=0.03,
        breath_rate=2.0, breath_depth=0.5,
        glow_intensity=0.95, particle_speed=2.5,
        color_shift=(0.6, 0, 0.2)  # Red-purple defense
    ),

    # === INFORMATION STATES ===
    "presenting_information": CognitiveProfile(
        "presenting_information",
        cohesion=0.6, separation=0.3, alignment=0.7, wander=0.2,
        breath_rate=1.2, breath_depth=0.3,
        glow_intensity=0.8, particle_speed=1.0
    ),

    "explaining_concept": CognitiveProfile(
        "explaining_concept",
        cohesion=0.65, separation=0.3, alignment=0.75, wander=0.25,
        breath_rate=1.4, breath_depth=0.35,
        glow_intensity=0.85, particle_speed=1.3,
        color_shift=(0, 0.2, 0.3)  # Educational cyan
    ),

    "demonstrating_feature": CognitiveProfile(
        "demonstrating_feature",
        cohesion=0.55, separation=0.4, alignment=0.6, wander=0.35,
        breath_rate=1.5, breath_depth=0.4,
        glow_intensity=0.9, particle_speed=1.5
    ),

    # === SENSOR-FOCUSED STATES ===
    "showing_wifi_map": CognitiveProfile(
        "showing_wifi_map",
        cohesion=0.4, separation=0.5, alignment=0.4, wander=0.4,
        breath_rate=1.0, breath_depth=0.3,
        glow_intensity=0.8, particle_speed=1.2,
        color_shift=(0, 0, 0.6),  # Blue WiFi
        wifi_response=1.0
    ),

    "showing_bluetooth_devices": CognitiveProfile(
        "showing_bluetooth_devices",
        cohesion=0.5, separation=0.4, alignment=0.5, wander=0.3,
        breath_rate=1.1, breath_depth=0.3,
        glow_intensity=0.8, particle_speed=1.1,
        color_shift=(0.4, 0, 0.6),  # Purple Bluetooth
        bluetooth_response=1.0
    ),

    "displaying_sensor_data": CognitiveProfile(
        "displaying_sensor_data",
        cohesion=0.6, separation=0.3, alignment=0.6, wander=0.2,
        breath_rate=1.3, breath_depth=0.35,
        glow_intensity=0.85, particle_speed=1.4,
        color_shift=(0, 0.3, 0.2)  # Green data
    ),

    # === UTILITY STATES ===
    "error_state": CognitiveProfile(
        "error_state",
        cohesion=0.3, separation=0.7, alignment=0.2, wander=0.9,
        breath_rate=2.5, breath_depth=0.7,
        glow_intensity=0.9, particle_speed=2.0,
        color_shift=(0.8, 0, 0)  # Bright red error
    ),

    "thinking_pause": CognitiveProfile(
        "thinking_pause",
        cohesion=0.7, separation=0.2, alignment=0.8, wander=0.1,
        breath_rate=0.6, breath_depth=0.25,
        glow_intensity=0.6, particle_speed=0.5
    ),

    "memory_recall": CognitiveProfile(
        "memory_recall",
        cohesion=0.75, separation=0.2, alignment=0.8, wander=0.15,
        breath_rate=1.5, breath_depth=0.4,
        glow_intensity=0.85, particle_speed=1.2,
        color_shift=(0.5, 0.3, 0)  # Golden memory
    ),

    "learning_new_pattern": CognitiveProfile(
        "learning_new_pattern",
        cohesion=0.7, separation=0.25, alignment=0.75, wander=0.3,
        breath_rate=1.7, breath_depth=0.45,
        glow_intensity=0.9, particle_speed=1.8,
        color_shift=(0, 0.4, 0.3)  # Green learning
    ),

    # === SPECIAL STATES ===
    "sleep_mode": CognitiveProfile(
        "sleep_mode",
        cohesion=0.95, separation=0.05, alignment=0.95, wander=0.02,
        breath_rate=0.3, breath_depth=0.15,
        glow_intensity=0.2, particle_speed=0.1,
        color_shift=(0, 0, 0.2)  # Dim blue rest
    ),

    "wake_up_sequence": CognitiveProfile(
        "wake_up_sequence",
        cohesion=0.4, separation=0.5, alignment=0.4, wander=0.6,
        breath_rate=2.0, breath_depth=0.7,
        glow_intensity=0.7, particle_speed=2.5,
        color_shift=(0.3, 0.3, 0)  # Warm awakening
    ),

    "shutdown_sequence": CognitiveProfile(
        "shutdown_sequence",
        cohesion=0.9, separation=0.1, alignment=0.9, wander=0.05,
        breath_rate=0.5, breath_depth=0.3,
        glow_intensity=0.5, particle_speed=0.3,
        color_shift=(0, 0, 0.3)  # Blue shutdown
    ),

    # === ADVANCED COGNITIVE STATES ===
    "pattern_recognition": CognitiveProfile(
        "pattern_recognition",
        cohesion=0.8, separation=0.2, alignment=0.9, wander=0.15,
        breath_rate=2.0, breath_depth=0.45,
        glow_intensity=0.95, particle_speed=2.2,
        color_shift=(0.2, 0.3, 0.4)  # Analytical blue-green
    ),

    "creative_thinking": CognitiveProfile(
        "creative_thinking",
        cohesion=0.3, separation=0.6, alignment=0.3, wander=0.8,
        breath_rate=1.8, breath_depth=0.6,
        glow_intensity=0.9, particle_speed=2.5,
        color_shift=(0.4, 0, 0.5)  # Purple creativity
    ),

    "collaborative_mode": CognitiveProfile(
        "collaborative_mode",
        cohesion=0.6, separation=0.3, alignment=0.7, wander=0.3,
        breath_rate=1.4, breath_depth=0.4,
        glow_intensity=0.85, particle_speed=1.5,
        color_shift=(0.2, 0.3, 0.2)  # Balanced green collaboration
    ),

    "autonomous_operation": CognitiveProfile(
        "autonomous_operation",
        cohesion=0.7, separation=0.25, alignment=0.75, wander=0.25,
        breath_rate=1.2, breath_depth=0.35,
        glow_intensity=0.8, particle_speed=1.3,
        color_shift=(0, 0.3, 0.3)  # Cyan autonomy
    ),

    "meditation_state": CognitiveProfile(
        "meditation_state",
        cohesion=0.9, separation=0.1, alignment=0.9, wander=0.05,
        breath_rate=0.4, breath_depth=0.2,
        glow_intensity=0.6, particle_speed=0.4,
        color_shift=(0.1, 0, 0.3)  # Deep purple calm
    ),
}


class CognitiveEngine:
    """
    Real-time cognitive state to particle behavior mapping.

    This is the nervous system that makes the visualization ALIVE.
    Translates abstract personality states into concrete particle motion.
    """

    def __init__(self):
        self.current_state = "idle_standing"
        self.target_state = "idle_standing"
        self.transition_progress = 1.0  # 0.0 = current, 1.0 = target
        self.transition_duration = 1.0  # seconds
        self.transition_start_time = 0.0

        # Breathing timer (for organic pulsing)
        self.breath_timer = 0.0

        # Sensor data (updated by external systems)
        self.sensor_data = {
            "wifi_networks": [],
            "bluetooth_devices": [],
            "audio_amplitude": 0.0,
            "gps_movement": 0.0,
            "human_detected": False
        }

        # Performance optimization
        self.last_update_time = time.time()

    def update_state(self, new_state: str, transition_time: float = 1.0):
        """
        Smoothly transition to new cognitive state.

        Args:
            new_state: Target personality state name
            transition_time: Seconds to complete transition
        """
        if new_state not in COGNITIVE_PROFILES:
            print(f"Warning: Unknown cognitive state '{new_state}'")
            return

        if new_state == self.target_state:
            return  # Already transitioning to this state

        self.current_state = self.target_state  # Previous target becomes new current
        self.target_state = new_state
        self.transition_progress = 0.0
        self.transition_duration = max(0.1, transition_time)
        self.transition_start_time = time.time()

    def update(self, dt: float):
        """
        Update internal state (call each frame).

        Args:
            dt: Delta time in seconds
        """
        # Update breathing timer
        self.breath_timer += dt

        # Update state transition
        if self.transition_progress < 1.0:
            self.transition_progress = min(1.0,
                (time.time() - self.transition_start_time) / self.transition_duration)

    def get_current_profile(self) -> CognitiveProfile:
        """
        Get the interpolated cognitive profile between current and target states.

        Returns:
            Blended CognitiveProfile
        """
        current = COGNITIVE_PROFILES[self.current_state]

        if self.transition_progress >= 1.0:
            return COGNITIVE_PROFILES[self.target_state]

        target = COGNITIVE_PROFILES[self.target_state]
        t = self.transition_progress

        # Smooth interpolation using ease-in-out cubic
        t = t * t * (3 - 2 * t)

        # Interpolate all parameters
        return CognitiveProfile(
            state_name=f"{current.state_name} -> {target.state_name}",
            cohesion=current.cohesion * (1-t) + target.cohesion * t,
            separation=current.separation * (1-t) + target.separation * t,
            alignment=current.alignment * (1-t) + target.alignment * t,
            wander=current.wander * (1-t) + target.wander * t,
            breath_rate=current.breath_rate * (1-t) + target.breath_rate * t,
            breath_depth=current.breath_depth * (1-t) + target.breath_depth * t,
            glow_intensity=current.glow_intensity * (1-t) + target.glow_intensity * t,
            particle_speed=current.particle_speed * (1-t) + target.particle_speed * t,
            color_shift=tuple(
                current.color_shift[i] * (1-t) + target.color_shift[i] * t
                for i in range(3)
            ),
            wifi_response=current.wifi_response * (1-t) + target.wifi_response * t,
            bluetooth_response=current.bluetooth_response * (1-t) + target.bluetooth_response * t,
            audio_response=current.audio_response * (1-t) + target.audio_response * t
        )

    def update_sensor_data(self, sensor_type: str, data: any):
        """
        Feed sensor data to the cognitive engine.

        Args:
            sensor_type: Type of sensor data (wifi_networks, bluetooth_devices, etc.)
            data: Sensor data payload
        """
        self.sensor_data[sensor_type] = data

    def get_breathing_factor(self) -> float:
        """
        Get current breathing oscillation value.

        Returns:
            Float between -1.0 and 1.0
        """
        profile = self.get_current_profile()
        return np.sin(self.breath_timer * profile.breath_rate * 2 * np.pi) * profile.breath_depth


# === TESTING ===

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("COGNITIVE ENGINE TEST")
    print("=" * 70)

    engine = CognitiveEngine()

    print(f"\nDefined {len(COGNITIVE_PROFILES)} cognitive profiles:")
    for state_name in sorted(COGNITIVE_PROFILES.keys()):
        profile = COGNITIVE_PROFILES[state_name]
        print(f"  {state_name:30} - speed:{profile.particle_speed:.1f} glow:{profile.glow_intensity:.1f}")

    print(f"\n✓ Cognitive Engine initialized")
    print(f"✓ Current state: {engine.current_state}")

    # Test state transition
    print(f"\nTransitioning to 'analyzing_data' over 2 seconds...")
    engine.update_state("analyzing_data", transition_time=2.0)

    for i in range(20):
        engine.update(0.1)
        profile = engine.get_current_profile()
        breath = engine.get_breathing_factor()
        print(f"  t={i*0.1:.1f}s  progress:{engine.transition_progress:.2f}  "
              f"speed:{profile.particle_speed:.2f}  breath:{breath:+.2f}")
        time.sleep(0.1)

    print(f"\n✓ State transition complete")
    print(f"✓ Final state: {engine.target_state}")
    print("\n" + "=" * 70)
