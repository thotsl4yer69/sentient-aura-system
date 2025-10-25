#!/usr/bin/env python3
"""
Sentient Core v4 - Text-Based Interface
For systems without microphone - communicate via keyboard
"""

import sys
import logging
from world_state import WorldState
from sentient_aura.sentient_core import SentientCore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class TextInterface:
    """Simple text-based interface for Sentient Core."""

    def __init__(self):
        """Initialize text interface."""
        print("=" * 70)
        print("SENTIENT CORE v4 - TEXT INTERFACE")
        print("=" * 70)
        print()

        # Initialize WorldState
        print("Initializing WorldState...")
        self.world_state = WorldState()

        # Initialize the brain (no voice I/O)
        print("Initializing Brain...")
        self.core = SentientCore(
            listener=None,  # No voice input
            voice=None,     # No voice output (responses will print to console)
            gui=None,       # No GUI
            world_state=self.world_state,
            daemons=[]      # No daemons for text mode
        )

        # Start the core
        self.core.start()

        print("\n✓ System initialized!")
        print("\nType your commands below. Type 'help' for available commands, 'quit' to exit.\n")

    def run(self):
        """Run the text interface loop."""
        import sys
        import select

        # Check if stdin is connected to a terminal
        if not sys.stdin.isatty():
            print("Warning: Text interface cannot run in background mode (no terminal attached)")
            print("To use text interface, run directly in a terminal: python3 text_interface.py")
            return

        while True:
            try:
                # Get user input (with better error handling)
                try:
                    user_input = input("You: ").strip()
                except EOFError:
                    # This happens when stdin is closed or running in background
                    print("\nInput stream closed. Use terminal mode or connect via network interface.")
                    break

                if not user_input:
                    continue

                # Handle quit command
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\nShutting down...")
                    break

                # Send command to the core (processes asynchronously)
                print(f"\nProcessing: '{user_input}'...")

                # Get conversation history length before sending
                history_len_before = len(self.core.conversation_history)

                # Send command
                self.core.send_command(user_input)

                # Wait for response (check conversation history)
                import time
                max_wait = 60  # 60 seconds max wait
                waited = 0
                response = None

                while waited < max_wait:
                    time.sleep(0.5)
                    waited += 0.5

                    # Check if response was added to history
                    if len(self.core.conversation_history) > history_len_before:
                        last_entry = self.core.conversation_history[-1]
                        if last_entry.get('response'):
                            response = last_entry['response']
                            break

                # Display response
                if response:
                    print(f"Aura: {response}\n")
                else:
                    print(f"Aura: (No response generated - timeout or error)\n")

            except KeyboardInterrupt:
                print("\n\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
                logging.exception("Error in text interface")

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'core') and self.core:
            print("Stopping core...")
            self.core.stop()
        print("Goodbye!")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Sentient Core v4 - Text Mode")
    print("No microphone required - Type your commands")
    print("=" * 70 + "\n")

    interface = TextInterface()

    try:
        interface.run()
    finally:
        interface.cleanup()
