#!/usr/bin/env python3
"""
Test visualization data flow end-to-end.
Simulates sensor data and verifies it reaches the WebSocket server.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import time
import logging
import asyncio
from world_state import WorldState
from sentient_aura.websocket_server import WebSocketServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("viz_test")

class MockSentientCore:
    """Mock brain that broadcasts sensor data."""

    def __init__(self, world_state, websocket_server):
        self.world_state = world_state
        self.websocket_server = websocket_server
        self.running = False

    def start(self):
        """Start broadcasting test data."""
        self.running = True
        logger.info("Starting mock brain...")

        iteration = 0
        while self.running and iteration < 10:
            # Simulate sensor data in WorldState
            self.world_state.update('environment', {
                'temperature': 20 + (iteration % 10),
                'humidity': 40 + (iteration % 20)
            })

            self.world_state.update('audio', {
                'ambient_noise_level': 0.1 + (iteration % 5) * 0.1
            })

            self.world_state.update('vision', {
                'motion_detected': iteration % 2 == 0,
                'detected_objects': [
                    {'label': 'person', 'confidence': 0.9, 'box': {'x': 100, 'y': 100, 'w': 50, 'h': 100}}
                ] if iteration % 3 == 0 else []
            })

            # Broadcast to WebSocket
            message = {
                'type': 'state_update',
                'state': 'listening',
                'text': f'Test iteration {iteration}',
                'world_state': {
                    'environment': self.world_state.get('environment'),
                    'audio': self.world_state.get('audio'),
                    'vision': self.world_state.get('vision')
                }
            }

            import json
            self.websocket_server.broadcast(json.dumps(message))
            logger.info(f"Broadcasted test data (iteration {iteration})")

            time.sleep(2)
            iteration += 1

        self.running = False
        logger.info("Mock brain stopped")

async def main():
    """Run the visualization test."""
    logger.info("=" * 70)
    logger.info("VISUALIZATION DATA FLOW TEST")
    logger.info("=" * 70)

    # Create components
    world_state = WorldState()
    websocket_server = WebSocketServer(port=8765)

    # Start WebSocket server
    logger.info("Starting WebSocket server on port 8765...")
    await websocket_server.start()
    logger.info("✓ WebSocket server started")

    # Create mock brain
    mock_brain = MockSentientCore(world_state, websocket_server)

    logger.info("\n" + "=" * 70)
    logger.info("INSTRUCTIONS:")
    logger.info("=" * 70)
    logger.info("1. Open http://localhost:8765 in your browser")
    logger.info("2. Or open: file:///home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html")
    logger.info("3. Watch the info panel for sensor data updates")
    logger.info("4. Test will run for 20 seconds (10 iterations)")
    logger.info("=" * 70)
    logger.info("\nStarting in 5 seconds...\n")

    await asyncio.sleep(5)

    # Start broadcasting
    logger.info("Starting data broadcast...")
    mock_brain.start()

    logger.info("\n" + "=" * 70)
    logger.info("TEST COMPLETE")
    logger.info("=" * 70)
    logger.info("✓ Broadcasted 10 test messages")
    logger.info("✓ Each message contained:")
    logger.info("  - Temperature data")
    logger.info("  - Humidity data")
    logger.info("  - Audio level data")
    logger.info("  - Vision data (motion + objects)")
    logger.info("\nCheck browser console for received WebSocket messages")
    logger.info("=" * 70)

    # Cleanup
    await websocket_server.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(0)
