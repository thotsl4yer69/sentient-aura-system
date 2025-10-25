#!/usr/bin/env python3
"""
Simple text chat that works with the visualizer
Sends commands to the running Sentient Core
"""
import time
import queue
import threading
from sentient_aura.sentient_core import SentientCore
from sentient_aura.websocket_server import WebSocketServer
from world_state import WorldState
import asyncio

print("=" * 70)
print("SENTIENT CORE - TEXT CHAT")
print("=" * 70)
print()
print("The visualizer shows the AI's consciousness state.")
print("Type here to communicate with the AI.")
print()
print("Commands: 'quit' to exit, 'clear' for new conversation")
print("=" * 70)
print()

# Create world state
world_state = WorldState()

# Create WebSocket server for visualizer
ws_server = WebSocketServer()

def run_ws_server(server, ready_event):
    """Run WebSocket server in separate thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server.start())
    ready_event.set()
    loop.run_forever()

# Start WebSocket server
print("Starting WebSocket server...")
ready_event = threading.Event()
ws_thread = threading.Thread(target=run_ws_server, args=(ws_server, ready_event), daemon=True)
ws_thread.start()
ready_event.wait()
print("✓ WebSocket server running on ws://localhost:8765")
print("✓ Visualizer should connect automatically")
print()

# Create core
print("Initializing AI core...")
core = SentientCore(
    listener=None,  # No voice input
    voice=None,     # No voice output (we'll print responses)
    gui=ws_server,  # Connect to visualizer
    world_state=world_state,
    daemons=[]
)

# Start the brain
core.start()
print("✓ AI core started")
print()
print("Ready to chat! Type below:")
print()

# Response tracking
last_response_count = 0

try:
    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nShutting down...")
            break

        if user_input.lower() == 'clear':
            print("\n" * 50)
            print("Conversation cleared.\n")
            continue

        # Send command to core
        print()
        core.send_command(user_input)

        # Give it time to process
        print("AI is thinking", end="", flush=True)
        for i in range(10):  # Wait up to 10 seconds
            time.sleep(1)
            print(".", end="", flush=True)

            # Check for new responses in conversation history
            if len(core.conversation_history) > last_response_count:
                last_entry = core.conversation_history[-1]
                if last_entry.get('response'):
                    print()
                    print(f"\nAI: {last_entry['response']}\n")
                    last_response_count = len(core.conversation_history)
                    break
        else:
            print()
            print("\n(AI is still processing... watch the visualizer for state changes)\n")
            last_response_count = len(core.conversation_history)

except KeyboardInterrupt:
    print("\n\nInterrupted by user")

finally:
    core.stop()
    print("\nGoodbye!")
