#!/usr/bin/env python3
"""
Binary Protocol for Sentient Core WebSocket Communication

Replaces JSON serialization with efficient binary format:
- Header: 64 bytes (metadata)
- Payload: 120KB (10,000 particles × 3 coordinates × 4 bytes float32)

Total: ~120KB vs 500KB+ JSON (75% reduction)
Performance: <1ms serialization vs 30-70ms JSON
"""

import struct
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger("binary_protocol")

# Protocol version
PROTOCOL_VERSION = 1

# Message types
MSG_TYPE_PARTICLES = 0x01
MSG_TYPE_METADATA = 0x02
MSG_TYPE_HEARTBEAT = 0x03

# Header format (64 bytes total)
# Format: <version><type><frame_id><timestamp_ms><particle_count><fps><inference_ms><total_ms><reserved>
# Breakdown: B(1) + B(1) + I(4) + Q(8) + I(4) + f(4) + f(4) + f(4) + 34x(34) = 64 bytes
HEADER_FORMAT = '<BBIQIfff34x'  # Little-endian
HEADER_SIZE = 64

class BinaryProtocol:
    """
    Binary protocol encoder/decoder for Sentient Core WebSocket messages.

    Message Structure:
    ┌──────────────┬────────────────────────────────────┐
    │   Header     │            Payload                 │
    │   64 bytes   │     120KB (10,000 × 3 × float32)  │
    └──────────────┴────────────────────────────────────┘

    Header Fields:
    - version (1 byte): Protocol version
    - msg_type (1 byte): Message type (particles, metadata, heartbeat)
    - frame_id (4 bytes): Frame counter
    - timestamp_ms (8 bytes): Timestamp in milliseconds
    - particle_count (4 bytes): Number of particles
    - fps (4 bytes float): Current FPS
    - inference_ms (4 bytes float): Inference time in milliseconds
    - total_ms (4 bytes float): Total frame time in milliseconds
    - reserved (34 bytes): Reserved for future use
    """

    @staticmethod
    def encode_particles(
        particles_3d: np.ndarray,
        frame_id: int,
        timestamp_ms: int,
        fps: float,
        inference_ms: float,
        total_ms: float
    ) -> bytes:
        """
        Encode particle data to binary format.

        Args:
            particles_3d: NumPy array of shape (N, 3) with float32 particle positions
            frame_id: Frame counter
            timestamp_ms: Timestamp in milliseconds
            fps: Frames per second
            inference_ms: Inference time in milliseconds
            total_ms: Total frame time in milliseconds

        Returns:
            Binary message ready to send via WebSocket
        """
        # Ensure particles are float32
        if particles_3d.dtype != np.float32:
            particles_3d = particles_3d.astype(np.float32)

        particle_count = particles_3d.shape[0]

        # Pack header
        header = struct.pack(
            HEADER_FORMAT,
            PROTOCOL_VERSION,       # version
            MSG_TYPE_PARTICLES,     # msg_type
            frame_id,               # frame_id
            timestamp_ms,           # timestamp_ms
            particle_count,         # particle_count
            fps,                    # fps
            inference_ms,           # inference_ms
            total_ms                # total_ms
            # reserved bytes added automatically by format
        )

        # Convert particles to bytes (much faster than JSON)
        payload = particles_3d.tobytes()

        # Combine header + payload
        message = header + payload

        logger.debug(
            f"Encoded particles: {particle_count} particles, "
            f"{len(message)} bytes (header: {len(header)}, payload: {len(payload)})"
        )

        return message

    @staticmethod
    def decode_particles(message: bytes) -> Tuple[Dict, np.ndarray]:
        """
        Decode binary particle message.

        Args:
            message: Binary message from WebSocket

        Returns:
            Tuple of (metadata_dict, particles_array)
        """
        if len(message) < HEADER_SIZE:
            raise ValueError(f"Message too short: {len(message)} bytes (expected >= {HEADER_SIZE})")

        # Unpack header
        header_data = struct.unpack(HEADER_FORMAT, message[:HEADER_SIZE])

        version = header_data[0]
        msg_type = header_data[1]
        frame_id = header_data[2]
        timestamp_ms = header_data[3]
        particle_count = header_data[4]
        fps = header_data[5]
        inference_ms = header_data[6]
        total_ms = header_data[7]

        if version != PROTOCOL_VERSION:
            raise ValueError(f"Unsupported protocol version: {version}")

        if msg_type != MSG_TYPE_PARTICLES:
            raise ValueError(f"Unexpected message type: {msg_type}")

        # Extract payload
        payload = message[HEADER_SIZE:]

        # Reconstruct particle array
        expected_size = particle_count * 3 * 4  # 3 floats × 4 bytes each
        if len(payload) != expected_size:
            raise ValueError(
                f"Payload size mismatch: {len(payload)} bytes "
                f"(expected {expected_size} for {particle_count} particles)"
            )

        particles_3d = np.frombuffer(payload, dtype=np.float32).reshape(particle_count, 3)

        metadata = {
            "frame_id": frame_id,
            "timestamp_ms": timestamp_ms,
            "particle_count": particle_count,
            "fps": fps,
            "inference_ms": inference_ms,
            "total_ms": total_ms
        }

        logger.debug(f"Decoded particles: {particle_count} particles, FPS: {fps:.1f}")

        return metadata, particles_3d

    @staticmethod
    def encode_heartbeat(timestamp_ms: int) -> bytes:
        """
        Encode heartbeat message (minimal overhead).

        Args:
            timestamp_ms: Timestamp in milliseconds

        Returns:
            Binary heartbeat message
        """
        header = struct.pack(
            HEADER_FORMAT,
            PROTOCOL_VERSION,
            MSG_TYPE_HEARTBEAT,
            0,  # frame_id (unused)
            timestamp_ms,
            0,  # particle_count (unused)
            0.0,  # fps (unused)
            0.0,  # inference_ms (unused)
            0.0   # total_ms (unused)
        )
        return header


