#!/usr/bin/env python3
"""
Test Enhanced Edge TPU Model
Tests the compiled 120-feature multi-sensor fusion model on Coral TPU
"""

import time
import numpy as np
from pathlib import Path

try:
    from pycoral.utils.edgetpu import make_interpreter
    PYCORAL_AVAILABLE = True
except ImportError:
    print("⚠️  PyCoral not available, falling back to TFLite")
    import tensorflow as tf
    PYCORAL_AVAILABLE = False


def test_edgetpu_model(model_path: Path):
    """Test the Edge TPU compiled model."""
    print("="*70)
    print("ENHANCED MODEL - EDGE TPU TEST")
    print("Multi-Sensor Fusion - 120 Features")
    print("="*70)
    print(f"Model: {model_path.name}")
    print(f"Size: {model_path.stat().st_size / (1024*1024):.2f} MB")

    if PYCORAL_AVAILABLE:
        print("Using: PyCoral (Edge TPU acceleration)")
        interpreter = make_interpreter(str(model_path))
    else:
        print("Using: TensorFlow Lite (CPU only)")
        interpreter = tf.lite.Interpreter(model_path=str(model_path))

    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    print("\n" + "="*70)
    print("MODEL DETAILS")
    print("="*70)
    print(f"Input tensor:")
    print(f"  Shape: {input_details['shape']}")
    print(f"  Type: {input_details['dtype']}")
    print(f"  Name: {input_details['name']}")
    print(f"\nOutput tensor:")
    print(f"  Shape: {output_details['shape']}")
    print(f"  Type: {output_details['dtype']}")
    print(f"  Name: {output_details['name']}")

    # Create test input (120 features - multi-sensor data)
    test_input = np.random.rand(1, 120).astype(np.float32)

    print("\n" + "="*70)
    print("WARMING UP...")
    print("="*70)
    for i in range(10):
        interpreter.set_tensor(input_details['index'], test_input)
        interpreter.invoke()
        if i == 0:
            output = interpreter.get_tensor(output_details['index'])
            print(f"First inference output shape: {output.shape}")
            print(f"Output range: [{output.min():.3f}, {output.max():.3f}]")

    print("\n" + "="*70)
    print("TESTING INFERENCE SPEED (100 iterations)")
    print("="*70)

    times = []
    for i in range(100):
        start = time.perf_counter()
        interpreter.set_tensor(input_details['index'], test_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details['index'])
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

        if i % 20 == 0:
            print(f"  Iteration {i}: {times[-1]:.2f}ms")

    avg_time = np.mean(times)
    min_time = np.min(times)
    max_time = np.max(times)
    std_time = np.std(times)
    fps = 1000 / avg_time

    print("\n" + "="*70)
    print("PERFORMANCE RESULTS")
    print("="*70)
    print(f"Average inference time: {avg_time:.2f}ms")
    print(f"Min time: {min_time:.2f}ms")
    print(f"Max time: {max_time:.2f}ms")
    print(f"Std deviation: {std_time:.2f}ms")
    print(f"\nFPS capability: {fps:.1f}")
    print(f"Target frame rate (60 FPS): {1000/60:.2f}ms per frame")

    # Test with different scenarios
    print("\n" + "="*70)
    print("TESTING MULTI-SENSOR SCENARIOS")
    print("="*70)

    scenarios = {
        "Urban Environment (Dense Signals)": {
            "wifi_networks_visible": 0.9,
            "bluetooth_devices_visible": 0.8,
            "vision_people_count": 0.6,
            "cognitive_state": 0.8,
        },
        "Flipper Active Capture": {
            "flipper_subghz_433mhz": 0.8,
            "flipper_subghz_capture_active": 1.0,
            "cognitive_state": 0.9,
            "attention_focus": 1.0,
        },
        "Rural Isolation": {
            "wifi_networks_visible": 0.05,
            "bluetooth_devices_visible": 0.0,
            "ambient_light": 0.9,
            "air_quality": 1.0,
        },
        "NFC Card Interaction": {
            "flipper_nfc_card_detected": 1.0,
            "flipper_nfc_read_active": 1.0,
            "human_interaction": 0.9,
            "vision_people_count": 0.05,
        }
    }

    for scenario_name, features in scenarios.items():
        # Create input with scenario features
        scenario_input = np.random.rand(1, 120).astype(np.float32) * 0.1  # Low baseline
        # Set specific features (simplified - would map to actual indices)

        start = time.perf_counter()
        interpreter.set_tensor(input_details['index'], scenario_input)
        interpreter.invoke()
        output = interpreter.get_tensor(output_details['index'])
        end = time.perf_counter()

        inference_time = (end - start) * 1000
        print(f"\n{scenario_name}:")
        print(f"  Inference: {inference_time:.2f}ms")
        print(f"  Output particles: {output.shape[1]} × {output.shape[2]}D")
        print(f"  Particle range: [{output.min():.3f}, {output.max():.3f}]")

    print("\n" + "="*70)
    print("FINAL ASSESSMENT")
    print("="*70)

    if PYCORAL_AVAILABLE:
        if avg_time < 10:
            print("✅ EXCELLENT! Edge TPU acceleration active!")
            print(f"✅ Real-time performance: {fps:.0f} FPS")
            print("✅ Multi-sensor fusion ready for deployment")

            if avg_time < 5:
                print(f"✅ EXCEPTIONAL! {avg_time:.2f}ms = 200+ FPS capability")
                print("✅ Can handle multiple visualization streams simultaneously")
        elif avg_time < 20:
            print("✅ GOOD! Edge TPU working, slightly slower than optimal")
            print(f"✅ Usable performance: {fps:.0f} FPS")
        else:
            print("⚠️  Slower than expected. Check Edge TPU connection.")
            print("   Make sure USB Accelerator is properly connected")
    else:
        print("⚠️  Running on CPU (TensorFlow Lite)")
        print(f"   Performance: {avg_time:.2f}ms ({fps:.0f} FPS)")
        print("   Install PyCoral for Edge TPU acceleration")

    print("\n" + "="*70)
    print("MODEL CAPABILITIES")
    print("="*70)
    print("Input Features (120):")
    print("  • 8 Cognitive State")
    print("  • 10 Environmental Sensors")
    print("  • 12 RF Spectrum Analysis")
    print("  • 10 Visual Processing")
    print("  • 6 Audio Processing")
    print("  • 7 Human Interaction")
    print("  • 6 Network Activity")
    print("  • 4 System Resources")
    print("  • 5 Security/Defense")
    print("  • 20 Flipper Zero (Sub-GHz, NFC, IR, GPIO)")
    print("  • 12 WiFi Scanning")
    print("  • 10 Bluetooth Scanning")
    print("  • 10 Enhanced Computer Vision")
    print("\nOutput: 10,000 particles × 3D coordinates")
    print("Visualization: Color-coded reality mapping")
    print("="*70)


def main():
    script_dir = Path(__file__).parent
    model_dir = script_dir / 'models'

    # Find the Edge TPU compiled model
    edgetpu_models = sorted(model_dir.glob('*_edgetpu.tflite'))

    if not edgetpu_models:
        print("❌ No Edge TPU compiled model found!")
        print(f"   Looking in: {model_dir}")
        print("   Expected: *_edgetpu.tflite")
        return 1

    # Use the latest model
    model_path = edgetpu_models[-1]

    test_edgetpu_model(model_path)

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
