#!/usr/bin/env python3
"""
Morphing Controller for Cortana <-> Environment Form Switching

Manages particle system transitions between:
1. Cortana Form: Sexy holographic female humanoid (500K particles, Halo-accurate)
2. Environment Form: 3D reconstruction of surroundings (like sentient sand sculpture)

Key capabilities:
- Smooth morphing transitions (not instant switches)
- Blend modes (partial Cortana + partial environment)
- Context-aware mode selection (talking → Cortana, observing → environment)
- Camera data integration for 3D reconstruction
- Imagination/inference for blind spots

Based on user vision: "sentient sexy cortana sand creature that can morph into
a full house design or city scape in as much detail as possible"
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class VisualizationMode(Enum):
    """Particle system visualization modes."""
    CORTANA_FULL = "cortana_full"              # 100% Cortana humanoid form
    ENVIRONMENT_FULL = "environment_full"      # 100% 3D environment reconstruction
    HYBRID = "hybrid"                          # Blend of both (e.g., Cortana in scene)
    TRANSITION = "transition"                  # Actively morphing between modes
    ABSTRACT = "abstract"                      # Abstract particle expression


@dataclass
class ParticleTarget:
    """Target position for a single particle."""
    position: np.ndarray   # (x, y, z)
    color: np.ndarray      # (r, g, b, a)
    size: float
    glow: float


@dataclass
class CortanaFormSpec:
    """Specification for Cortana humanoid form."""
    total_particles: int = 500000

    # Particle distribution
    head_particles: int = 75000
    torso_particles: int = 150000
    arms_particles: int = 80000
    legs_particles: int = 120000
    data_symbols: int = 75000

    # Anatomical proportions (meters, 1.73m tall)
    height: float = 1.73
    head_radius: float = 0.11
    torso_width: float = 0.35

    # Color scheme (Halo Cortana: blue/cyan/lavender gradient)
    base_color: Tuple[float, float, float] = (0.0, 0.75, 1.0)  # Cyan

    # Animation parameters
    breathing_rate: float = 0.3  # Hz
    idle_sway_amount: float = 0.02  # meters


@dataclass
class EnvironmentFormSpec:
    """Specification for 3D environment reconstruction."""
    total_particles: int = 500000

    # Reconstruction parameters
    voxel_resolution: float = 0.05  # 5cm voxels
    max_range: float = 5.0  # meters

    # Data sources
    use_camera: bool = True
    use_sensors: bool = True
    use_inference: bool = True  # Fill blind spots with imagination

    # Visual style
    particle_density: float = 1.0  # particles per voxel
    color_mode: str = 'realistic'  # or 'semantic', 'heat_map'


class MorphingController:
    """
    Controls particle system morphing between Cortana and Environment forms.

    Manages smooth transitions, blending, and context-aware mode selection.
    """

    def __init__(self, total_particles: int = 500000):
        """
        Initialize morphing controller.

        Args:
            total_particles: Total number of particles in system
        """
        self.total_particles = total_particles

        # Current state
        self.current_mode = VisualizationMode.CORTANA_FULL
        self.target_mode = VisualizationMode.CORTANA_FULL

        # Transition state
        self.is_transitioning = False
        self.transition_progress = 0.0  # 0.0 = source, 1.0 = target
        self.transition_duration = 2.0  # seconds
        self.transition_start_time = 0.0

        # Blend weights
        self.cortana_weight = 1.0
        self.environment_weight = 0.0

        # Form specifications
        self.cortana_spec = CortanaFormSpec(total_particles=total_particles)
        self.environment_spec = EnvironmentFormSpec(total_particles=total_particles)

        # Particle targets (computed lazily)
        self._cortana_targets = None
        self._environment_targets = None

        # Context tracking
        self.user_speaking = False
        self.user_present = False
        self.active_scene_observation = False

        logger.info("Morphing controller initialized: %d particles", total_particles)

    def update(self, context: Dict) -> VisualizationMode:
        """
        Update morphing state based on context.

        Args:
            context: Current context (user interaction, scene, emotion, etc.)

        Returns:
            Current visualization mode
        """
        # Extract context
        self.user_speaking = context.get('user_speaking', False)
        self.user_present = context.get('user_present', False)
        self.active_scene_observation = context.get('observing_environment', False)

        # Determine target mode based on context
        new_target = self._infer_target_mode(context)

        # If target changed, start transition
        if new_target != self.target_mode:
            self._start_transition(new_target)

        # Update transition if in progress
        if self.is_transitioning:
            self._update_transition()

        return self.current_mode

    def _infer_target_mode(self, context: Dict) -> VisualizationMode:
        """
        Infer target visualization mode from context.

        Rules:
        - User speaking/interaction → Cortana form (show presence)
        - Actively observing environment → Environment form (show what she sees)
        - Idle with no user → Abstract or environment
        - Danger/alert → Cortana form (protective presence)
        """
        # Priority 1: User interaction
        if self.user_speaking or context.get('user_interaction', False):
            return VisualizationMode.CORTANA_FULL

        # Priority 2: Danger/alert (show protective presence)
        if context.get('danger_detected', False):
            return VisualizationMode.CORTANA_FULL

        # Priority 3: Active observation (show what she's seeing)
        if self.active_scene_observation:
            # If user is present, show hybrid (Cortana + environment)
            if self.user_present:
                return VisualizationMode.HYBRID
            else:
                return VisualizationMode.ENVIRONMENT_FULL

        # Priority 4: Emotion-driven
        emotion_state = context.get('emotion', {}).get('state', 'calm')
        if emotion_state in ['curious', 'thinking', 'focused']:
            return VisualizationMode.ENVIRONMENT_FULL

        # Default: Cortana form (show personality)
        return VisualizationMode.CORTANA_FULL

    def _start_transition(self, target_mode: VisualizationMode):
        """
        Start transition to new mode.

        Args:
            target_mode: Target visualization mode
        """
        logger.info("Starting transition: %s → %s",
                   self.current_mode.value, target_mode.value)

        self.target_mode = target_mode
        self.is_transitioning = True
        self.transition_progress = 0.0
        self.transition_start_time = time.time()

        # Adjust transition duration based on mode change
        if (self.current_mode == VisualizationMode.CORTANA_FULL and
            target_mode == VisualizationMode.ENVIRONMENT_FULL):
            self.transition_duration = 3.0  # Slower for major change
        else:
            self.transition_duration = 1.5  # Faster for minor changes

    def _update_transition(self):
        """Update ongoing transition."""
        elapsed = time.time() - self.transition_start_time
        self.transition_progress = min(elapsed / self.transition_duration, 1.0)

        # Smooth easing (ease-in-out cubic)
        t = self.transition_progress
        eased = 3*t*t - 2*t*t*t if t < 0.5 else 1 - pow(-2*t + 2, 3) / 2

        # Update blend weights
        if self.target_mode == VisualizationMode.CORTANA_FULL:
            self.cortana_weight = eased
            self.environment_weight = 1.0 - eased
        elif self.target_mode == VisualizationMode.ENVIRONMENT_FULL:
            self.cortana_weight = 1.0 - eased
            self.environment_weight = eased
        elif self.target_mode == VisualizationMode.HYBRID:
            # Blend to 50/50
            target_cortana = 0.6
            target_env = 0.4
            self.cortana_weight = self.cortana_weight + (target_cortana - self.cortana_weight) * eased
            self.environment_weight = 1.0 - self.cortana_weight

        # Check if transition complete
        if self.transition_progress >= 1.0:
            self.is_transitioning = False
            self.current_mode = self.target_mode
            logger.debug("Transition complete: now in %s mode", self.current_mode.value)

    def get_particle_targets(self, camera_data: Optional[Dict] = None,
                           sensor_data: Optional[Dict] = None) -> List[ParticleTarget]:
        """
        Get current particle target positions/colors based on mode.

        Args:
            camera_data: Optional camera/vision data for environment reconstruction
            sensor_data: Optional sensor data for environment understanding

        Returns:
            List of particle targets (positions, colors, sizes)
        """
        # Get Cortana targets
        cortana_targets = self._get_cortana_targets()

        # Get environment targets
        environment_targets = self._get_environment_targets(camera_data, sensor_data)

        # Blend based on current weights
        blended_targets = []
        for i in range(self.total_particles):
            cortana_t = cortana_targets[i]
            env_t = environment_targets[i]

            # Blend position
            blended_pos = (self.cortana_weight * cortana_t.position +
                          self.environment_weight * env_t.position)

            # Blend color
            blended_color = (self.cortana_weight * cortana_t.color +
                           self.environment_weight * env_t.color)

            # Blend size and glow
            blended_size = (self.cortana_weight * cortana_t.size +
                           self.environment_weight * env_t.size)
            blended_glow = (self.cortana_weight * cortana_t.glow +
                           self.environment_weight * env_t.glow)

            blended_targets.append(ParticleTarget(
                position=blended_pos,
                color=blended_color,
                size=blended_size,
                glow=blended_glow
            ))

        return blended_targets

    def _get_cortana_targets(self) -> List[ParticleTarget]:
        """
        Generate particle targets for Cortana humanoid form.

        Returns:
            List of particle targets forming Cortana
        """
        # Cache targets if not computed
        if self._cortana_targets is None:
            self._cortana_targets = self._generate_cortana_form()

        # Apply animation (breathing, idle sway)
        animated_targets = self._apply_cortana_animation(self._cortana_targets)

        return animated_targets

    def _generate_cortana_form(self) -> List[ParticleTarget]:
        """
        Generate Cortana humanoid form (anatomically accurate).

        Based on CORTANA_VISUALIZATION_SPEC.md:
        - 500K particles total
        - Anatomically accurate female proportions
        - Blue/cyan/lavender gradient
        - Holographic appearance
        """
        targets = []

        spec = self.cortana_spec

        # HEAD (75K particles)
        for _ in range(spec.head_particles):
            # Random point in sphere
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            r = spec.head_radius * np.random.uniform(0.7, 1.0) ** (1/3)

            x = r * np.sin(phi) * np.cos(theta)
            y = spec.height - spec.head_radius + r * np.cos(phi)
            z = r * np.sin(phi) * np.sin(theta)

            # Cyan color with slight variation
            color = np.array([0.0, 0.6 + np.random.uniform(-0.1, 0.1),
                            0.9 + np.random.uniform(-0.1, 0.1), 0.8])

            targets.append(ParticleTarget(
                position=np.array([x, y, z]),
                color=color,
                size=0.003,
                glow=0.7
            ))

        # TORSO (150K particles)
        for _ in range(spec.torso_particles):
            # Ellipsoid shape
            y = np.random.uniform(0.95, 1.55)  # Height range

            # Width varies with height (narrower at waist)
            if y < 1.05:  # Hips
                width = spec.torso_width * 0.9
            elif y < 1.15:  # Waist
                width = spec.torso_width * 0.6
            else:  # Chest
                width = spec.torso_width * 0.8

            theta = np.random.uniform(0, 2*np.pi)
            r = width * np.random.uniform(0, 1) ** 0.5

            x = r * np.cos(theta)
            z = r * np.sin(theta) * 0.6  # Flatter front-back

            # Color gradient: darker blue at bottom, lighter at top
            y_norm = (y - 0.95) / 0.6
            color = np.array([
                0.0,
                0.5 + y_norm * 0.3,
                0.8 + y_norm * 0.2,
                0.7
            ])

            targets.append(ParticleTarget(
                position=np.array([x, y, z]),
                color=color,
                size=0.003,
                glow=0.6
            ))

        # ARMS (40K each = 80K total)
        for side in [-1, 1]:  # Left and right
            for _ in range(40000):
                # Arm extends down from shoulder
                y = np.random.uniform(0.75, 1.45)  # Shoulder to hand

                # Arm position (away from body)
                shoulder_offset = spec.torso_width * 0.5
                x_base = side * shoulder_offset

                # Slight bend
                arm_length = 1.45 - y
                x = x_base + side * arm_length * 0.2

                # Arm thickness
                r = 0.04 * np.random.uniform(0, 1) ** 0.5
                theta = np.random.uniform(0, 2*np.pi)
                x += r * np.cos(theta)
                z = r * np.sin(theta)

                color = np.array([0.0, 0.65, 0.95, 0.7])

                targets.append(ParticleTarget(
                    position=np.array([x, y, z]),
                    color=color,
                    size=0.0025,
                    glow=0.6
                ))

        # LEGS (60K each = 120K total)
        for side in [-1, 1]:
            for _ in range(60000):
                y = np.random.uniform(0.0, 0.95)  # Ground to hips

                # Leg separation
                x_base = side * 0.1
                z_offset = np.random.uniform(-0.08, 0.08)

                # Leg thickness
                r = 0.05 * np.random.uniform(0, 1) ** 0.5
                theta = np.random.uniform(0, 2*np.pi)
                x = x_base + r * np.cos(theta)
                z = z_offset + r * np.sin(theta)

                # Darker blue at legs
                color = np.array([0.0, 0.3, 0.7, 0.7])

                targets.append(ParticleTarget(
                    position=np.array([x, y, z]),
                    color=color,
                    size=0.003,
                    glow=0.5
                ))

        # DATA SYMBOLS (75K particles - scrolling code overlay)
        for _ in range(spec.data_symbols):
            # Random position around body
            x = np.random.uniform(-0.5, 0.5)
            y = np.random.uniform(0.5, 1.8)
            z = np.random.uniform(-0.3, 0.3)

            # Bright cyan/white for symbols
            color = np.array([0.7, 0.9, 1.0, 0.5])

            targets.append(ParticleTarget(
                position=np.array([x, y, z]),
                color=color,
                size=0.002,
                glow=0.9
            ))

        logger.info("Generated Cortana form: %d particles", len(targets))
        return targets

    def _apply_cortana_animation(self, base_targets: List[ParticleTarget]) -> List[ParticleTarget]:
        """Apply animation to Cortana form (breathing, idle sway)."""
        t = time.time()

        # Breathing (subtle chest expansion)
        breath_phase = np.sin(2 * np.pi * self.cortana_spec.breathing_rate * t)
        breath_amount = breath_phase * 0.01

        # Idle sway
        sway_phase = np.sin(2 * np.pi * 0.15 * t)  # 0.15 Hz sway
        sway_x = sway_phase * self.cortana_spec.idle_sway_amount

        animated = []
        for target in base_targets:
            pos = target.position.copy()

            # Apply breathing to torso particles
            if 0.95 < pos[1] < 1.55:
                scale = 1.0 + breath_amount
                pos[0] *= scale
                pos[2] *= scale

            # Apply sway to upper body
            if pos[1] > 0.8:
                pos[0] += sway_x * (pos[1] - 0.8) / 1.0

            animated.append(ParticleTarget(
                position=pos,
                color=target.color,
                size=target.size,
                glow=target.glow
            ))

        return animated

    def _get_environment_targets(self, camera_data: Optional[Dict],
                                sensor_data: Optional[Dict]) -> List[ParticleTarget]:
        """
        Generate particle targets for 3D environment reconstruction.

        This is a placeholder - full implementation would:
        1. Process camera depth/RGB data
        2. Build 3D voxel map
        3. Use sensor fusion for unseen areas
        4. Apply inference/imagination for blind spots
        5. Generate particle positions matching environment

        Args:
            camera_data: Camera/vision data
            sensor_data: Additional sensor data

        Returns:
            List of particle targets forming environment
        """
        # TODO: Implement full 3D reconstruction pipeline
        # For now, generate placeholder environment (simple grid/cloud)

        targets = []
        spec = self.environment_spec

        # Generate particles in voxel grid around origin
        particles_per_axis = int(self.total_particles ** (1/3))

        for i in range(self.total_particles):
            # Random position in environment space
            x = np.random.uniform(-spec.max_range, spec.max_range)
            y = np.random.uniform(0, spec.max_range)
            z = np.random.uniform(-spec.max_range, spec.max_range)

            # Realistic colors (gray/brown for now)
            color = np.array([0.5, 0.5, 0.5, 0.6])

            targets.append(ParticleTarget(
                position=np.array([x, y, z]),
                color=color,
                size=0.01,
                glow=0.2
            ))

        return targets

    def force_mode(self, mode: VisualizationMode, duration: float = 2.0):
        """
        Force specific visualization mode (override context).

        Args:
            mode: Mode to switch to
            duration: Transition duration in seconds
        """
        self.transition_duration = duration
        self._start_transition(mode)

    def get_current_mode(self) -> VisualizationMode:
        """Get current visualization mode."""
        return self.current_mode

    def get_blend_weights(self) -> Tuple[float, float]:
        """
        Get current blend weights.

        Returns:
            Tuple of (cortana_weight, environment_weight)
        """
        return self.cortana_weight, self.environment_weight


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create morphing controller
    controller = MorphingController(total_particles=500000)

    print("\nMorphing Controller Test\n" + "=" * 60)

    # Test context-based mode selection
    contexts = [
        {'user_speaking': True, 'user_present': True},
        {'observing_environment': True, 'user_present': False},
        {'user_interaction': False, 'danger_detected': True},
        {'emotion': {'state': 'curious'}},
    ]

    for i, ctx in enumerate(contexts):
        mode = controller.update(ctx)
        cortana_w, env_w = controller.get_blend_weights()

        print(f"\nContext {i+1}: {ctx}")
        print(f"  Mode: {mode.value}")
        print(f"  Weights: Cortana={cortana_w:.2f}, Environment={env_w:.2f}")

    # Test particle generation
    print("\n\nGenerating particle targets...")
    targets = controller.get_particle_targets()
    print(f"Generated {len(targets)} particle targets")

    # Sample some targets
    print("\nSample particles:")
    for i in [0, 100000, 250000, 400000]:
        t = targets[i]
        print(f"  Particle {i}: pos=({t.position[0]:.2f}, {t.position[1]:.2f}, {t.position[2]:.2f}), "
              f"color=({t.color[0]:.2f}, {t.color[1]:.2f}, {t.color[2]:.2f})")
