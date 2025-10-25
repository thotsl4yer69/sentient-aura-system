#!/usr/bin/env python3
"""
Coral Visualization Daemon - High-Performance AI Self-Representation

Leverages Google Coral TPU for real-time (60 FPS) particle visualization
based on 68-dimensional cognitive + sensory feature extraction.

Performance targets:
- Feature extraction: <2ms
- Coral inference: <5ms
- Total frame time: <16ms (60 FPS)
"""

import sys
import os
import threading
import time
import logging
import json
from typing import Dict, Optional
from collections import deque

import numpy as np

logger = logging.getLogger("CoralVizDaemon")


class CoralVisualizationDaemon(threading.Thread):
    """
    High-performance visualization daemon using Google Coral TPU.

    Responsibilities:
    1. Extract 68 features from WorldState at 60 FPS
    2. Run Coral TPU inference (<5ms per frame)
    3. Interpolate particle positions for smooth motion
    4. Broadcast via WebSocket to GUI
    5. Collect performance metrics
    6. Handle fallback to LLM mode
    """

    def __init__(self, world_state, websocket_server, config):
        """
        Initialize Coral visualization daemon.

        Args:
            world_state: Shared WorldState instance
            websocket_server: WebSocketServer for broadcasting
            config: Configuration dict with:
                - target_fps: int (default 60)
                - model_path: str (path to .tflite model)
                - fallback_mode: str ('llm' or 'static')
                - enable_metrics: bool
                - interpolation_alpha: float (0-1, default 0.3)
        """
        super().__init__(daemon=True, name="CoralVizDaemon")

        self.world_state = world_state
        self.websocket_server = websocket_server
        self.config = config

        # Coral TPU components
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.coral_available = False

        # Performance monitoring
        self.metrics = PerformanceMetrics()
        self.frame_counter = 0
        self.last_metrics_report = time.time()

        # Feature extraction pipeline
        self.feature_extractor = FeatureExtractor(world_state)

        # Particle interpolation (for smooth 60 FPS)
        self.interpolator = ParticleInterpolator(
            alpha=config.get('interpolation_alpha', 0.3)
        )

        # Control flow
        self.running = False
        self.mode = 'coral'  # 'coral' or 'llm' or 'static'

        # Thread synchronization
        self.state_lock = threading.Lock()

        # Preallocated buffers
        self.input_buffer = None
        self.previous_particles = None

    def _initialize_coral(self):
        """
        Initialize Coral TPU interpreter.

        Returns:
            bool: True if successful, False if fallback required
        """
        try:
            # Import Coral libraries
            try:
                from pycoral.utils import edgetpu
                import tflite_runtime.interpreter as tflite
            except ImportError as e:
                logger.error(f"Coral libraries not installed: {e}")
                logger.error("Install: sudo apt-get install python3-pycoral")
                return False

            model_path = self.config['model_path']

            # Validate model file exists
            if not os.path.exists(model_path):
                logger.error(f"Model not found: {model_path}")
                logger.error("Generate model with coral_training/train_model.py")
                return False

            # Check if Coral device is available
            devices = edgetpu.list_edge_tpus()
            if not devices:
                logger.error("No Coral TPU devices found")
                logger.error("Connect Coral USB Accelerator and check lsusb")
                return False

            logger.info(f"Found {len(devices)} Coral TPU device(s)")
            for i, device in enumerate(devices):
                logger.info(f"  Device {i}: {device['type']} at {device.get('path', 'N/A')}")

            # Load Edge TPU model
            logger.info(f"Loading Coral TPU model: {model_path}")
            self.interpreter = tflite.Interpreter(
                model_path=model_path,
                experimental_delegates=[
                    tflite.load_delegate('libedgetpu.so.1')
                ]
            )

            # Allocate tensors
            self.interpreter.allocate_tensors()

            # Get input/output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()

            # Validate model architecture
            input_shape = self.input_details[0]['shape']
            output_shape = self.output_details[0]['shape']

            logger.info(f"Model input shape: {input_shape}")
            logger.info(f"Model output shape: {output_shape}")

            # Check dimensions
            if input_shape[1] != 68:
                logger.error(f"Expected 68 input features, got {input_shape[1]}")
                return False

            if output_shape[1] != 30000:
                logger.error(f"Expected 30000 output values, got {output_shape[1]}")
                return False

            # Preallocate input buffer (INT8)
            self.input_buffer = np.zeros(
                self.input_details[0]['shape'],
                dtype=np.int8
            )

            # Warmup inference (first run is always slower)
            logger.info("Warming up Coral TPU...")
            warmup_start = time.perf_counter()
            for i in range(5):
                self.interpreter.set_tensor(
                    self.input_details[0]['index'],
                    self.input_buffer
                )
                self.interpreter.invoke()
                warmup_time = (time.perf_counter() - warmup_start) * 1000
                logger.debug(f"  Warmup {i+1}/5: {warmup_time:.2f}ms")

            warmup_total = time.perf_counter() - warmup_start
            logger.info(f"✓ Coral TPU warmup complete ({warmup_total*1000:.1f}ms)")

            self.coral_available = True
            self.mode = 'coral'
            return True

        except Exception as e:
            logger.error(f"Coral initialization failed: {e}")
            logger.exception("Full traceback:")
            return False

    def run(self):
        """Main daemon loop - runs at target FPS."""
        target_fps = self.config.get('target_fps', 60)
        logger.info(f"CoralVisualizationDaemon starting (target: {target_fps} FPS)")

        # Initialize Coral TPU
        if not self._initialize_coral():
            logger.warning("Falling back to LLM mode")
            self.mode = 'llm'
            # Don't start daemon if fallback mode is LLM
            # (existing SentientCore handles LLM visualization)
            logger.info("CoralVisualizationDaemon in fallback mode - exiting")
            return

        self.running = True
        target_frame_time = 1.0 / target_fps  # 16.67ms for 60 FPS

        logger.info("=" * 60)
        logger.info("CORAL VISUALIZATION DAEMON ACTIVE")
        logger.info(f"Target FPS: {target_fps}")
        logger.info(f"Frame budget: {target_frame_time*1000:.2f}ms")
        logger.info("=" * 60)

        while self.running:
            frame_start = time.perf_counter()

            try:
                # 1. Extract features from WorldState (~2ms)
                extract_start = time.perf_counter()
                features = self.feature_extractor.extract()
                extract_time = time.perf_counter() - extract_start

                # 2. Run Coral inference (~3-5ms)
                particles = self._coral_inference(features)

                # 3. Interpolate for smooth motion (~1ms)
                interp_start = time.perf_counter()
                smooth_particles = self.interpolator.update(particles)
                interp_time = time.perf_counter() - interp_start

                # 4. Broadcast to WebSocket clients (~2ms)
                broadcast_start = time.perf_counter()
                self._broadcast_particles(smooth_particles, extract_time, interp_time)
                broadcast_time = time.perf_counter() - broadcast_start

                # 5. Update metrics
                frame_time = time.perf_counter() - frame_start
                self.metrics.record_frame(frame_time)
                self.metrics.record_component('extraction', extract_time)
                self.metrics.record_component('interpolation', interp_time)
                self.metrics.record_component('broadcast', broadcast_time)
                self.frame_counter += 1

                # 6. Report metrics every 5 seconds
                if time.time() - self.last_metrics_report > 5.0:
                    self._report_metrics()
                    self.last_metrics_report = time.time()

                # 7. Sleep to maintain target FPS
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    # Frame took too long - log warning
                    if frame_time > target_frame_time * 1.5:
                        logger.warning(
                            f"Frame {self.frame_counter} overran budget: "
                            f"{frame_time*1000:.2f}ms (target: {target_frame_time*1000:.2f}ms) "
                            f"[extract={extract_time*1000:.2f}ms, "
                            f"infer={self.metrics.get_last_inference_ms():.2f}ms, "
                            f"interp={interp_time*1000:.2f}ms, "
                            f"broadcast={broadcast_time*1000:.2f}ms]"
                        )

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Frame {self.frame_counter} error: {e}")
                logger.exception("Full traceback:")
                time.sleep(0.1)  # Back off on error

        logger.info("CoralVisualizationDaemon stopped")

    def _coral_inference(self, features: np.ndarray) -> np.ndarray:
        """
        Run inference on Coral TPU.

        Args:
            features: (68,) float32 array, values in [0, 1]

        Returns:
            particles: (30000,) float32 array representing 10000 particles × (x,y,z)
        """
        # Quantize features to INT8 (model expects INT8 input)
        # Scale: float [0, 1] → int8 [-128, 127]
        input_scale = self.input_details[0]['quantization'][0]
        input_zero_point = self.input_details[0]['quantization'][1]

        features_int8 = np.round(
            features / input_scale + input_zero_point
        ).astype(np.int8)

        # Set input tensor (in-place to preallocated buffer)
        self.input_buffer[0] = features_int8
        self.interpreter.set_tensor(
            self.input_details[0]['index'],
            self.input_buffer
        )

        # Run inference
        inference_start = time.perf_counter()
        self.interpreter.invoke()
        inference_time = time.perf_counter() - inference_start
        self.metrics.record_inference(inference_time)

        # Get output tensor
        output_int8 = self.interpreter.get_tensor(
            self.output_details[0]['index']
        )[0]  # Remove batch dimension

        # Dequantize: int8 → float32
        output_scale = self.output_details[0]['quantization'][0]
        output_zero_point = self.output_details[0]['quantization'][1]

        particles_float = (
            output_int8.astype(np.float32) - output_zero_point
        ) * output_scale

        return particles_float

    def _broadcast_particles(self, particles: np.ndarray, extract_time: float, interp_time: float):
        """
        Broadcast particle positions to WebSocket clients.

        Message format:
        {
            "type": "particles",
            "mode": "coral",
            "timestamp": 1729800000.123,
            "frame": 12345,
            "particles": [[x1,y1,z1], [x2,y2,z2], ...],  # 10000 particles
            "metadata": {
                "fps": 59.8,
                "inference_ms": 4.2,
                "extraction_ms": 1.8,
                "interpolation_ms": 0.9,
                "broadcast_ms": 2.1,
                "total_ms": 12.1
            }
        }
        """
        # Reshape to (10000, 3)
        particles_3d = particles.reshape(10000, 3)

        # Build message
        message = {
            "type": "particles",
            "mode": self.mode,
            "timestamp": time.time(),
            "frame": self.frame_counter,
            "particles": particles_3d.tolist(),
            "metadata": {
                "fps": self.metrics.get_fps(),
                "inference_ms": self.metrics.get_avg_inference_ms(),
                "extraction_ms": extract_time * 1000,
                "interpolation_ms": interp_time * 1000,
                "total_ms": self.metrics.get_avg_frame_ms()
            }
        }

        # Serialize to JSON
        message_json = json.dumps(message)

        # Broadcast via WebSocket
        if self.websocket_server:
            self.websocket_server.broadcast(message_json)

    def _report_metrics(self):
        """Log performance metrics."""
        metrics_dict = self.metrics.get_metrics_dict()
        logger.info(
            f"Coral Metrics: "
            f"FPS={metrics_dict['fps']:.1f}, "
            f"Frame={metrics_dict['avg_frame_ms']:.2f}ms, "
            f"Inference={metrics_dict['avg_inference_ms']:.2f}ms, "
            f"Frames={self.frame_counter}"
        )

    def stop(self):
        """Gracefully stop the daemon."""
        logger.info("Stopping CoralVisualizationDaemon...")
        self.running = False

    def health_check(self) -> dict:
        """
        Comprehensive health check.

        Returns:
            dict: Health status with details
        """
        health = {
            'status': 'healthy',
            'checks': {},
            'metrics': {}
        }

        # 1. Coral TPU availability
        try:
            from pycoral.utils import edgetpu
            devices = edgetpu.list_edge_tpus()
            health['checks']['coral_device'] = {
                'status': 'pass' if devices else 'fail',
                'devices': len(devices) if devices else 0
            }
        except Exception as e:
            health['checks']['coral_device'] = {
                'status': 'fail',
                'error': str(e)
            }

        # 2. Model file exists
        if os.path.exists(self.config['model_path']):
            health['checks']['model_file'] = {'status': 'pass'}
        else:
            health['checks']['model_file'] = {
                'status': 'fail',
                'error': f'Model not found: {self.config["model_path"]}'
            }

        # 3. Inference performance
        if hasattr(self, 'metrics'):
            fps = self.metrics.get_fps()
            target_fps = self.config.get('target_fps', 60)
            health['checks']['performance'] = {
                'status': 'pass' if fps >= target_fps * 0.8 else 'warn',
                'fps': fps,
                'target_fps': target_fps
            }
            health['metrics'] = self.metrics.get_metrics_dict()

        # 4. WebSocket connectivity
        if self.websocket_server and hasattr(self.websocket_server, 'clients'):
            client_count = len(self.websocket_server.clients)
            health['checks']['websocket'] = {
                'status': 'pass',
                'clients': client_count
            }
        else:
            health['checks']['websocket'] = {
                'status': 'warn',
                'clients': 0
            }

        # Overall status
        failed = [k for k, v in health['checks'].items() if v['status'] == 'fail']
        if failed:
            health['status'] = 'unhealthy'
            health['failed_checks'] = failed

        return health


