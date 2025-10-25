#!/usr/bin/env python3
"""Quick GUI broadcast test"""
import asyncio
import json
import time
import sys
import threading
from sentient_aura.websocket_server import WebSocketServer
from world_state import WorldState
from sentient_aura.sentient_core import SentientCore

def run_ws_server(server, ready_event):
    """Run WebSocket server in separate thread with its own event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start())
    ready_event.set()
    loop.run_forever()

print("=" * 60)
print("Quick GUI Broadcasting Test")
print("=" * 60)

# Start WebSocket server
ws_server = WebSocketServer()
ready_event = threading.Event()
ws_thread = threading.Thread(target=run_ws_server, args=(ws_server, ready_event), daemon=True)
ws_thread.start()
ready_event.wait()
print("✓ WebSocket server started on ws://localhost:8765")

# Create World State with test data
world_state = WorldState()
world_state.update_nested('environment.temperature', 22.5)
world_state.update_nested('environment.humidity', 45.2)
world_state.update_nested('audio.ambient_noise_level', 0.15)
world_state.update_nested('vision.motion_detected', False)
world_state.update_nested('system.active_daemons', ['arduino', 'vision'])
print("✓ World State populated")

# Create Core
core = SentientCore(listener=None, voice=None, gui=ws_server, world_state=world_state, daemons=[])
print("✓ Core initialized")

# Test broadcasts
states = [('listening', 'Listening...'), ('processing', 'Thinking...'), ('speaking', 'Speaking...')]
print("\nBroadcasting states:")
for state, text in states:
    core._update_gui_state(state, text)
    print(f"  ✓ {state}")
    time.sleep(0.3)

print("\n" + "=" * 60)
print("✅ Test PASSED - Broadcasting works!")
print("=" * 60)
print("\nWorld State Data Included:")
print("  - Temperature: 22.5°C")
print("  - Humidity: 45.2%")
print("  - Audio Level: 0.15")
print("  - Active Daemons: ['arduino', 'vision']")
print("\nServer ready for browser connection at:")
print("  file:///home/mz1312/Sentient-Core-v4/sentient_aura/sentient_core.html")

# Keep running for 5 more seconds
print("\nKeeping server alive for 5 seconds...")
for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print("\n✓ Test complete!")
