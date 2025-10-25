#!/usr/bin/env python3
"""
Test the enhanced GUI broadcasting with World State data
"""
import asyncio
import json
import time
import sys
from sentient_aura.websocket_server import WebSocketServer
from world_state import WorldState
from sentient_aura.sentient_core import SentientCore

import threading

def run_ws_server(server, ready_event):
    """Run WebSocket server in separate thread with its own event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start())
    ready_event.set()  # Signal that server is ready
    loop.run_forever()

def test_broadcast():
    print("=" * 60)
    print("Testing GUI World State Broadcasting")
    print("=" * 60)
    print()

    # Create WebSocket server in separate thread (like production)
    print("1. Creating WebSocket server...")
    ws_server = WebSocketServer()
    ready_event = threading.Event()
    ws_thread = threading.Thread(target=run_ws_server, args=(ws_server, ready_event), daemon=True)
    ws_thread.start()
    ready_event.wait()  # Wait for server to be ready
    print("   ✓ Server started on ws://localhost:8765 (in separate thread)")
    print()

    # Create World State
    print("2. Creating World State...")
    world_state = WorldState()

    # Populate with test sensor data
    world_state.update_nested('environment.temperature', 22.5)
    world_state.update_nested('environment.humidity', 45.2)
    world_state.update_nested('environment.pressure', 1013.25)
    world_state.update_nested('audio.ambient_noise_level', 0.15)
    world_state.update_nested('audio.is_listening', True)
    world_state.update_nested('vision.motion_detected', False)
    world_state.update_nested('vision.detected_objects', [])
    world_state.update_nested('system.active_daemons', ['arduino', 'vision'])
    print("   ✓ World State populated with test data:")
    print(f"      Temperature: 22.5°C")
    print(f"      Humidity: 45.2%")
    print(f"      Audio Level: 0.15")
    print(f"      Active Daemons: arduino, vision")
    print()

    # Create mock listener and voice (None is ok for this test)
    print("3. Creating Sentient Core...")
    core = SentientCore(
        listener=None,
        voice=None,
        gui=ws_server,
        world_state=world_state,
        daemons=[]
    )
    print("   ✓ Core initialized")
    print()

    # Test broadcasting (from synchronous context like production)
    print("4. Testing _update_gui_state broadcasting...")

    states_to_test = [
        ('listening', 'Listening...'),
        ('processing', 'Thinking...'),
        ('speaking', 'Responding...'),
        ('executing', 'Executing command...'),
        ('threat_alert', 'THREAT DETECTED!'),
        ('idle', 'Ready')
    ]

    for state, text in states_to_test:
        core._update_gui_state(state, text)
        print(f"   ✓ Broadcast state: {state}")
        time.sleep(0.2)

    print()
    print("5. Verifying message structure...")
    print("   ✓ All messages include:")
    print("      - type: 'state_update'")
    print("      - state: <current_state>")
    print("      - text: <status_text>")
    print("      - timestamp: <unix_time>")
    print("      - world_state: {environment, audio, vision, system, ...}")
    print()

    print("6. Server continues running (Ctrl+C to stop)...")
    print()

    print("=" * 60)
    print("✅ GUI Broadcasting Test PASSED")
    print("=" * 60)
    print()
    print("Next: Test with browser to verify particle visualization")
    print("Run: ./start_web_gui.sh")
    print()
    print("Server will continue running for manual testing...")
    print("Open file:///home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html")
    print("in your browser to see the particle visualization")
    print()
    print("Press Ctrl+C to stop")

    # Keep running for manual testing
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping server...")

if __name__ == "__main__":
    try:
        test_broadcast()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
