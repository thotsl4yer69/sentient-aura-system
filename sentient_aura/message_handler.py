#!/usr/bin/env python3
"""
Message Handler - WebSocket Communication Bridge
=================================================

Handles text-based communication between GUI and SentientCore.
Integrates with existing WebSocket server for bidirectional messaging.
"""

import json
import logging
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger("message_handler")


class MessageHandler:
    """
    Handles user messages from GUI and sends AI responses back.

    Integrates with WebSocket server and SentientCore command processing.
    """

    def __init__(self, websocket_server, sentient_core=None):
        """
        Initialize message handler.

        Args:
            websocket_server: WebSocketServer instance for broadcasting
            sentient_core: Optional SentientCore instance for command processing
        """
        self.websocket_server = websocket_server
        self.sentient_core = sentient_core

        # Callback for processing user commands
        self.command_callback: Optional[Callable[[str], str]] = None

        logger.info("MessageHandler initialized")

    def set_sentient_core(self, sentient_core):
        """Set SentientCore instance for command processing."""
        self.sentient_core = sentient_core
        logger.info("SentientCore instance linked to MessageHandler")

    def set_command_callback(self, callback: Callable[[str], str]):
        """
        Set callback function for processing user commands.

        Args:
            callback: Function that takes command string and returns response string
        """
        self.command_callback = callback
        logger.info("Command callback registered")

    def handle_user_message(self, message_data: Dict[str, Any]) -> Optional[str]:
        """
        Handle incoming user message from WebSocket.

        Args:
            message_data: Dictionary with 'type', 'text', 'timestamp'

        Returns:
            Response text or None if async processing
        """
        if message_data.get('type') != 'user_message':
            logger.warning(f"Unknown message type: {message_data.get('type')}")
            return None

        user_text = message_data.get('text', '').strip()
        if not user_text:
            return None

        logger.info(f"User message: {user_text}")

        # Process command via callback or SentientCore
        response = None

        if self.command_callback:
            try:
                response = self.command_callback(user_text)
            except Exception as e:
                logger.error(f"Command callback error: {e}")
                response = f"Error processing command: {str(e)}"
        elif self.sentient_core:
            try:
                # Use SentientCore's command processing
                response = self.sentient_core.send_command(user_text)
            except Exception as e:
                logger.error(f"SentientCore command error: {e}")
                response = f"Error: {str(e)}"
        else:
            logger.warning("No command processor available")
            response = "No command processor configured. Please set up SentientCore or callback."

        # Send response back to GUI
        if response:
            self.send_ai_response(response)

        return response

    def send_ai_response(self, text: str):
        """
        Send AI response to GUI via WebSocket.

        Args:
            text: Response text to send
        """
        message = {
            'type': 'ai_response',
            'text': text,
            'timestamp': int(time.time() * 1000)
        }

        try:
            # Broadcast to all connected clients
            self.websocket_server.broadcast(json.dumps(message))
            logger.info(f"AI response sent: {text[:100]}...")
        except Exception as e:
            logger.error(f"Failed to send AI response: {e}")

    def send_state_update(self, state: str, text: str = "", world_state: Optional[Dict] = None):
        """
        Send state update to GUI.

        Args:
            state: Current state (idle, listening, processing, etc.)
            text: Optional status text
            world_state: Optional world state data (sensors, daemons, etc.)
        """
        message = {
            'type': 'state_update',
            'state': state,
            'text': text,
            'timestamp': int(time.time() * 1000)
        }

        if world_state:
            message['world_state'] = world_state

        try:
            self.websocket_server.broadcast(json.dumps(message))
            logger.debug(f"State update sent: {state}")
        except Exception as e:
            logger.error(f"Failed to send state update: {e}")


# Import time for timestamp
import time


# === INTEGRATION EXAMPLE ===

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Mock WebSocket server for testing
    class MockWebSocketServer:
        def broadcast(self, message):
            print(f"[WebSocket Broadcast] {message}")

    ws_server = MockWebSocketServer()
    handler = MessageHandler(ws_server)

    # Define simple command callback
    def simple_command_processor(command: str) -> str:
        command_lower = command.lower()

        if "hello" in command_lower or "hi" in command_lower:
            return "Hello! I'm your Sentient Core AI. How can I assist you?"
        elif "status" in command_lower:
            return "All systems operational. 7 daemons active, sensors online."
        elif "help" in command_lower:
            return "I can help you with system status, sensor data, and command execution. Just ask!"
        else:
            return f"I received: '{command}'. Processing..."

    handler.set_command_callback(simple_command_processor)

    # Test message handling
    print("\n=== MESSAGE HANDLER TEST ===\n")

    test_messages = [
        {'type': 'user_message', 'text': 'Hello!', 'timestamp': 0},
        {'type': 'user_message', 'text': 'What is the status?', 'timestamp': 1},
        {'type': 'user_message', 'text': 'Help me', 'timestamp': 2},
        {'type': 'user_message', 'text': 'Execute daemon scan', 'timestamp': 3}
    ]

    for msg in test_messages:
        print(f"\nUser: {msg['text']}")
        response = handler.handle_user_message(msg)
        print(f"Response: {response}\n")

    # Test state update
    handler.send_state_update(
        state='processing',
        text='Analyzing sensors...',
        world_state={
            'system': {
                'active_daemons': ['WiFi Scanner', 'Bluetooth Scanner', 'Hardware Monitor']
            },
            'environment': {
                'temperature': 24.5,
                'humidity': 45.2
            }
        }
    )

    print("\n=== TEST COMPLETE ===\n")