# Benchmark function
if __name__ == "__main__":
    import time
    import json

    logging.basicConfig(level=logging.INFO)

    print("=== Binary Protocol Benchmark ===\n")

    # Create test data
    particles = np.random.random((10000, 3)).astype(np.float32)

    # Test binary encoding
    start = time.perf_counter()
    for _ in range(100):
        binary_msg = BinaryProtocol.encode_particles(
            particles,
            frame_id=1,
            timestamp_ms=1000,
            fps=60.0,
            inference_ms=2.5,
            total_ms=15.0
        )
    binary_time = (time.perf_counter() - start) / 100 * 1000  # ms

    # Test JSON encoding (old method)
    start = time.perf_counter()
    for _ in range(100):
        json_msg = json.dumps({
            "particles": particles.tolist(),
            "metadata": {
                "fps": 60.0,
                "inference_ms": 2.5,
                "total_ms": 15.0
            }
        })
    json_time = (time.perf_counter() - start) / 100 * 1000  # ms

    # Results
    print(f"Binary Encoding:")
    print(f"  Time: {binary_time:.2f}ms per frame")
    print(f"  Size: {len(binary_msg):,} bytes ({len(binary_msg) / 1024:.1f} KB)")
    print()
    print(f"JSON Encoding (old):")
    print(f"  Time: {json_time:.2f}ms per frame")
    print(f"  Size: {len(json_msg):,} bytes ({len(json_msg) / 1024:.1f} KB)")
    print()
    print(f"Performance Improvement:")
    print(f"  Speed: {json_time / binary_time:.1f}x faster")
    print(f"  Size: {len(json_msg) / len(binary_msg):.1f}x smaller")
    print()

    # Test decode
    metadata, decoded_particles = BinaryProtocol.decode_particles(binary_msg)
    print(f"Decode verification:")
    print(f"  Metadata: {metadata}")
    print(f"  Particles match: {np.allclose(particles, decoded_particles)}")
