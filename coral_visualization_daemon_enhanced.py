#!/usr/bin/env python3
"""
Enhanced Coral Visualization Daemon
===================================

This version integrates the CognitiveIntegrationMixin to add personality-driven
behavior to the high-performance Coral visualization.

Key enhancements:
- Inherits from CognitiveIntegrationMixin
- Determines personality state from sensor data
- Updates cognitive engine with current state
- Broadcasts cognitive state via WebSocket
- Applies personality-driven physics to particles
"""

import sys
import os
import threading
import time
import logging
import json
from typing import Dict, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from coral_visualization_daemon import CoralVisualizationDaemon, FeatureExtractor, ParticleInterpolator, PerformanceMetrics
from sentient_core_cognitive_integration import CognitiveIntegrationMixin

logger = logging.getLogger("EnhancedCoralViz")


class EnhancedCoralVisualizationDaemon(CoralVisualizationDaemon, CognitiveIntegrationMixin):
    """
    Enhanced Coral daemon with cognitive integration.
    """

    def __init__(self, world_state, websocket_server, config):
        """
        Initialize the enhanced daemon.
        """
        self.logger = logging.getLogger("EnhancedCoralViz")
        # Initialize the parent CoralVisualizationDaemon
        super().__init__(world_state, websocket_server, config)

        # Initialize the CognitiveIntegrationMixin
        self.initialize_cognitive_engine()

        # Initialize the Particle Physics Engine
        from sentient_aura.particle_physics import ParticlePhysicsEngine
        self.particle_engine = ParticlePhysicsEngine(num_particles=10000)
        self.particle_engine.reset_positions(distribution="humanoid")


        logger.info("✓ Enhanced Coral Visualization Daemon Initialized with Cognitive Engine and Particle Physics")

    def run(self):
        """
        Main daemon loop - runs at target FPS, now with cognitive updates.
        """
        target_fps = self.config.get('target_fps', 60)
        logger.info(f"EnhancedCoralVisualizationDaemon starting (target: {target_fps} FPS)")

        # This is a deviation from the original plan, but the Coral TPU is not available.
        # We will run the particle physics engine directly and broadcast the results.
        self.running = True
        target_frame_time = 1.0 / target_fps

        logger.info("=" * 60)
        logger.info("ENHANCED VISUALIZATION DAEMON ACTIVE (CPU MODE)")
        logger.info(f"Target FPS: {target_fps}")
        logger.info(f"Frame budget: {target_frame_time*1000:.2f}ms")
        logger.info("=" * 60)

        last_sensor_broadcast_time = time.time()

        while self.running:
            frame_start = time.perf_counter()

            try:
                # 1. Update cognitive state based on world state
                self.update_cognitive_state()

                # 2. Get cognitive profile
                current_profile = self.cognitive_engine.get_current_profile()
                breathing_factor = self.cognitive_engine.get_breathing_factor()

                # 3. Update particle physics
                dt = target_frame_time
                particles = self.particle_engine.update(
                    dt=dt,
                    cohesion=current_profile.cohesion,
                    separation=current_profile.separation,
                    alignment=current_profile.alignment,
                    wander=current_profile.wander,
                    breath_factor=breathing_factor,
                    speed_multiplier=current_profile.particle_speed,
                )

                # 4. Interpolate for smooth motion
                interp_start = time.perf_counter()
                smooth_particles = self.interpolator.update(particles)
                interp_time = time.perf_counter() - interp_start

                # 5. Broadcast particles and cognitive state
                broadcast_start = time.perf_counter()
                self._broadcast_particles(smooth_particles, 0, interp_time)
                self.broadcast_cognitive_state() # From the mixin
                broadcast_time = time.perf_counter() - broadcast_start

                # 6. Broadcast sensor data periodically
                now = time.time()
                if now - last_sensor_broadcast_time > 2.0: # Every 2 seconds
                    self.broadcast_sensor_data()
                    last_sensor_broadcast_time = now

                # 7. Update metrics
                frame_time = time.perf_counter() - frame_start
                self.metrics.record_frame(frame_time)
                self.metrics.record_component('interpolation', interp_time)
                self.metrics.record_component('broadcast', broadcast_time)
                self.frame_counter += 1

                # 8. Report metrics every 5 seconds
                if time.time() - self.last_metrics_report > 5.0:
                    self._report_metrics()
                    self.last_metrics_report = time.time()

                # 9. Sleep to maintain target FPS
                sleep_time = target_frame_time - frame_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.error(f"Frame {self.frame_counter} error: {e}")
                logger.exception("Full traceback:")
                time.sleep(0.1)

        logger.info("EnhancedCoralVisualizationDaemon stopped")


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Mock objects for testing
    class MockWorldState:
        def __init__(self):
            self._state = {
                'wifi_scanner': {'networks': [{'ssid': 'test-wifi'}]},
                'bluetooth_scanner': {'devices': [{'name': 'test-bt'}]},
                'audio': {'amplitude': 0.1, 'speech_detected': True},
                'imu': {'motion_detected': True},
                'vision': {'person_detected': True, 'face_known': True}
            }
        def get_snapshot(self):
            return self._state
        def get(self, key, default=None):
            return self._state.get(key, default)

    class MockWebSocketServer:
        def __init__(self):
            self.clients = []
        def broadcast(self, message):
            msg_data = json.loads(message)
            msg_type = msg_data.get('type')
            if msg_type == 'cognitive_state':
                logger.info(f"Broadcast Cognitive State: {msg_data['state']['name']}")
            # else:
            #     logger.info(f"Broadcast: {msg_type} ({len(message)} bytes)")


    # Test configuration
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'sentient_config.json'))
    
    # Default config if file not found
    viz_config = {
        'target_fps': 30,
        'model_path': 'models/sentient_viz_edgetpu.tflite',
        'fallback_mode': 'llm',
        'enable_metrics': True,
        'interpolation_alpha': 0.3
    }

    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            sentient_config = json.load(f)
            viz_config.update(sentient_config.get('coral_visualization', {}))
            # Ensure model path is absolute
            viz_config['model_path'] = os.path.join(os.path.dirname(__file__), viz_config['model_path'])


    logger.info("="*70)
    logger.info("ENHANCED CORAL VISUALIZATION DAEMON TEST")
    logger.info("="*70)

    # Create daemon
    daemon = EnhancedCoralVisualizationDaemon(
        world_state=MockWorldState(),
        websocket_server=MockWebSocketServer(),
        config=viz_config
    )

    # Start the daemon in a thread
    daemon_thread = threading.Thread(target=daemon.run, daemon=True)
    daemon_thread.start()

    try:
        # Let it run for a few seconds to see state changes
        for i in range(10):
            time.sleep(2)
            # You could modify the mock world state here to test different personality states
            logger.info(f"Current personality: {daemon.current_personality_state}")

    except KeyboardInterrupt:
        logger.info("Stopping test...")
    finally:
        daemon.stop()
        daemon_thread.join(timeout=5)

    logger.info("="*70)
    logger.info("✓ TEST COMPLETE")
    logger.info("="*70)