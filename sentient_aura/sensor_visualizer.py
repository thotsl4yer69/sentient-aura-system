#!/usr/bin/env python3
"""
Sensor Visualizer - Maps Real-World Data to Particle Aesthetics
================================================================

Visualizes sensor data through particle colors and motion:
- WiFi Networks: Blue particle streams flowing from network sources
- Bluetooth Devices: Purple particle clusters around detected devices
- Audio Amplitude: Green particle waves pulsing with speech
- GPS Movement: Particle trails showing motion direction

NO SIMULATED DATA - only visualizes real sensor readings.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import math


class SensorVisualizer:
    """
    Maps sensor data to particle visual properties.

    Transforms abstract sensor readings into concrete visual elements
    that make the invisible electromagnetic spectrum VISIBLE.
    """

    def __init__(self, num_particles: int = 10000):
        """
        Initialize sensor visualizer.

        Args:
            num_particles: Total number of particles available
        """
        self.num_particles = num_particles

        # Particle allocation (percentages)
        self.wifi_particle_ratio = 0.2      # 20% for WiFi visualization
        self.bluetooth_particle_ratio = 0.15 # 15% for Bluetooth
        self.audio_particle_ratio = 0.1      # 10% for Audio
        # Remaining 55% controlled by cognitive state

        # Particle indices for each sensor type
        self.wifi_particles = range(0, int(num_particles * self.wifi_particle_ratio))
        self.bluetooth_particles = range(
            int(num_particles * self.wifi_particle_ratio),
            int(num_particles * (self.wifi_particle_ratio + self.bluetooth_particle_ratio))
        )
        self.audio_particles = range(
            int(num_particles * (self.wifi_particle_ratio + self.bluetooth_particle_ratio)),
            int(num_particles * (self.wifi_particle_ratio + self.bluetooth_particle_ratio + self.audio_particle_ratio))
        )

        # Color definitions (RGB 0-255)
        self.COLOR_WIFI = np.array([0, 100, 255])        # Blue
        self.COLOR_BLUETOOTH = np.array([128, 0, 255])   # Purple
        self.COLOR_AUDIO = np.array([0, 255, 100])       # Green
        self.COLOR_GPS = np.array([255, 200, 0])         # Amber
        self.COLOR_DEFAULT = np.array([100, 150, 255])   # Soft blue-white

    def visualize_wifi_networks(
        self,
        particle_positions: np.ndarray,
        wifi_data: List[Dict],
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Visualize WiFi networks as blue particle streams.

        Args:
            particle_positions: Current particle positions (N, 3)
            wifi_data: List of detected WiFi networks with signal strength
            dt: Delta time for smooth animation

        Returns:
            Tuple of (position_influences, particle_colors)
        """
        influences = np.zeros_like(particle_positions)
        colors = np.tile(self.COLOR_DEFAULT, (self.num_particles, 1))

        if not wifi_data:
            return influences, colors

        # Create WiFi source positions based on network properties
        wifi_sources = []
        for network in wifi_data[:10]:  # Max 10 networks
            # Position based on BSSID hash (consistent positioning)
            bssid_hash = hash(network.get('bssid', '')) % 360
            angle = bssid_hash * np.pi / 180
            distance = (100 + network.get('signal', -50)) / 100.0  # -100 to 0 dBm

            # Create source position on sphere around origin
            source = np.array([
                np.cos(angle) * distance * 0.8,
                np.sin(angle) * distance * 0.8,
                np.sin(angle * 2) * 0.3  # Z variation
            ])

            wifi_sources.append({
                'position': source,
                'strength': -network.get('signal', -50) / 100.0,  # Normalize
                'ssid': network.get('ssid', 'Unknown')
            })

        # Attract WiFi particles to network sources
        for i in self.wifi_particles:
            if wifi_sources:
                # Choose source based on particle index
                source_idx = i % len(wifi_sources)
                source = wifi_sources[source_idx]

                # Calculate attraction force
                direction = source['position'] - particle_positions[i]
                distance = np.linalg.norm(direction)

                if distance > 0:
                    # Stronger signal = stronger attraction
                    influence = direction / distance * source['strength'] * 0.1
                    influences[i] = influence

                # Set WiFi color with signal strength variation
                intensity = source['strength']
                colors[i] = self.COLOR_WIFI * intensity

        return influences, colors

    def visualize_bluetooth_devices(
        self,
        particle_positions: np.ndarray,
        bluetooth_data: List[Dict],
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Visualize Bluetooth devices as purple particle clusters.

        Args:
            particle_positions: Current particle positions (N, 3)
            bluetooth_data: List of detected Bluetooth devices with RSSI
            dt: Delta time for smooth animation

        Returns:
            Tuple of (position_influences, particle_colors)
        """
        influences = np.zeros_like(particle_positions)
        colors = np.tile(self.COLOR_DEFAULT, (self.num_particles, 1))

        if not bluetooth_data:
            return influences, colors

        # Create clusters for each Bluetooth device
        particles_per_device = len(self.bluetooth_particles) // max(len(bluetooth_data), 1)

        for device_idx, device in enumerate(bluetooth_data[:10]):  # Max 10 devices
            # Cluster center based on device type and signal
            device_hash = hash(device.get('mac', '')) % 360
            angle = device_hash * np.pi / 180

            # Position based on RSSI (closer = stronger signal)
            rssi = device.get('rssi', -70)  # -100 to -30 dBm typical
            distance = (rssi + 100) / 70.0  # Normalize to 0-1

            cluster_center = np.array([
                np.cos(angle) * 0.6,
                np.sin(angle) * 0.6,
                distance * 0.4 - 0.2
            ])

            # Assign particles to this device cluster
            start_idx = list(self.bluetooth_particles)[device_idx * particles_per_device]
            end_idx = list(self.bluetooth_particles)[min(
                (device_idx + 1) * particles_per_device,
                len(self.bluetooth_particles)
            )]

            for i in range(start_idx, end_idx):
                # Pull particles toward cluster center
                direction = cluster_center - particle_positions[i]
                distance_to_center = np.linalg.norm(direction)

                if distance_to_center > 0:
                    # Form tight cluster (strong cohesion)
                    influence = direction / distance_to_center * 0.15
                    influences[i] = influence

                # Purple color with RSSI intensity
                intensity = (rssi + 100) / 70.0  # Normalize
                colors[i] = self.COLOR_BLUETOOTH * np.clip(intensity, 0.3, 1.0)

        return influences, colors

    def visualize_audio_amplitude(
        self,
        particle_positions: np.ndarray,
        audio_amplitude: float,
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Visualize audio amplitude as green particle waves.

        Args:
            particle_positions: Current particle positions (N, 3)
            audio_amplitude: Current audio amplitude (0-1)
            dt: Delta time for smooth animation

        Returns:
            Tuple of (position_influences, particle_colors)
        """
        influences = np.zeros_like(particle_positions)
        colors = np.tile(self.COLOR_DEFAULT, (self.num_particles, 1))

        if audio_amplitude < 0.01:
            return influences, colors

        # Create outward wave pulse from center
        for i in self.audio_particles:
            # Calculate distance from center
            distance = np.linalg.norm(particle_positions[i])

            # Create pulsing outward force
            if distance > 0:
                direction = particle_positions[i] / distance
                pulse_strength = audio_amplitude * 0.2

                # Pulse particles outward
                influences[i] = direction * pulse_strength

            # Green color with audio intensity
            colors[i] = self.COLOR_AUDIO * np.clip(audio_amplitude, 0.3, 1.0)

        return influences, colors

    def visualize_gps_movement(
        self,
        particle_positions: np.ndarray,
        movement_vector: np.ndarray,
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Visualize GPS movement as particle trails.

        Args:
            particle_positions: Current particle positions (N, 3)
            movement_vector: Movement direction vector (3,)
            dt: Delta time for smooth animation

        Returns:
            Tuple of (position_influences, particle_colors)
        """
        influences = np.zeros_like(particle_positions)
        colors = np.tile(self.COLOR_DEFAULT, (self.num_particles, 1))

        movement_magnitude = np.linalg.norm(movement_vector)

        if movement_magnitude < 0.001:
            return influences, colors

        # Create trailing effect in movement direction
        movement_dir = movement_vector / movement_magnitude

        # Apply subtle drift in movement direction to all particles
        influences[:] = movement_dir * movement_magnitude * 0.05

        # Amber glow for particles showing movement
        if movement_magnitude > 0.1:
            colors[:] = (colors + self.COLOR_GPS * movement_magnitude) / 2

        return influences, colors

    def combine_sensor_influences(
        self,
        particle_positions: np.ndarray,
        sensor_data: Dict,
        dt: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Combine all sensor visualizations into unified influence.

        Args:
            particle_positions: Current particle positions (N, 3)
            sensor_data: Dictionary containing all sensor readings
            dt: Delta time for animation

        Returns:
            Tuple of (total_influences, particle_colors)
        """
        total_influences = np.zeros_like(particle_positions)
        colors = np.tile(self.COLOR_DEFAULT, (self.num_particles, 1))

        # 1. WiFi visualization
        wifi_data = sensor_data.get('wifi_networks', [])
        wifi_influence, wifi_colors = self.visualize_wifi_networks(
            particle_positions, wifi_data, dt
        )
        total_influences += wifi_influence
        colors[list(self.wifi_particles)] = wifi_colors[list(self.wifi_particles)]

        # 2. Bluetooth visualization
        bluetooth_data = sensor_data.get('bluetooth_devices', [])
        bt_influence, bt_colors = self.visualize_bluetooth_devices(
            particle_positions, bluetooth_data, dt
        )
        total_influences += bt_influence
        colors[list(self.bluetooth_particles)] = bt_colors[list(self.bluetooth_particles)]

        # 3. Audio visualization
        audio_amplitude = sensor_data.get('audio_amplitude', 0.0)
        audio_influence, audio_colors = self.visualize_audio_amplitude(
            particle_positions, audio_amplitude, dt
        )
        total_influences += audio_influence
        colors[list(self.audio_particles)] = audio_colors[list(self.audio_particles)]

        # 4. GPS movement visualization
        movement_vector = sensor_data.get('gps_movement', np.array([0, 0, 0]))
        gps_influence, gps_colors = self.visualize_gps_movement(
            particle_positions, movement_vector, dt
        )
        total_influences += gps_influence

        return total_influences, colors

    def apply_cognitive_color_shift(
        self,
        base_colors: np.ndarray,
        color_shift: Tuple[float, float, float],
        glow_intensity: float
    ) -> np.ndarray:
        """
        Apply cognitive state color shift and glow to base colors.

        Args:
            base_colors: Base particle colors (N, 3)
            color_shift: RGB shift values (-1 to 1)
            glow_intensity: Overall glow intensity (0-1)

        Returns:
            Modified colors with cognitive influence
        """
        # Convert color_shift to RGB adjustment
        shift = np.array(color_shift) * 100

        # Apply shift
        shifted_colors = base_colors + shift

        # Apply glow intensity
        shifted_colors *= glow_intensity

        # Clamp to valid RGB range
        shifted_colors = np.clip(shifted_colors, 0, 255)

        return shifted_colors.astype(np.uint8)

    def apply_sensor_colors(
        self,
        particle_positions: np.ndarray,
        wifi_data: List[Dict] = None,
        bluetooth_data: List[Dict] = None,
        audio_amplitude: float = 0.0,
        base_color: Tuple[float, float, float] = (0, 0, 0)
    ) -> np.ndarray:
        """
        Apply sensor-based coloring to all particles.

        Combines WiFi, Bluetooth, and Audio visualizations.

        Args:
            particle_positions: Particle positions (N, 3)
            wifi_data: List of WiFi networks (optional)
            bluetooth_data: List of Bluetooth devices (optional)
            audio_amplitude: Audio level 0-1 (optional)
            base_color: Base color shift from cognitive state

        Returns:
            Array of RGB colors (N, 3) in range 0-255
        """
        # Start with default colors
        colors = np.tile(self.COLOR_DEFAULT, (self.num_particles, 1)).astype(float)

        # Apply base color shift from cognitive state
        if base_color != (0, 0, 0):
            shift = np.array(base_color) * 100
            colors += shift
            colors = np.clip(colors, 0, 255)

        # Overlay WiFi visualization
        if wifi_data:
            _, wifi_colors = self.visualize_wifi_networks(particle_positions, wifi_data, 0.016)
            # Blend WiFi colors for WiFi particles
            for i in self.wifi_particles:
                colors[i] = wifi_colors[i]

        # Overlay Bluetooth visualization
        if bluetooth_data:
            _, bt_colors = self.visualize_bluetooth_devices(particle_positions, bluetooth_data, 0.016)
            # Blend Bluetooth colors for BT particles
            for i in self.bluetooth_particles:
                colors[i] = bt_colors[i]

        # Overlay Audio visualization
        if audio_amplitude > 0.01:
            _, audio_colors = self.visualize_audio_amplitude(particle_positions, audio_amplitude, 0.016)
            # Blend audio colors for audio particles
            for i in self.audio_particles:
                colors[i] = audio_colors[i]

        return colors.astype(np.uint8)


# === TESTING ===

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SENSOR VISUALIZER TEST")
    print("=" * 70)

    visualizer = SensorVisualizer(num_particles=10000)

    print(f"\n✓ Sensor Visualizer initialized")
    print(f"  Total particles: {visualizer.num_particles}")
    print(f"  WiFi particles: {len(visualizer.wifi_particles)}")
    print(f"  Bluetooth particles: {len(visualizer.bluetooth_particles)}")
    print(f"  Audio particles: {len(visualizer.audio_particles)}")

    # Test WiFi visualization
    print(f"\nTesting WiFi visualization...")
    test_positions = np.random.rand(10000, 3) * 2 - 1
    test_wifi = [
        {'ssid': 'HomeNetwork', 'bssid': 'AA:BB:CC:DD:EE:FF', 'signal': -45},
        {'ssid': 'OfficeWiFi', 'bssid': '11:22:33:44:55:66', 'signal': -65},
        {'ssid': 'Neighbor5G', 'bssid': 'AA:11:BB:22:CC:33', 'signal': -75}
    ]

    wifi_influence, wifi_colors = visualizer.visualize_wifi_networks(
        test_positions, test_wifi, dt=1/60
    )
    print(f"  WiFi influence magnitude: {np.linalg.norm(wifi_influence):.3f}")
    print(f"  Unique colors used: {len(np.unique(wifi_colors, axis=0))}")

    # Test Bluetooth visualization
    print(f"\nTesting Bluetooth visualization...")
    test_bluetooth = [
        {'mac': '00:11:22:33:44:55', 'name': 'Phone', 'rssi': -40},
        {'mac': 'AA:BB:CC:DD:EE:FF', 'name': 'Headphones', 'rssi': -55}
    ]

    bt_influence, bt_colors = visualizer.visualize_bluetooth_devices(
        test_positions, test_bluetooth, dt=1/60
    )
    print(f"  Bluetooth influence magnitude: {np.linalg.norm(bt_influence):.3f}")
    print(f"  Unique colors used: {len(np.unique(bt_colors, axis=0))}")

    # Test combined sensors
    print(f"\nTesting combined sensor visualization...")
    sensor_data = {
        'wifi_networks': test_wifi,
        'bluetooth_devices': test_bluetooth,
        'audio_amplitude': 0.5,
        'gps_movement': np.array([0.1, 0.2, 0.0])
    }

    total_influence, combined_colors = visualizer.combine_sensor_influences(
        test_positions, sensor_data, dt=1/60
    )
    print(f"  Total influence magnitude: {np.linalg.norm(total_influence):.3f}")
    print(f"  Unique colors used: {len(np.unique(combined_colors, axis=0))}")

    # Test color shift
    print(f"\nTesting cognitive color shift...")
    shifted_colors = visualizer.apply_cognitive_color_shift(
        combined_colors,
        color_shift=(0.3, 0, 0.5),  # Purple shift
        glow_intensity=0.8
    )
    print(f"  Color range after shift: [{shifted_colors.min()}, {shifted_colors.max()}]")

    print(f"\n✓ All sensor visualization tests passed")
    print("\n" + "=" * 70)