class FeatureExtractor:
    """
    Extracts 68 features from WorldState in optimized manner.

    Performance target: <2ms extraction time
    """

    def __init__(self, world_state):
        self.world_state = world_state

        # Preallocate feature buffer
        self.features = np.zeros(68, dtype=np.float32)

        # Cache for computed values
        self.cache = {}
        self.cache_timeout = 0.1  # 100ms cache lifetime

    def extract(self) -> np.ndarray:
        """
        Extract all 68 features from current WorldState.

        Returns:
            features: (68,) float32 array, all values in [0, 1]
        """
        # Get snapshot of WorldState (thread-safe)
        # If world_state has get_snapshot, use it. Otherwise use direct access.
        if hasattr(self.world_state, 'get_snapshot'):
            state = self.world_state.get_snapshot()
        else:
            # Fallback: direct access with get()
            state = {}

        # COGNITIVE STATE (8 features) - indices 0-7
        self.features[0] = self._extract_cognitive_state(state)
        self.features[1] = self._extract_reasoning_depth(state)
        self.features[2] = self._extract_uncertainty_level(state)
        self.features[3] = self._extract_cognitive_load(state)
        self.features[4] = self._extract_creativity_mode(state)
        self.features[5] = self._extract_attention_focus(state)
        self.features[6] = self._extract_learning_active(state)
        self.features[7] = self._extract_memory_access_depth(state)

        # ENVIRONMENTAL SENSORS (10 features) - indices 8-17
        env = state.get('environment', {}) if isinstance(state, dict) else {}
        self.features[8] = self._normalize_temperature(env.get('temperature', 22.0))
        self.features[9] = self._normalize_humidity(env.get('humidity', 45.0))
        self.features[10] = self._normalize_pressure(env.get('pressure', 1013.0))
        self.features[11] = env.get('light_level', 0.5)
        self.features[12] = env.get('ambient_sound', 0.0)
        vision = state.get('vision', {}) if isinstance(state, dict) else {}
        self.features[13] = float(vision.get('motion_detected', False))
        self.features[14] = vision.get('motion_intensity', 0.0)
        self.features[15] = self._extract_proximity_human(state)
        self.features[16] = env.get('air_quality', 0.8)
        self.features[17] = self._normalize_time_of_day()

        # RF SPECTRUM ANALYSIS (12 features) - indices 18-29
        rf_data = state.get('rf_scanner', {}) if isinstance(state, dict) else {}
        self.features[18] = float(rf_data.get('active', False))
        self.features[19] = rf_data.get('433mhz', 0.0)
        self.features[20] = rf_data.get('915mhz', 0.0)
        self.features[21] = rf_data.get('2_4ghz', 0.0)
        self.features[22] = rf_data.get('5ghz', 0.0)
        self.features[23] = rf_data.get('spectrum_density', 0.0)
        self.features[24] = self._normalize_count(rf_data.get('known_devices', 0), max_val=10)
        self.features[25] = self._normalize_count(rf_data.get('unknown_signals', 0), max_val=10)
        self.features[26] = rf_data.get('signal_diversity', 0.0)
        self.features[27] = rf_data.get('jamming_detected', 0.0)
        self.features[28] = rf_data.get('wifi_activity', 0.0)
        self.features[29] = rf_data.get('bluetooth_activity', 0.0)

        # VISUAL PROCESSING (10 features) - indices 30-39
        self.features[30] = float(vision.get('rgb_frame') is not None)
        self.features[31] = self._compute_scene_complexity(vision)
        self.features[32] = self._normalize_count(len(vision.get('detected_objects', [])), max_val=10)
        self.features[33] = self._normalize_count(len(vision.get('faces_detected', [])), max_val=5)
        self.features[34] = self._extract_dominant_color_hue(vision)
        self.features[35] = vision.get('brightness', 0.5)
        self.features[36] = float(vision.get('motion_detected', False)) * 0.5
        self.features[37] = self._compute_edge_density(vision)
        self.features[38] = self._compute_avg_object_confidence(vision)
        self.features[39] = vision.get('visual_novelty', 0.0)

        # AUDIO PROCESSING (6 features) - indices 40-45
        audio = state.get('audio', {}) if isinstance(state, dict) else {}
        self.features[40] = float(audio.get('active', False))
        self.features[41] = float(audio.get('speech_detected', False))
        self.features[42] = audio.get('speech_clarity', 0.0)
        self.features[43] = audio.get('freq_low', 0.0)
        self.features[44] = audio.get('freq_mid', 0.0)
        self.features[45] = audio.get('freq_high', 0.0)

        # INTERACTION MODE (7 features) - indices 46-52
        self.features[46] = self._extract_human_interaction(state)
        self.features[47] = self._extract_personality_mode(state)
        self.features[48] = self._extract_communication_intent(state)
        interaction = state.get('interaction', {}) if isinstance(state, dict) else {}
        self.features[49] = interaction.get('empathy_level', 0.5)
        self.features[50] = interaction.get('formality_level', 0.3)
        self.features[51] = interaction.get('proactivity', 0.0)
        self.features[52] = interaction.get('user_engagement', 0.0)

        # NETWORK & DATA STREAMS (6 features) - indices 53-58
        network = state.get('network', {}) if isinstance(state, dict) else {}
        self.features[53] = float(network.get('connected', True))
        self.features[54] = network.get('activity', 0.0)
        self.features[55] = float(state.get('api_manager', {}).get('active', False) if isinstance(state, dict) else False)
        self.features[56] = state.get('database', {}).get('activity', 0.0) if isinstance(state, dict) else 0.0
        self.features[57] = self._normalize_count(
            len(state.get('websocket_clients', []) if isinstance(state, dict) else []),
            max_val=10
        )
        self.features[58] = float(state.get('data_streaming', False) if isinstance(state, dict) else False)

        # SYSTEM RESOURCES (4 features) - indices 59-62
        system = state.get('system', {}) if isinstance(state, dict) else {}
        self.features[59] = self._get_cpu_usage()
        self.features[60] = self._get_memory_usage()
        self.features[61] = system.get('gpu_usage', 0.0)
        self.features[62] = system.get('thermal_state', 0.0)

        # SECURITY & THREAT AWARENESS (5 features) - indices 63-67
        security = state.get('security', {}) if isinstance(state, dict) else {}
        self.features[63] = security.get('threat_level', 0.0)
        self.features[64] = float(security.get('anomaly_detected', False))
        self.features[65] = security.get('defensive_mode', 0.0)
        self.features[66] = security.get('sensor_tampering', 0.0)
        self.features[67] = security.get('intrusion_attempts', 0.0)

        # Validate all features in [0, 1]
        if not np.all((self.features >= 0.0) & (self.features <= 1.0)):
            # Log warning but clamp values
            invalid_indices = np.where((self.features < 0.0) | (self.features > 1.0))[0]
            logger.warning(f"Features outside [0,1] at indices {invalid_indices}: {self.features[invalid_indices]}")
            self.features = np.clip(self.features, 0.0, 1.0)

        return self.features

    # Helper methods for complex feature extraction
    def _extract_cognitive_state(self, state):
        """Map cognitive state string to 0-1 value."""
        state_map = {
            'idle': 0.0,
            'listening': 0.2,
            'processing': 0.4,
            'speaking': 0.6,
            'executing': 0.8,
            'reasoning': 1.0
        }
        if not isinstance(state, dict):
            return 0.0
        cognitive = state.get('cognitive', {})
        return state_map.get(cognitive.get('state', 'idle'), 0.0)

    def _extract_reasoning_depth(self, state):
        if not isinstance(state, dict):
            return 0.0
        return state.get('cognitive', {}).get('reasoning_depth', 0.0)

    def _extract_uncertainty_level(self, state):
        if not isinstance(state, dict):
            return 0.0
        return state.get('cognitive', {}).get('uncertainty_level', 0.0)

    def _extract_cognitive_load(self, state):
        if not isinstance(state, dict):
            return 0.0
        return state.get('cognitive', {}).get('load', 0.0)

    def _extract_creativity_mode(self, state):
        if not isinstance(state, dict):
            return 0.0
        return state.get('cognitive', {}).get('creativity', 0.0)

    def _extract_attention_focus(self, state):
        if not isinstance(state, dict):
            return 0.0
        return state.get('cognitive', {}).get('attention_focus', 0.0)

    def _extract_learning_active(self, state):
        if not isinstance(state, dict):
            return 0.0
        return float(state.get('cognitive', {}).get('learning_active', False))

    def _extract_memory_access_depth(self, state):
        if not isinstance(state, dict):
            return 0.0
        return state.get('cognitive', {}).get('memory_depth', 0.0)

    def _normalize_temperature(self, temp_c):
        """Normalize temperature 0-40°C → 0-1."""
        return np.clip(temp_c / 40.0, 0.0, 1.0)

    def _normalize_humidity(self, humidity_pct):
        """Normalize humidity 0-100% → 0-1."""
        return np.clip(humidity_pct / 100.0, 0.0, 1.0)

    def _normalize_pressure(self, pressure_hpa):
        """Normalize pressure 900-1100 hPa → 0-1."""
        return np.clip((pressure_hpa - 900.0) / 200.0, 0.0, 1.0)

    def _normalize_time_of_day(self):
        """Normalize current hour 0-24 → 0-1 for circadian rhythm."""
        from datetime import datetime
        hour = datetime.now().hour
        return hour / 24.0

    def _normalize_count(self, count, max_val):
        """Normalize count to [0, 1] with saturation."""
        return np.clip(count / max_val, 0.0, 1.0)

    def _extract_proximity_human(self, state):
        """Extract human proximity from vision/motion data."""
        if not isinstance(state, dict):
            return 0.0
        vision = state.get('vision', {})
        faces = len(vision.get('faces_detected', []))
        if faces > 0:
            return 0.7  # Face detected = close proximity
        elif vision.get('motion_detected', False):
            return 0.3  # Motion but no face = moderate proximity
        return 0.0

    def _compute_scene_complexity(self, vision):
        """Estimate scene complexity from object count and edge density."""
        obj_count = len(vision.get('detected_objects', []))
        edge_density = vision.get('edge_density', 0.5)
        # Simple heuristic
        complexity = (obj_count / 10.0) * 0.6 + edge_density * 0.4
        return np.clip(complexity, 0.0, 1.0)

    def _extract_dominant_color_hue(self, vision):
        """Extract dominant color hue from vision data."""
        # Placeholder - would need actual color analysis
        return vision.get('dominant_hue', 0.5)

    def _compute_edge_density(self, vision):
        """Compute edge density from vision data."""
        return vision.get('edge_density', 0.5)

    def _compute_avg_object_confidence(self, vision):
        """Average confidence of detected objects."""
        objects = vision.get('detected_objects', [])
        if not objects:
            return 0.0
        confidences = [obj.get('confidence', 0.5) for obj in objects]
        return np.mean(confidences)

    def _extract_human_interaction(self, state):
        """Extract human interaction level."""
        if not isinstance(state, dict):
            return 0.0
        return state.get('interaction', {}).get('level', 0.0)

    def _extract_personality_mode(self, state):
        """Map personality mode to 0-1 value."""
        mode_map = {
            'analytical': 0.2,
            'friendly': 0.4,
            'defensive': 0.6,
            'creative': 0.8,
            'educational': 1.0
        }
        if not isinstance(state, dict):
            return 0.4
        mode = state.get('interaction', {}).get('personality', 'friendly')
        return mode_map.get(mode, 0.4)

    def _extract_communication_intent(self, state):
        """Map communication intent to 0-1 value."""
        intent_map = {
            'inform': 0.2,
            'query': 0.4,
            'warn': 0.6,
            'express': 0.8,
            'entertain': 1.0
        }
        if not isinstance(state, dict):
            return 0.2
        intent = state.get('interaction', {}).get('intent', 'inform')
        return intent_map.get(intent, 0.2)

    def _get_cpu_usage(self):
        """Get current CPU usage (cached for performance)."""
        if 'cpu_usage' in self.cache:
            if time.time() - self.cache['cpu_usage_time'] < self.cache_timeout:
                return self.cache['cpu_usage']

        try:
            import psutil
            usage = psutil.cpu_percent(interval=0) / 100.0
            self.cache['cpu_usage'] = usage
            self.cache['cpu_usage_time'] = time.time()
            return usage
        except:
            return 0.2  # Default fallback

    def _get_memory_usage(self):
        """Get current memory usage (cached for performance)."""
        if 'mem_usage' in self.cache:
            if time.time() - self.cache['mem_usage_time'] < self.cache_timeout:
                return self.cache['mem_usage']

        try:
            import psutil
            usage = psutil.virtual_memory().percent / 100.0
            self.cache['mem_usage'] = usage
            self.cache['mem_usage_time'] = time.time()
            return usage
        except:
            return 0.3  # Default fallback


