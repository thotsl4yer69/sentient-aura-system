#!/usr/bin/env python3
"""
Particle Physics Engine - Makes 10,000 Particles ALIVE
=======================================================

Implements optimized particle motion algorithms for ARM64 (Raspberry Pi 5).
Uses spatial hashing for O(n) performance instead of O(n²).

Particles exhibit emergent flocking behavior based on cognitive state:
- Cohesion: Attraction to center of mass
- Separation: Repulsion from neighbors
- Alignment: Velocity matching
- Wander: Random exploration
"""

import numpy as np
from typing import Tuple, Dict, List, Optional
import time


class ParticlePhysicsEngine:
    """
    High-performance particle physics for 10,000 particles @ 60 FPS.

    Optimized for ARM64 architecture with NumPy vectorization and
    spatial hashing for neighbor queries.
    """

    def __init__(self, num_particles: int = 10000):
        """
        Initialize particle physics engine.

        Args:
            num_particles: Number of particles to simulate (default 10000)
        """
        self.num_particles = num_particles

        # Particle state (positions and velocities in 3D space)
        self.positions = np.random.rand(num_particles, 3) * 2 - 1  # Range [-1, 1]
        self.velocities = np.zeros((num_particles, 3), dtype=np.float32)

        # Spatial hashing for efficient neighbor queries
        self.grid_size = 0.15  # Size of hash grid cells
        self.neighbor_radius = 0.2  # Neighbor search radius

        # Performance tracking
        self.frame_count = 0
        self.total_time = 0.0

    def calculate_forces(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
        cohesion: float,
        separation: float,
        alignment: float,
        wander: float,
        breath_factor: float = 0.0
    ) -> np.ndarray:
        """
        Calculate force vectors for all particles using boid-like flocking.

        Args:
            positions: Particle positions (N, 3)
            velocities: Particle velocities (N, 3)
            cohesion: Cohesion strength (0-1)
            separation: Separation strength (0-1)
            alignment: Alignment strength (0-1)
            wander: Wander strength (0-1)
            breath_factor: Breathing oscillation (-1 to 1)

        Returns:
            Force vectors (N, 3)
        """
        forces = np.zeros_like(positions)

        # 1. COHESION FORCE - Attraction to center of mass
        if cohesion > 0:
            center = np.mean(positions, axis=0)
            cohesion_force = (center - positions) * cohesion * 0.5
            forces += cohesion_force

        # 2. SEPARATION FORCE - Repulsion from neighbors (spatial hashing)
        if separation > 0:
            separation_force = self._calculate_separation_spatial_hash(
                positions, separation
            )
            forces += separation_force

        # 3. ALIGNMENT FORCE - Velocity matching with neighbors
        if alignment > 0:
            alignment_force = self._calculate_alignment(
                positions, velocities, alignment
            )
            forces += alignment_force

        # 4. WANDER FORCE - Random exploration
        if wander > 0:
            wander_force = (np.random.randn(*positions.shape) - 0.5) * wander * 0.3
            forces += wander_force

        # 5. BREATHING FORCE - Organic pulsing
        if abs(breath_factor) > 0.01:
            breath_force = positions * breath_factor * 0.05
            forces += breath_force

        # 6. BOUNDARY FORCE - Soft boundary constraints
        boundary_force = self._calculate_boundary_force(positions)
        forces += boundary_force

        return forces

    def _calculate_separation_spatial_hash(
        self,
        positions: np.ndarray,
        strength: float
    ) -> np.ndarray:
        """
        Calculate separation force using spatial hashing.

        This is O(n) instead of O(n²) - critical for 10,000 particles!

        Args:
            positions: Particle positions
            strength: Separation strength

        Returns:
            Separation force vectors
        """
        forces = np.zeros_like(positions)

        # Build spatial hash grid
        grid_coords = (positions / self.grid_size).astype(int)
        grid: Dict[Tuple[int, int, int], List[int]] = {}

        for i, coord in enumerate(grid_coords):
            key = tuple(coord)
            if key not in grid:
                grid[key] = []
            grid[key].append(i)

        # Calculate separation for each particle
        for i in range(len(positions)):
            neighbor_force = np.zeros(3)
            count = 0

            # Check adjacent cells (3x3x3 = 27 cells)
            gx, gy, gz = grid_coords[i]
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        key = (gx + dx, gy + dy, gz + dz)
                        if key in grid:
                            for j in grid[key]:
                                if i != j:
                                    diff = positions[i] - positions[j]
                                    dist = np.linalg.norm(diff)
                                    if 0 < dist < self.neighbor_radius:
                                        # Inverse square law for separation
                                        neighbor_force += diff / (dist * dist + 0.01)
                                        count += 1

            if count > 0:
                forces[i] = (neighbor_force / count) * strength

        return forces

    def _calculate_alignment(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
        strength: float
    ) -> np.ndarray:
        """
        Calculate alignment force (velocity matching).

        Simplified implementation using global average for performance.

        Args:
            positions: Particle positions
            velocities: Particle velocities
            strength: Alignment strength

        Returns:
            Alignment force vectors
        """
        # Global average velocity (fast approximation)
        avg_velocity = np.mean(velocities, axis=0)
        alignment_force = (avg_velocity - velocities) * strength * 0.3
        return alignment_force

    def _calculate_boundary_force(self, positions: np.ndarray) -> np.ndarray:
        """
        Calculate soft boundary force to keep particles in view.

        Uses exponential force near boundaries for smooth containment.

        Args:
            positions: Particle positions

        Returns:
            Boundary force vectors
        """
        boundary_limit = 0.95
        boundary_strength = 0.2

        forces = np.zeros_like(positions)

        # For each axis, apply force when near boundary
        for axis in range(3):
            # Particles past +boundary_limit
            mask_pos = positions[:, axis] > boundary_limit
            forces[mask_pos, axis] -= (positions[mask_pos, axis] - boundary_limit) * boundary_strength

            # Particles past -boundary_limit
            mask_neg = positions[:, axis] < -boundary_limit
            forces[mask_neg, axis] -= (positions[mask_neg, axis] + boundary_limit) * boundary_strength

        return forces

    def update(
        self,
        dt: float,
        cohesion: float,
        separation: float,
        alignment: float,
        wander: float,
        breath_factor: float,
        speed_multiplier: float = 1.0,
        damping: float = 0.98
    ) -> np.ndarray:
        """
        Update particle positions and velocities.

        Args:
            dt: Delta time in seconds
            cohesion: Cohesion strength (0-1)
            separation: Separation strength (0-1)
            alignment: Alignment strength (0-1)
            wander: Wander strength (0-1)
            breath_factor: Breathing oscillation (-1 to 1)
            speed_multiplier: Overall speed scaling
            damping: Velocity damping factor (0-1)

        Returns:
            Updated particle positions
        """
        start_time = time.time()

        # Calculate forces
        forces = self.calculate_forces(
            self.positions,
            self.velocities,
            cohesion,
            separation,
            alignment,
            wander,
            breath_factor
        )

        # Update velocities (F = ma, assuming m=1)
        self.velocities += forces * dt * speed_multiplier

        # Apply damping
        self.velocities *= damping

        # Clamp velocity magnitude
        max_speed = 2.0 * speed_multiplier
        speeds = np.linalg.norm(self.velocities, axis=1, keepdims=True)
        speeds = np.clip(speeds, 0, max_speed)
        velocity_directions = self.velocities / (np.linalg.norm(self.velocities, axis=1, keepdims=True) + 1e-8)
        self.velocities = velocity_directions * speeds

        # Update positions
        self.positions += self.velocities * dt

        # Hard clamp to boundaries (safety)
        self.positions = np.clip(self.positions, -1.0, 1.0)

        # Performance tracking
        self.frame_count += 1
        self.total_time += time.time() - start_time

        return self.positions

    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get performance statistics.

        Returns:
            Dictionary with FPS and average frame time
        """
        if self.total_time > 0:
            avg_frame_time = self.total_time / self.frame_count
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        else:
            avg_frame_time = 0
            fps = 0

        return {
            "fps": fps,
            "avg_frame_time_ms": avg_frame_time * 1000,
            "total_frames": self.frame_count
        }

    def reset_positions(self, distribution: str = "sphere"):
        """
        Reset particle positions to initial distribution.

        Args:
            distribution: Distribution type ("sphere", "cube", "humanoid")
        """
        if distribution == "sphere":
            # Uniform distribution in sphere
            phi = np.random.rand(self.num_particles) * 2 * np.pi
            costheta = np.random.rand(self.num_particles) * 2 - 1
            u = np.random.rand(self.num_particles)

            theta = np.arccos(costheta)
            r = u ** (1/3) * 0.8  # Sphere radius 0.8

            self.positions[:, 0] = r * np.sin(theta) * np.cos(phi)
            self.positions[:, 1] = r * np.sin(theta) * np.sin(phi)
            self.positions[:, 2] = r * np.cos(theta)

        elif distribution == "cube":
            # Uniform distribution in cube
            self.positions = np.random.rand(self.num_particles, 3) * 2 - 1

        elif distribution == "humanoid":
            # Humanoid silhouette distribution
            self._create_humanoid_distribution()

        # Reset velocities
        self.velocities = np.zeros_like(self.positions)

    def _create_humanoid_distribution(self):
        """
        Create humanoid silhouette distribution (Cortana-inspired).

        Particles distributed in rough humanoid proportions:
        - Head: 10% of particles
        - Torso: 30% of particles
        - Arms: 20% of particles
        - Legs: 20% of particles
        - Aura: 20% of particles
        """
        n = self.num_particles

        # Head (sphere at top)
        head_particles = int(n * 0.1)
        head_pos = self._sphere_distribution(head_particles, radius=0.15)
        head_pos[:, 1] += 0.6  # Move to top

        # Torso (ellipsoid)
        torso_particles = int(n * 0.3)
        torso_pos = self._ellipsoid_distribution(
            torso_particles, rx=0.25, ry=0.4, rz=0.2
        )
        torso_pos[:, 1] += 0.1  # Center

        # Arms (cylinders)
        arm_particles = int(n * 0.2)
        arms_pos = self._arm_distribution(arm_particles)

        # Legs (cylinders)
        leg_particles = int(n * 0.2)
        legs_pos = self._leg_distribution(leg_particles)

        # Aura (surrounding particles)
        aura_particles = n - (head_particles + torso_particles + arm_particles + leg_particles)
        aura_pos = self._sphere_distribution(aura_particles, radius=1.0) * 0.8

        # Combine all parts
        self.positions = np.vstack([
            head_pos,
            torso_pos,
            arms_pos,
            legs_pos,
            aura_pos
        ])

    def _sphere_distribution(self, n: int, radius: float = 1.0) -> np.ndarray:
        """Generate uniform distribution in sphere."""
        phi = np.random.rand(n) * 2 * np.pi
        costheta = np.random.rand(n) * 2 - 1
        u = np.random.rand(n)

        theta = np.arccos(costheta)
        r = u ** (1/3) * radius

        positions = np.zeros((n, 3))
        positions[:, 0] = r * np.sin(theta) * np.cos(phi)
        positions[:, 1] = r * np.sin(theta) * np.sin(phi)
        positions[:, 2] = r * np.cos(theta)

        return positions

    def _ellipsoid_distribution(
        self,
        n: int,
        rx: float = 1.0,
        ry: float = 1.0,
        rz: float = 1.0
    ) -> np.ndarray:
        """Generate uniform distribution in ellipsoid."""
        pos = self._sphere_distribution(n, radius=1.0)
        pos[:, 0] *= rx
        pos[:, 1] *= ry
        pos[:, 2] *= rz
        return pos

    def _arm_distribution(self, n: int) -> np.ndarray:
        """Generate arm distribution (two cylinders)."""
        half = n // 2
        arms = np.zeros((n, 3))

        # Left arm
        arms[:half, 0] = -0.4 + np.random.randn(half) * 0.05
        arms[:half, 1] = 0.2 - np.random.rand(half) * 0.5
        arms[:half, 2] = np.random.randn(half) * 0.05

        # Right arm
        arms[half:, 0] = 0.4 + np.random.randn(n - half) * 0.05
        arms[half:, 1] = 0.2 - np.random.rand(n - half) * 0.5
        arms[half:, 2] = np.random.randn(n - half) * 0.05

        return arms

    def _leg_distribution(self, n: int) -> np.ndarray:
        """Generate leg distribution (two cylinders)."""
        half = n // 2
        legs = np.zeros((n, 3))

        # Left leg
        legs[:half, 0] = -0.15 + np.random.randn(half) * 0.05
        legs[:half, 1] = -0.3 - np.random.rand(half) * 0.5
        legs[:half, 2] = np.random.randn(half) * 0.05

        # Right leg
        legs[half:, 0] = 0.15 + np.random.randn(n - half) * 0.05
        legs[half:, 1] = -0.3 - np.random.rand(n - half) * 0.5
        legs[half:, 2] = np.random.randn(n - half) * 0.05

        return legs

    def get_positions_for_distribution(self, distribution: str = "humanoid") -> np.ndarray:
        """
        Get particle positions initialized to specific distribution.

        Args:
            distribution: Distribution type ("sphere", "cube", "humanoid")

        Returns:
            Particle positions array (N, 3)
        """
        # Initialize to distribution if not already done
        if distribution == "humanoid" and np.allclose(self.positions, 0):
            self.reset_positions("humanoid")
        elif distribution == "sphere" and np.allclose(self.positions, 0):
            self.reset_positions("sphere")

        return self.positions.copy()


# === TESTING ===

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PARTICLE PHYSICS ENGINE TEST")
    print("=" * 70)

    # Create engine with 10,000 particles
    engine = ParticlePhysicsEngine(num_particles=10000)

    print(f"\n✓ Particle Physics Engine initialized")
    print(f"  Particles: {engine.num_particles}")
    print(f"  Grid size: {engine.grid_size}")
    print(f"  Neighbor radius: {engine.neighbor_radius}")

    # Test different distributions
    distributions = ["sphere", "cube", "humanoid"]
    for dist in distributions:
        print(f"\nTesting {dist} distribution...")
        engine.reset_positions(dist)
        mean = np.mean(engine.positions, axis=0)
        std = np.std(engine.positions, axis=0)
        print(f"  Mean position: ({mean[0]:.3f}, {mean[1]:.3f}, {mean[2]:.3f})")
        print(f"  Std deviation: ({std[0]:.3f}, {std[1]:.3f}, {std[2]:.3f})")

    # Performance test
    print(f"\nPerformance test (100 frames)...")
    engine.reset_positions("sphere")

    for i in range(100):
        engine.update(
            dt=1/60,  # 60 FPS
            cohesion=0.5,
            separation=0.3,
            alignment=0.4,
            wander=0.2,
            breath_factor=np.sin(i * 0.1),
            speed_multiplier=1.0
        )

    stats = engine.get_performance_stats()
    print(f"\n✓ Performance test complete")
    print(f"  Average FPS: {stats['fps']:.1f}")
    print(f"  Average frame time: {stats['avg_frame_time_ms']:.2f}ms")
    print(f"  Total frames: {stats['total_frames']}")

    # Verify Raspberry Pi 5 can hit 60 FPS
    if stats['fps'] >= 60:
        print(f"\n✅ PERFORMANCE TARGET MET (≥60 FPS on ARM64)")
    else:
        print(f"\n⚠️  Performance below target ({stats['fps']:.1f} < 60 FPS)")

    print("\n" + "=" * 70)
