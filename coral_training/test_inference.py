#!/usr/bin/env python3
"""
Test Edge TPU Model Inference

Tests the compiled Edge TPU model for particle generation.
Uses TensorFlow Lite with Edge TPU delegate (modern approach).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    logger.error("tflite_runtime not installed")
    logger.error("Install with: pip install tflite-runtime")
    sys.exit(1)


class CoralInferenceTester:
    """Test Edge TPU model inference performance."""

    def __init__(self, model_path: str):
        """
        Initialize inference tester.

        Args:
            model_path: Path to Edge TPU compiled model (*_edgetpu.tflite)
        """
        self.model_path = Path(model_path)
        self.interpreter = None
        self.input_details = None
        self.output_details = None

        # Test states
        self.states = ['idle', 'listening', 'processing', 'speaking', 'executing']

    def load_model(self) -> bool:
        """
        Load Edge TPU model with TFLite Interpreter.

        Returns:
            True if successful, False otherwise
        """
        if not self.model_path.exists():
            logger.error(f"Model not found: {self.model_path}")
            return False

        logger.info(f"Loading model: {self.model_path}")

        try:
            # Try to load Edge TPU delegate
            delegates = []
            try:
                # Load Edge TPU delegate
                edgetpu_delegate = tflite.load_delegate('libedgetpu.so.1')
                delegates = [edgetpu_delegate]
                logger.info("✓ Edge TPU delegate loaded")
            except Exception as e:
                logger.warning(f"Could not load Edge TPU delegate: {e}")
                logger.warning("Running on CPU (will be slow)")

            # Create interpreter
            self.interpreter = tflite.Interpreter(
                model_path=str(self.model_path),
                experimental_delegates=delegates
            )

            # Allocate tensors
            self.interpreter.allocate_tensors()

            # Get input/output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            logger.info("Model loaded successfully")
            logger.info(f"Input shape: {self.input_details[0]['shape']}")
            logger.info(f"Output shape: {self.output_details[0]['shape']}")

            return True

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False

    def encode_state_sensors(self, state: str, sensors: dict) -> np.ndarray:
        """
        Encode state and sensors as input tensor.

        Args:
            state: Current state ('idle', 'listening', etc.)
            sensors: Sensor data dict

        Returns:
            Input tensor (1, 9) float32
        """
        # State one-hot encoding (5 states)
        state_encoding = np.zeros(5, dtype=np.float32)
        state_idx = self.states.index(state)
        state_encoding[state_idx] = 1.0

        # Sensor encoding (4 values)
        sensor_encoding = np.array([
            sensors.get('temperature', 20.0) / 30.0,  # Normalize 0-30°C
            sensors.get('humidity', 50.0) / 100.0,     # Normalize 0-100%
            1.0 if sensors.get('motion', False) else 0.0,
            sensors.get('audio_level', 0.0),
        ], dtype=np.float32)

        # Combine
        input_tensor = np.concatenate([state_encoding, sensor_encoding])
        return input_tensor.reshape(1, -1)

    def run_inference(self, state: str, sensors: dict) -> np.ndarray:
        """
        Run inference to generate particle positions.

        Args:
            state: Current state
            sensors: Sensor data

        Returns:
            Particle positions (num_particles, 3) float32
        """
        # Encode input
        input_tensor = self.encode_state_sensors(state, sensors)

        # Set input tensor
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)

        # Run inference
        start_time = time.time()
        self.interpreter.invoke()
        inference_time = (time.time() - start_time) * 1000  # Convert to ms

        # Get output tensor
        output_tensor = self.interpreter.get_tensor(self.output_details[0]['index'])

        logger.info(f"Inference time: {inference_time:.2f} ms")

        return output_tensor[0]  # Remove batch dimension

    def benchmark(self, num_iterations: int = 100):
        """
        Benchmark inference performance.

        Args:
            num_iterations: Number of inference runs
        """
        logger.info("=" * 70)
        logger.info("Benchmark: Edge TPU Inference Performance")
        logger.info("=" * 70)

        # Test cases
        test_cases = [
            ('idle', {'temperature': 22.0, 'humidity': 45.0, 'motion': False, 'audio_level': 0.0}),
            ('listening', {'temperature': 23.0, 'humidity': 48.0, 'motion': True, 'audio_level': 0.6}),
            ('processing', {'temperature': 25.0, 'humidity': 50.0, 'motion': False, 'audio_level': 0.3}),
            ('speaking', {'temperature': 24.0, 'humidity': 47.0, 'motion': False, 'audio_level': 0.8}),
            ('executing', {'temperature': 26.0, 'humidity': 52.0, 'motion': True, 'audio_level': 0.5}),
        ]

        times = []

        for i in range(num_iterations):
            # Rotate through test cases
            state, sensors = test_cases[i % len(test_cases)]

            # Encode input
            input_tensor = self.encode_state_sensors(state, sensors)

            # Set input
            self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)

            # Time inference
            start_time = time.time()
            self.interpreter.invoke()
            inference_time = (time.time() - start_time) * 1000

            times.append(inference_time)

            if (i + 1) % 20 == 0:
                logger.info(f"Progress: {i + 1}/{num_iterations} iterations")

        # Calculate statistics
        times = np.array(times)
        mean_time = np.mean(times)
        std_time = np.std(times)
        min_time = np.min(times)
        max_time = np.max(times)
        fps = 1000.0 / mean_time

        logger.info("=" * 70)
        logger.info("Benchmark Results:")
        logger.info(f"Iterations: {num_iterations}")
        logger.info(f"Mean inference time: {mean_time:.2f} ± {std_time:.2f} ms")
        logger.info(f"Min/Max: {min_time:.2f} / {max_time:.2f} ms")
        logger.info(f"Estimated FPS: {fps:.1f}")
        logger.info("=" * 70)

        # Performance assessment
        if fps >= 60:
            logger.info("✓ EXCELLENT: Suitable for real-time 60 FPS visualization")
        elif fps >= 30:
            logger.info("✓ GOOD: Suitable for 30 FPS visualization")
        elif fps >= 15:
            logger.warning("⚠ ACCEPTABLE: Limited to 15-30 FPS")
        else:
            logger.error("✗ POOR: Too slow for real-time visualization")
            logger.error("Likely running on CPU - check Edge TPU delegate loading")

    def test_single_inference(self):
        """Test single inference with detailed output."""
        logger.info("=" * 70)
        logger.info("Single Inference Test")
        logger.info("=" * 70)

        state = 'processing'
        sensors = {
            'temperature': 24.0,
            'humidity': 48.0,
            'motion': True,
            'audio_level': 0.7
        }

        logger.info(f"State: {state}")
        logger.info(f"Sensors: {sensors}")

        # Run inference
        particles = self.run_inference(state, sensors)

        logger.info(f"Generated particles shape: {particles.shape}")
        logger.info(f"Particle position range:")
        logger.info(f"  X: [{np.min(particles[:, 0]):.3f}, {np.max(particles[:, 0]):.3f}]")
        logger.info(f"  Y: [{np.min(particles[:, 1]):.3f}, {np.max(particles[:, 1]):.3f}]")
        logger.info(f"  Z: [{np.min(particles[:, 2]):.3f}, {np.max(particles[:, 2]):.3f}]")

        # Sample particles
        logger.info("Sample particle positions:")
        for i in range(min(5, len(particles))):
            logger.info(f"  Particle {i}: ({particles[i, 0]:.3f}, {particles[i, 1]:.3f}, {particles[i, 2]:.3f})")


def main():
    """Run inference tests."""
    logger.info("=" * 70)
    logger.info("Coral TPU Model Inference Test")
    logger.info("=" * 70)

    # Find model
    models_dir = Path(__file__).parent / 'models'

    # Look for Edge TPU model
    edgetpu_models = list(models_dir.glob('*_edgetpu.tflite'))

    if not edgetpu_models:
        logger.error("No Edge TPU model found")
        logger.error(f"Expected location: {models_dir}/*_edgetpu.tflite")
        logger.error("")
        logger.error("Steps to compile model:")
        logger.error("1. Train model: python3 coral_training/train_model.py")
        logger.error("2. Compile on x86_64/Colab: See coral_training/COLAB_COMPILE.md")
        logger.error("3. Transfer compiled *_edgetpu.tflite to models/")
        return 1

    model_path = edgetpu_models[0]
    logger.info(f"Using model: {model_path}")

    # Create tester
    tester = CoralInferenceTester(str(model_path))

    # Load model
    if not tester.load_model():
        return 1

    # Run single inference test
    tester.test_single_inference()

    # Run benchmark
    logger.info("")
    tester.benchmark(num_iterations=100)

    logger.info("=" * 70)
    logger.info("Test complete!")
    logger.info("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
