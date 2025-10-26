#!/usr/bin/env python3
"""
Coral Pixel Engine - Real-time TPU inference for particle control.

This module runs TensorFlow Lite models on the Google Coral Edge TPU to
generate intelligent particle behavior parameters from sensor data.
"""

import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CoralPixelEngine:
    """
    Real-time inference engine using Google Coral Edge TPU.

    Converts sensor data → particle behavior parameters at <5ms latency.
    """

    def __init__(self, model_path: str = "models/sentient_pixel_controller_edgetpu.tflite"):
        """
        Initialize Coral TPU inference engine.

        Args:
            model_path: Path to Edge TPU compiled .tflite model
        """
        self.model_path = Path(model_path)
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.inference_count = 0
        self.total_inference_time = 0.0

        # Sensor feature normalization factors (must match training!)
        self.normalization = {
            'temperature': 50.0,
            'humidity': 100.0,
            'pressure': 1100.0,
            'gas_resistance': 200000.0,
            'oxidising': 1000.0,
            'reducing': 1000.0,
            'nh3': 200.0,
            'light_level': 1000.0,
            'ambient_noise': 100.0,
            'sound_direction': 360.0,
            'detected_objects': 10.0,
            'faces_detected': 5.0,
            'latitude': 180.0,
            'longitude': 360.0,
            'altitude': 1000.0,
            'battery_charge': 100.0,
            'battery_voltage': 5.0,
            'uptime': 86400.0,
            'active_daemons': 10.0,
            'cpu_temp': 100.0
        }

        self._load_model()

    def _load_model(self):
        """Load and initialize Edge TPU model."""
        try:
            # Import PyCoral library
            from pycoral.utils import edgetpu
            from pycoral.adapters import common

            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"Model not found: {self.model_path}\n"
                    f"Please train model in Colab and compile with edgetpu_compiler"
                )

            logger.info(f"Loading Edge TPU model: {self.model_path}")
            self.interpreter = edgetpu.make_interpreter(str(self.model_path))
            self.interpreter.allocate_tensors()

            self.input_details = self.interpreter.get_input_details()[0]
            self.output_details = self.interpreter.get_output_details()[0]

            logger.info("Coral TPU model loaded successfully")
            logger.info(f"  Input shape: {self.input_details['shape']}")
            logger.info(f"  Input dtype: {self.input_details['dtype']}")
            logger.info(f"  Output shape: {self.output_details['shape']}")
            logger.info(f"  Output dtype: {self.output_details['dtype']}")

        except ImportError:
            logger.error("PyCoral library not installed!")
            logger.error("Install with: pip install pycoral")
            raise
        except Exception as e:
            logger.error(f"Failed to load Coral model: {e}")
            raise

    def _extract_features(self, world_state: Dict[str, Any]) -> np.ndarray:
        """
        Extract and normalize 22 sensor features from WorldState.

        Args:
            world_state: WorldState snapshot dictionary

        Returns:
            np.ndarray: (22,) normalized feature vector [0-1]
        """
        features = np.zeros(22, dtype=np.float32)

        env = world_state.get('environment', {})
        audio = world_state.get('audio', {})
        vision = world_state.get('vision', {})
        location = world_state.get('location', {})
        power = world_state.get('power', {})
        system = world_state.get('system', {})

        # Environment (8 features) - indices 0-7
        features[0] = (env.get('temperature') or 20.0) / self.normalization['temperature']
        features[1] = (env.get('humidity') or 50.0) / self.normalization['humidity']
        features[2] = (env.get('pressure') or 1013.0) / self.normalization['pressure']
        features[3] = (env.get('gas_resistance') or 50000.0) / self.normalization['gas_resistance']
        features[4] = (env.get('oxidising') or 0.0) / self.normalization['oxidising']
        features[5] = (env.get('reducing') or 0.0) / self.normalization['reducing']
        features[6] = (env.get('nh3') or 0.0) / self.normalization['nh3']
        features[7] = (env.get('light_level') or 500.0) / self.normalization['light_level']

        # Audio (2 features) - indices 8-9
        features[8] = (audio.get('ambient_noise_level') or 40.0) / self.normalization['ambient_noise']
        features[9] = (audio.get('sound_direction') or 0.0) / self.normalization['sound_direction']

        # Vision (3 features) - indices 10-12
        features[10] = 1.0 if vision.get('motion_detected', False) else 0.0
        features[11] = len(vision.get('detected_objects', [])) / self.normalization['detected_objects']
        features[12] = len(vision.get('faces_detected', [])) / self.normalization['faces_detected']

        # Location (3 features) - indices 13-15
        lat = location.get('latitude')
        lon = location.get('longitude')
        alt = location.get('altitude')
        features[13] = (lat / self.normalization['latitude'] + 0.5) if lat is not None else 0.5
        features[14] = (lon / self.normalization['longitude'] + 0.5) if lon is not None else 0.5
        features[15] = (alt or 0.0) / self.normalization['altitude']

        # Power (3 features) - indices 16-18
        features[16] = (power.get('battery_charge') or 100.0) / self.normalization['battery_charge']
        features[17] = (power.get('battery_voltage') or 3.7) / self.normalization['battery_voltage']
        features[18] = 1.0 if power.get('is_charging', False) else 0.0

        # System (3 features) - indices 19-21
        features[19] = (system.get('uptime') or 0.0) / self.normalization['uptime']
        features[20] = len(system.get('active_daemons', [])) / self.normalization['active_daemons']

        # CPU temp (estimated from system if available)
        cpu_temp = 50.0  # Default fallback
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                cpu_temp = float(f.read().strip()) / 1000.0
        except:
            pass
        features[21] = cpu_temp / self.normalization['cpu_temp']

        # Clip to valid range [0, 1]
        features = np.clip(features, 0.0, 1.0)

        return features

    def predict_particle_params(self, world_state: Dict[str, Any]) -> Dict[str, float]:
        """
        Run Coral TPU inference to generate particle behavior parameters.

        Args:
            world_state: WorldState snapshot

        Returns:
            dict: 12 particle behavior parameters in [0, 1] range
                 (vertical_bias in [-1, 1])
        """
        import time
        from pycoral.adapters import common

        start_time = time.perf_counter()

        try:
            # Extract normalized features
            features = self._extract_features(world_state)

            # Quantize input to int8
            input_scale, input_zero_point = self.input_details['quantization']
            features_int8 = np.round(features / input_scale + input_zero_point).astype(np.int8)
            features_int8 = features_int8.reshape(1, -1)  # (1, 22)

            # Run inference on Coral TPU
            common.set_input(self.interpreter, features_int8)
            self.interpreter.invoke()

            # Dequantize output
            output_int8 = common.output_tensor(self.interpreter, 0)
            output_scale, output_zero_point = self.output_details['quantization']
            params = (output_int8.astype(np.float32) - output_zero_point) * output_scale
            params = params.flatten()

            # Convert to named dictionary
            result = {
                'swarm_cohesion': float(params[0]),
                'flow_speed': float(params[1]),
                'turbulence': float(params[2]),
                'color_hue_shift': float(params[3]),
                'brightness': float(params[4]),
                'pulse_frequency': float(params[5]),
                'symmetry': float(params[6]),
                'vertical_bias': float(params[7]) * 2.0 - 1.0,  # Scale to [-1, 1]
                'horizontal_spread': float(params[8]),
                'depth_layering': float(params[9]),
                'particle_size': float(params[10]),
                'glow_intensity': float(params[11])
            }

            # Track performance
            elapsed = time.perf_counter() - start_time
            self.inference_count += 1
            self.total_inference_time += elapsed

            if self.inference_count % 100 == 0:
                avg_time = self.total_inference_time / self.inference_count * 1000
                logger.debug(f"Coral inference: {elapsed*1000:.2f}ms (avg: {avg_time:.2f}ms)")

            return result

        except Exception as e:
            logger.error(f"Coral inference failed: {e}")
            # Return neutral fallback parameters
            return self._get_fallback_params()

    def _get_fallback_params(self) -> Dict[str, float]:
        """
        Return neutral fallback parameters when inference fails.

        Returns:
            dict: Safe default parameters
        """
        return {
            'swarm_cohesion': 0.5,
            'flow_speed': 0.3,
            'turbulence': 0.2,
            'color_hue_shift': 0.5,
            'brightness': 0.7,
            'pulse_frequency': 0.4,
            'symmetry': 0.5,
            'vertical_bias': 0.0,
            'horizontal_spread': 0.6,
            'depth_layering': 0.5,
            'particle_size': 0.8,
            'glow_intensity': 0.6
        }

    def get_performance_stats(self) -> Dict[str, float]:
        """
        Get inference performance statistics.

        Returns:
            dict: Performance metrics
        """
        if self.inference_count == 0:
            return {'count': 0, 'avg_latency_ms': 0.0}

        avg_latency = (self.total_inference_time / self.inference_count) * 1000
        return {
            'count': self.inference_count,
            'avg_latency_ms': avg_latency,
            'total_time_s': self.total_inference_time
        }


