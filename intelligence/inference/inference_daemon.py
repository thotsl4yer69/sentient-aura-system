#!/usr/bin/env python3
"""
Intelligence Inference Daemon

Consumes 120-feature vectors from the Coral TPU pipeline and runs multiple
TFLite models to extract high-level semantic understanding:
- Presence detection (is someone in the room?)
- Activity classification (what are they doing?)

This is the first layer of actual AI intelligence in the Sentient Core system.
"""

import logging
import time
import numpy as np
import tensorflow as tf
from typing import Dict, Optional, List
from pathlib import Path
from daemon_base import BaseDaemon
from world_state import WorldState

logger = logging.getLogger("InferenceDaemon")


class InferenceDaemon(BaseDaemon):
    """
    Intelligence inference daemon - extracts meaning from sensor data.

    Runs multiple TFLite models on 120-feature vectors to understand:
    - Presence (binary: someone is here or not)
    - Activity (multi-class: working, relaxing, moving, absent)

    Future expansion:
    - Anomaly detection
    - Pattern recognition
    - Scene analysis
    """

    # Activity class labels (must match training data)
    ACTIVITY_CLASSES = ['working', 'relaxing', 'moving', 'absent']

    def __init__(self, world_state: WorldState, update_rate: float = 2.0):
        """
        Initialize inference daemon.

        Args:
            world_state: Central world state
            update_rate: How often to run inference (Hz) - default 2 Hz
        """
        super().__init__("intelligence_inference", world_state, update_rate)

        # Model paths
        self.models_dir = Path("intelligence/models")

        # TFLite interpreters
        self.presence_interpreter = None
        self.activity_interpreter = None

        # Latest inference results
        self.latest_presence = None
        self.latest_activity = None
        self.latest_confidence = {}

        # Performance metrics
        self.inference_count = 0
        self.total_inference_time = 0.0

    def initialize(self) -> bool:
        """
        Load TFLite models.

        Returns:
            True if models loaded successfully
        """
        self.logger.info("Initializing Intelligence Inference Daemon...")

        try:
            # Find latest models
            presence_model = self._find_latest_model("presence_detector")
            activity_model = self._find_latest_model("activity_classifier")

            if not presence_model or not activity_model:
                self.logger.error("Could not find required models")
                return False

            # Load presence detection model
            self.logger.info(f"Loading presence model: {presence_model.name}")
            self.presence_interpreter = tf.lite.Interpreter(str(presence_model))
            self.presence_interpreter.allocate_tensors()

            # Load activity classification model
            self.logger.info(f"Loading activity model: {activity_model.name}")
            self.activity_interpreter = tf.lite.Interpreter(str(activity_model))
            self.activity_interpreter.allocate_tensors()

            # Verify input shapes
            presence_input = self.presence_interpreter.get_input_details()[0]
            activity_input = self.activity_interpreter.get_input_details()[0]

            self.logger.info(f"✓ Presence model input shape: {presence_input['shape']}")
            self.logger.info(f"✓ Activity model input shape: {activity_input['shape']}")

            if presence_input['shape'][1] != 120 or activity_input['shape'][1] != 120:
                self.logger.error("Model input shapes do not match expected 120 features")
                return False

            # Update world state
            self.world_state.update("intelligence", {
                "status": "active",
                "models_loaded": {
                    "presence": presence_model.name,
                    "activity": activity_model.name
                },
                "inference_rate_hz": self.update_rate
            })

            self.logger.info("✓ Intelligence Inference Daemon initialized")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}", exc_info=True)
            return False

    def _find_latest_model(self, model_prefix: str) -> Optional[Path]:
        """
        Find the most recent model file matching prefix.

        Args:
            model_prefix: Model name prefix (e.g., "presence_detector")

        Returns:
            Path to latest model or None
        """
        models = sorted(
            self.models_dir.glob(f"{model_prefix}_*.tflite"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if models:
            return models[0]
        else:
            self.logger.error(f"No models found matching {model_prefix}_*.tflite")
            return None

    def update(self) -> None:
        """
        Main update cycle - run inference on latest features.
        """
        if not self.presence_interpreter or not self.activity_interpreter:
            return

        # Get latest features from world state (published by Coral daemon)
        features = self.world_state.get_nested("coral.latest_features")

        if features is None:
            # No features available yet
            return

        # Ensure features are numpy array of shape (1, 120)
        if isinstance(features, list):
            features = np.array(features, dtype=np.float32)

        if features.ndim == 1:
            features = features.reshape(1, -1)

        if features.shape[1] != 120:
            self.logger.warning(f"Invalid feature shape: {features.shape}, expected (1, 120)")
            return

        # Run inference on both models
        start_time = time.perf_counter()

        presence_result = self._infer_presence(features)
        activity_result = self._infer_activity(features)

        inference_time = (time.perf_counter() - start_time) * 1000  # ms

        # Update metrics
        self.inference_count += 1
        self.total_inference_time += inference_time

        # Store results
        self.latest_presence = presence_result
        self.latest_activity = activity_result

        # Update world state with semantic understanding
        self.world_state.update("intelligence.inference", {
            "presence": presence_result,
            "activity": activity_result,
            "inference_ms": inference_time,
            "avg_inference_ms": self.total_inference_time / self.inference_count,
            "timestamp": time.time()
        })

        # Log periodically
        if self.inference_count % 10 == 0:
            self.logger.info(
                f"Inference #{self.inference_count}: "
                f"Presence={presence_result['detected']} ({presence_result['confidence']:.0%}), "
                f"Activity={activity_result['activity']} ({activity_result['confidence']:.0%}), "
                f"{inference_time:.1f}ms"
            )

        # Emit semantic events for behavior engine
        if presence_result['detected'] and presence_result['confidence'] > 0.8:
            self._emit_event("presence_detected", presence_result)

        if activity_result['confidence'] > 0.7:
            self._emit_event("activity_detected", activity_result)

    def _infer_presence(self, features: np.ndarray) -> Dict:
        """
        Run presence detection inference.

        Args:
            features: Feature vector (1, 120)

        Returns:
            Dict with 'detected' (bool) and 'confidence' (float)
        """
        try:
            # Get input/output tensors
            input_details = self.presence_interpreter.get_input_details()[0]
            output_details = self.presence_interpreter.get_output_details()[0]

            # Set input
            self.presence_interpreter.set_tensor(input_details['index'], features)

            # Run inference
            self.presence_interpreter.invoke()

            # Get output (sigmoid probability)
            output = self.presence_interpreter.get_tensor(output_details['index'])
            probability = float(output[0][0])

            return {
                "detected": probability > 0.5,
                "confidence": probability if probability > 0.5 else (1.0 - probability),
                "raw_probability": probability
            }

        except Exception as e:
            self.logger.error(f"Presence inference error: {e}")
            return {"detected": False, "confidence": 0.0, "raw_probability": 0.0}

    def _infer_activity(self, features: np.ndarray) -> Dict:
        """
        Run activity classification inference.

        Args:
            features: Feature vector (1, 120)

        Returns:
            Dict with 'activity' (str), 'confidence' (float), and 'probabilities' (dict)
        """
        try:
            # Get input/output tensors
            input_details = self.activity_interpreter.get_input_details()[0]
            output_details = self.activity_interpreter.get_output_details()[0]

            # Set input
            self.activity_interpreter.set_tensor(input_details['index'], features)

            # Run inference
            self.activity_interpreter.invoke()

            # Get output (softmax probabilities)
            output = self.activity_interpreter.get_tensor(output_details['index'])
            probabilities = output[0]

            # Get top prediction
            top_idx = np.argmax(probabilities)
            top_activity = self.ACTIVITY_CLASSES[top_idx]
            top_confidence = float(probabilities[top_idx])

            # Create probability dict
            prob_dict = {
                activity: float(prob)
                for activity, prob in zip(self.ACTIVITY_CLASSES, probabilities)
            }

            return {
                "activity": top_activity,
                "confidence": top_confidence,
                "probabilities": prob_dict,
                "top_2": sorted(
                    prob_dict.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:2]
            }

        except Exception as e:
            self.logger.error(f"Activity inference error: {e}")
            return {
                "activity": "unknown",
                "confidence": 0.0,
                "probabilities": {},
                "top_2": []
            }

    def _emit_event(self, event_type: str, data: Dict):
        """
        Emit semantic event for behavior engine.

        Args:
            event_type: Event type (e.g., "presence_detected")
            data: Event data
        """
        event = {
            "source": self.daemon_name,
            "event_type": event_type,
            "data": data,
            "timestamp": time.time()
        }

        # Store in world state for behavior engine to consume
        events = self.world_state.get_nested("intelligence.events") or []
        events.append(event)

        # Keep only last 100 events
        if len(events) > 100:
            events = events[-100:]

        self.world_state.update_nested("intelligence.events", events)

    def get_latest_inference(self) -> Dict:
        """
        Get latest inference results.

        Returns:
            Dict with presence and activity results
        """
        return {
            "presence": self.latest_presence,
            "activity": self.latest_activity,
            "timestamp": time.time()
        }

    def cleanup(self) -> None:
        """Clean up resources."""
        self.logger.info("Shutting down Intelligence Inference Daemon...")

        if self.inference_count > 0:
            avg_time = self.total_inference_time / self.inference_count
            self.logger.info(
                f"Inference Statistics: "
                f"{self.inference_count} inferences, "
                f"avg {avg_time:.2f}ms per inference"
            )

        self.presence_interpreter = None
        self.activity_interpreter = None


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create world state
    ws = WorldState()

    # Simulate features from Coral for testing
    # In production, these come from coral_visualization_daemon_enhanced.py
    print("\n" + "="*60)
    print("INTELLIGENCE INFERENCE DAEMON TEST")
    print("="*60)
    print("\nSimulating 120-feature vectors for testing...\n")

    # Create daemon
    daemon = InferenceDaemon(ws, update_rate=2.0)

    if not daemon.initialize():
        print("✗ Initialization failed")
        sys.exit(1)

    print("\n✓ Daemon initialized")
    print("✓ Running inference test with synthetic features...\n")

    # Simulate some feature vectors
    # In production, these would come from the Coral TPU via world state

    # Test 1: Simulate person present and working
    print("Test 1: Simulating presence + working...")
    test_features = np.random.uniform(0.6, 1.0, 120).astype(np.float32)
    ws.update_nested("coral.latest_features", test_features)
    daemon.update()
    time.sleep(0.5)

    # Test 2: Simulate person absent
    print("\nTest 2: Simulating absence...")
    test_features = np.random.uniform(0.0, 0.3, 120).astype(np.float32)
    ws.update_nested("coral.latest_features", test_features)
    daemon.update()
    time.sleep(0.5)

    # Test 3: Simulate person moving
    print("\nTest 3: Simulating movement...")
    test_features = np.random.uniform(0.5, 0.9, 120).astype(np.float32)
    test_features[40:60] = np.random.uniform(0.8, 1.0, 20)  # High motion
    ws.update_nested("coral.latest_features", test_features)
    daemon.update()
    time.sleep(0.5)

    # Show final results
    print("\n" + "="*60)
    print("Final Inference Results:")
    print("="*60)
    results = daemon.get_latest_inference()
    print(f"\nPresence: {results['presence']}")
    print(f"Activity: {results['activity']}")

    print("\n✓ Inference daemon test complete\n")

    daemon.cleanup()
