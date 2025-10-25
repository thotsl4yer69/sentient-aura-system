#!/usr/bin/env python3
"""
Coral Edge TPU Inference Test Script

Tests the compiled Edge TPU model for Sentient Core particle visualization.
Measures inference speed and verifies Edge TPU acceleration.

Requirements:
- Coral USB Accelerator connected
- Compiled _edgetpu.tflite model
- pycoral library installed

Expected Performance:
- Inference time: 2-5ms per frame
- FPS capability: 200+ FPS
- 100% Edge TPU operation mapping
"""

import sys
import os
import time
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pycoral.utils import edgetpu
    from pycoral.adapters import common
    import tflite_runtime.interpreter as tflite
    PYCORAL_AVAILABLE = True
except ImportError:
    logger.warning("PyCoral not available - will test with TFLite runtime only")
    import tflite_runtime.interpreter as tflite
    PYCORAL_AVAILABLE = False


class CoralInferenceTester:
    """Test Edge TPU inference performance."""

    def __init__(self, model_path: Path):
        """
        Initialize tester.

        Args:
            model_path: Path to .tflite or _edgetpu.tflite model
        """
        self.model_path = Path(model_path)
        self.is_edgetpu_model = '_edgetpu' in self.model_path.name

        self.num_features = 68
        self.num_particles = 10000

    def check_edgetpu_availability(self):
        """Check if Edge TPU is available."""
        if not PYCORAL_AVAILABLE:
            logger.error("PyCoral not installed - cannot use Edge TPU acceleration")
            logger.info("Install with: pip install pycoral")
            return False

        try:
            tpus = edgetpu.list_edge_tpus()
            if not tpus:
                logger.warning("No Edge TPU devices found!")
                logger.info("Check USB connection: lsusb | grep 'Global Unichip'")
                return False

            logger.info(f"✓ Found {len(tpus)} Edge TPU device(s):")
            for i, tpu in enumerate(tpus):
                logger.info(f"  [{i}] {tpu}")

            return True

        except Exception as e:
            logger.error(f"Error checking Edge TPU: {e}")
            return False

    def load_model(self):
        """Load model with appropriate interpreter."""
        logger.info(f"Loading model: {self.model_path.name}")

        if self.is_edgetpu_model and PYCORAL_AVAILABLE:
            logger.info("  Using Edge TPU delegate")
            try:
                interpreter = edgetpu.make_interpreter(str(self.model_path))
            except Exception as e:
                logger.error(f"Failed to load with Edge TPU: {e}")
                logger.info("Falling back to CPU...")
                interpreter = tflite.Interpreter(model_path=str(self.model_path))
        else:
            logger.info("  Using CPU (TFLite runtime)")
            interpreter = tflite.Interpreter(model_path=str(self.model_path))

        interpreter.allocate_tensors()

        # Get input/output details
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        logger.info("\n" + "="*70)
        logger.info("MODEL DETAILS")
        logger.info("="*70)
        logger.info(f"Input:")
        logger.info(f"  Shape: {input_details[0]['shape']}")
        logger.info(f"  Type:  {input_details[0]['dtype']}")
        logger.info(f"Output:")
        logger.info(f"  Shape: {output_details[0]['shape']}")
        logger.info(f"  Type:  {output_details[0]['dtype']}")
        logger.info("="*70 + "\n")

        return interpreter, input_details, output_details

    def generate_test_input(self) -> np.ndarray:
        """
        Generate test input tensor.

        Creates a sample cognitive/sensory state for testing.

        Returns:
            Input tensor of shape (1, 68)
        """
        # Example: "creative_problem_solving" scenario
        test_input = np.array([
            1.0,   # cognitive_state: reasoning
            0.9,   # reasoning_depth: deep
            0.3,   # uncertainty_level: moderate
            0.85,  # cognitive_load: high
            0.9,   # creativity_mode: very creative
            0.8,   # attention_focus: focused
            0.0,   # learning_active
            0.5,   # memory_access_depth
            # Environmental sensors (10 features)
            0.55, 0.45, 0.5, 0.6, 0.3, 0.0, 0.0, 0.0, 0.8, 0.5,
            # RF spectrum (12 features)
            1.0, 0.0, 0.0, 0.7, 0.4, 0.6, 0.5, 0.0, 0.7, 0.0, 0.8, 0.3,
            # Visual processing (10 features)
            1.0, 0.8, 0.5, 0.0, 0.5, 0.6, 0.3, 0.8, 0.7, 0.4,
            # Audio (6 features)
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
            # Interaction (7 features)
            0.0, 0.8, 0.4, 0.5, 0.3, 0.7, 0.3,
            # Network (6 features)
            1.0, 0.5, 0.7, 0.4, 0.2, 0.3,
            # System (4 features)
            0.6, 0.5, 0.4, 0.3,
            # Security (5 features)
            0.0, 0.0, 0.0, 0.0, 0.0
        ], dtype=np.float32)

        assert len(test_input) == 68, f"Expected 68 features, got {len(test_input)}"

        return test_input.reshape(1, 68)

    def run_inference(self,
                     interpreter,
                     input_details,
                     output_details,
                     input_data: np.ndarray) -> np.ndarray:
        """
        Run single inference.

        Args:
            interpreter: TFLite interpreter
            input_details: Input tensor details
            output_details: Output tensor details
            input_data: Input tensor

        Returns:
            Output particle positions
        """
        # Set input
        interpreter.set_tensor(input_details[0]['index'], input_data)

        # Run inference
        interpreter.invoke()

        # Get output
        output_data = interpreter.get_tensor(output_details[0]['index'])

        return output_data

    def benchmark(self, interpreter, input_details, output_details, num_iterations: int = 100):
        """
        Benchmark inference performance.

        Args:
            interpreter: TFLite interpreter
            input_details: Input tensor details
            output_details: Output tensor details
            num_iterations: Number of test iterations
        """
        logger.info("\n" + "="*70)
        logger.info("PERFORMANCE BENCHMARK")
        logger.info("="*70)

        # Generate test input
        test_input = self.generate_test_input()

        # Warmup
        logger.info("Warming up (5 iterations)...")
        for _ in range(5):
            self.run_inference(interpreter, input_details, output_details, test_input)

        # Benchmark
        logger.info(f"Running {num_iterations} iterations...")

        timings = []
        for i in range(num_iterations):
            start = time.perf_counter()
            output = self.run_inference(interpreter, input_details, output_details, test_input)
            end = time.perf_counter()

            elapsed_ms = (end - start) * 1000
            timings.append(elapsed_ms)

            if (i + 1) % 20 == 0:
                avg_ms = np.mean(timings[-20:])
                logger.info(f"  Iteration {i+1}/{num_iterations}: {avg_ms:.2f}ms avg (last 20)")

        # Statistics
        timings = np.array(timings)
        mean_ms = np.mean(timings)
        std_ms = np.std(timings)
        min_ms = np.min(timings)
        max_ms = np.max(timings)
        median_ms = np.median(timings)
        fps = 1000 / mean_ms

        logger.info("\n" + "="*70)
        logger.info("BENCHMARK RESULTS")
        logger.info("="*70)
        logger.info(f"Iterations:    {num_iterations}")
        logger.info(f"Mean:          {mean_ms:.3f} ms")
        logger.info(f"Median:        {median_ms:.3f} ms")
        logger.info(f"Std Dev:       {std_ms:.3f} ms")
        logger.info(f"Min:           {min_ms:.3f} ms")
        logger.info(f"Max:           {max_ms:.3f} ms")
        logger.info(f"Throughput:    {fps:.1f} FPS")
        logger.info("="*70)

        # Performance assessment
        logger.info("\n" + "="*70)
        logger.info("PERFORMANCE ASSESSMENT")
        logger.info("="*70)

        if mean_ms < 5:
            logger.info("✓ EXCELLENT: Full Edge TPU acceleration achieved!")
            logger.info("  Inference time < 5ms indicates 100% Edge TPU mapping")
        elif mean_ms < 20:
            logger.info("✓ GOOD: Mostly Edge TPU accelerated")
            logger.info("  Some operations may run on CPU")
        elif mean_ms < 100:
            logger.info("⚠️  DEGRADED: Significant CPU fallback detected")
            logger.info("  Check compiler output for unsupported operations")
        else:
            logger.info("❌ POOR: Mostly running on CPU")
            logger.info("  Model likely not compiled for Edge TPU")

        target_fps = 60
        if fps >= target_fps:
            logger.info(f"✓ Target FPS achieved: {fps:.1f} FPS >= {target_fps} FPS")
        else:
            logger.info(f"⚠️  Below target: {fps:.1f} FPS < {target_fps} FPS")

        logger.info("="*70 + "\n")

        # Verify output
        logger.info("Sample output verification:")
        logger.info(f"  Shape: {output.shape}")
        logger.info(f"  Range: [{output.min():.3f}, {output.max():.3f}]")
        logger.info(f"  Mean:  {output.mean():.3f}")

        return timings

    def run_test(self):
        """Run complete test suite."""
        logger.info("\n")
        logger.info("=" * 70)
        logger.info(" CORAL EDGE TPU INFERENCE TEST")
        logger.info("=" * 70)
        logger.info(f" Model: {self.model_path.name}")
        logger.info("=" * 70)
        logger.info("\n")

        # Check model exists
        if not self.model_path.exists():
            logger.error(f"Model not found: {self.model_path}")
            return 1

        # Check Edge TPU
        if self.is_edgetpu_model:
            self.check_edgetpu_availability()
        else:
            logger.info("Testing standard TFLite model (no Edge TPU compilation)")

        # Load model
        try:
            interpreter, input_details, output_details = self.load_model()
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            import traceback
            traceback.print_exc()
            return 1

        # Run benchmark
        try:
            self.benchmark(interpreter, input_details, output_details)
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            import traceback
            traceback.print_exc()
            return 1

        logger.info("\n✓ Test complete!\n")
        return 0


def main():
    """Main entry point."""

    # Find model to test
    models_dir = Path(__file__).parent / 'models'

    # Look for Edge TPU compiled model first
    edgetpu_models = list(models_dir.glob('*_edgetpu.tflite'))
    tflite_models = list(models_dir.glob('*.tflite'))
    tflite_models = [m for m in tflite_models if '_edgetpu' not in m.name]

    if edgetpu_models:
        model_path = sorted(edgetpu_models)[-1]  # Latest
        logger.info(f"Found Edge TPU compiled model: {model_path.name}")
    elif tflite_models:
        model_path = sorted(tflite_models)[-1]  # Latest
        logger.info(f"Found TFLite model: {model_path.name}")
        logger.info("Note: This is not compiled for Edge TPU yet")
    else:
        logger.error("No models found in models/ directory")
        logger.info("Run train_coral_optimized.py first")
        return 1

    # Run test
    tester = CoralInferenceTester(model_path)
    return tester.run_test()


if __name__ == '__main__':
    sys.exit(main())
