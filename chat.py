#!/usr/bin/env python3
"""
Simple chat interface to communicate with the running Sentient Core
Sends text commands and receives responses
"""
import sys
import time
from sentient_aura.sentient_core import SentientCore
from world_state import WorldState

# Note: The main system is already running with GUI
# This is a simple text interface to send commands

print("=" * 60)
print("  Sentient Core - Chat Interface")
print("=" * 60)
print()
print("The 3D visualizer is running in your browser.")
print("Use this terminal to chat with the AI.")
print()
print("Commands:")
print("  Type naturally to chat")
print("  'quit' or 'exit' to close this chat")
print("  'clear' to reset conversation")
print()
print("=" * 60)
print()

# Simple command loop
try:
    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! The visualizer will continue running.")
            break

        if user_input.lower() == 'clear':
            print("\n" * 50)  # Clear screen
            print("Conversation cleared.\n")
            continue

        # For now, just echo back since the core is running separately
        print()
        print("Note: The main Sentient Core is running separately.")
        print("To see it process your input, the system needs voice input")
        print("or the backend needs to be configured to accept text commands.")
        print()
        print(f"You said: {user_input}")
        print("The visualizer should show state changes from the main system.")
        print()

except KeyboardInterrupt:
    print("\n\nInterrupted. Goodbye!")
    sys.exit(0)