if __name__ == "__main__":
    """Test Coral Pixel Engine with dummy data."""
    logging.basicConfig(level=logging.INFO)

    # Test with dummy WorldState
    dummy_world_state = {
        'environment': {
            'temperature': 22.5,
            'humidity': 45.0,
            'pressure': 1013.25,
            'light_level': 600.0
        },
        'audio': {
            'ambient_noise_level': 45.0,
            'sound_direction': 90.0
        },
        'vision': {
            'motion_detected': True,
            'detected_objects': ['person', 'chair'],
            'faces_detected': [{'confidence': 0.95}]
        },
        'power': {
            'battery_charge': 85.0,
            'battery_voltage': 3.9,
            'is_charging': False
        },
        'system': {
            'uptime': 3600,
            'active_daemons': ['wifi_scanner', 'hardware_monitor', 'bluetooth']
        }
    }

    try:
        engine = CoralPixelEngine()
        params = engine.predict_particle_params(dummy_world_state)

        print("\nCoral Pixel Engine Test Results:")
        print("=" * 60)
        for key, value in params.items():
            print(f"  {key:20s}: {value:6.3f}")

        print("\nPerformance Stats:")
        stats = engine.get_performance_stats()
        for key, value in stats.items():
            print(f"  {key:20s}: {value}")

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print("\nNOTE: If model not found, please:")
        print("1. Run coral_training_notebook.ipynb in Google Colab")
        print("2. Download sentient_pixel_controller.tflite")
        print("3. Compile with: edgetpu_compiler sentient_pixel_controller.tflite")
        print("4. Move to: ~/Sentient-Core-v4/models/sentient_pixel_controller_edgetpu.tflite")