class ParticleInterpolator:
    """
    Exponential moving average interpolator for smooth particle motion.

    Prevents jitter and sudden jumps in particle positions.
    """

    def __init__(self, alpha=0.3):
        """
        Args:
            alpha: Smoothing factor (0 = no update, 1 = no smoothing)
                  0.3 is good balance between responsiveness and smoothness
        """
        self.alpha = alpha
        self.previous = None

    def update(self, current: np.ndarray) -> np.ndarray:
        """
        Apply EMA smoothing to particle positions.

        Args:
            current: (30000,) array of current particle positions

        Returns:
            smoothed: (30000,) array of smoothed positions
        """
        if self.previous is None:
            # First frame - no interpolation
            self.previous = current.copy()
            return current

        # EMA: smoothed = alpha * current + (1 - alpha) * previous
        smoothed = self.alpha * current + (1.0 - self.alpha) * self.previous

        # Update state
        self.previous = smoothed.copy()

        return smoothed


class PerformanceMetrics:
    """Track and report performance metrics."""

    def __init__(self, window_size=300):
        """
        Args:
            window_size: Number of frames to average over (300 = 5 sec at 60 FPS)
        """
        self.frame_times = deque(maxlen=window_size)
        self.inference_times = deque(maxlen=window_size)
        self.component_times = {
            'extraction': deque(maxlen=window_size),
            'interpolation': deque(maxlen=window_size),
            'broadcast': deque(maxlen=window_size)
        }
        self.frame_count = 0
        self.last_inference_time = 0.0

    def record_frame(self, frame_time: float):
        """Record total frame processing time."""
        self.frame_times.append(frame_time)
        self.frame_count += 1

    def record_inference(self, inference_time: float):
        """Record Coral inference time."""
        self.inference_times.append(inference_time)
        self.last_inference_time = inference_time

    def record_component(self, component: str, time_sec: float):
        """Record component-specific time."""
        if component in self.component_times:
            self.component_times[component].append(time_sec)

    def get_fps(self) -> float:
        """Calculate average FPS over window."""
        if not self.frame_times:
            return 0.0
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0

    def get_avg_frame_ms(self) -> float:
        """Average total frame time in milliseconds."""
        if not self.frame_times:
            return 0.0
        return (sum(self.frame_times) / len(self.frame_times)) * 1000.0

    def get_avg_inference_ms(self) -> float:
        """Average inference time in milliseconds."""
        if not self.inference_times:
            return 0.0
        return (sum(self.inference_times) / len(self.inference_times)) * 1000.0

    def get_last_inference_ms(self) -> float:
        """Last inference time in milliseconds."""
        return self.last_inference_time * 1000.0

    def get_metrics_dict(self) -> dict:
        """Get all metrics as dictionary."""
        return {
            'fps': self.get_fps(),
            'avg_frame_ms': self.get_avg_frame_ms(),
            'avg_inference_ms': self.get_avg_inference_ms(),
            'total_frames': self.frame_count
        }


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Mock objects for testing
    class MockWorldState:
        def get_snapshot(self):
            return {
                'cognitive': {'state': 'idle'},
                'environment': {'temperature': 22.0, 'humidity': 45.0},
                'vision': {'motion_detected': False},
                'network': {'connected': True},
                'system': {}
            }

    class MockWebSocketServer:
        def __init__(self):
            self.clients = []
        def broadcast(self, message):
            logger.info(f"Broadcast: {len(message)} bytes")

    # Test configuration
    config = {
        'target_fps': 60,
        'model_path': '/home/mz1312/Sentient-Core-v4/models/sentient_viz_edgetpu.tflite',
        'fallback_mode': 'llm',
        'enable_metrics': True,
        'interpolation_alpha': 0.3
    }

    # Create daemon
    daemon = CoralVisualizationDaemon(
        world_state=MockWorldState(),
        websocket_server=MockWebSocketServer(),
        config=config
    )

    # Test feature extraction
    logger.info("Testing feature extraction...")
    features = daemon.feature_extractor.extract()
    logger.info(f"Extracted {len(features)} features")
    logger.info(f"Feature range: [{features.min():.3f}, {features.max():.3f}]")

    # Test health check
    logger.info("\nRunning health check...")
    health = daemon.health_check()
    logger.info(f"Health status: {health}")
