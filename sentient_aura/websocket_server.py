#!/usr/bin/env python3
"""
WebSocket Server for Sentient Aura (Production-Ready)

Acts as a bridge between the Python core and the three.js visual interface.

Features:
- Binary protocol support (120KB vs 500KB+ JSON)
- Connection pooling with max connections
- Rate limiting per client
- Client health tracking
- Graceful error handling
- User text input handling
- Personality state and sensor data broadcasting
"""

import asyncio
import websockets
import logging
import time
import json
from collections import defaultdict
from typing import Set, Dict, Optional, Callable

logger = logging.getLogger("websocket_server")

class ClientInfo:
    """Track client connection metadata."""
    def __init__(self, websocket):
        self.websocket = websocket
        self.connected_at = time.time()
        self.last_message_at = time.time()
        self.message_count = 0
        self.error_count = 0

class WebSocketServer:
    def __init__(self, host="localhost", port=8765, max_connections=10, message_handler: Optional[Callable] = None):
        print("WebSocketServer instantiated (Production)")
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.server = None
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_info: Dict[websockets.WebSocketServerProtocol, ClientInfo] = {}
        self.loop = None  # Store event loop reference
        self.message_handler = message_handler  # Callback for handling incoming messages

        # Rate limiting (messages per second per client)
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max = 3600   # max messages per window (60 FPS)

    async def handler(self, websocket):
        """Handle incoming WebSocket connections with rate limiting and max connections."""
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"

        # Check max connections
        if len(self.clients) >= self.max_connections:
            logger.warning(f"Max connections reached ({self.max_connections}), rejecting {client_ip}")
            await websocket.close(1008, "Server at maximum capacity")
            return

        # Accept connection
        logger.info(f"Client connected from {websocket.remote_address} ({len(self.clients) + 1}/{self.max_connections})")
        self.clients.add(websocket)
        self.client_info[websocket] = ClientInfo(websocket)

        try:
            async for message in websocket:
                # Update client stats
                info = self.client_info[websocket]
                info.last_message_at = time.time()
                info.message_count += 1

                # Rate limiting check
                if info.message_count > self.rate_limit_max:
                    elapsed = time.time() - info.connected_at
                    if elapsed < self.rate_limit_window:
                        logger.warning(f"Rate limit exceeded for {client_ip}")
                        await websocket.close(1008, "Rate limit exceeded")
                        break

                # Handle incoming message
                try:
                    # Try to parse as JSON
                    if isinstance(message, str):
                        data = json.loads(message)
                        logger.debug(f"Received JSON message from {client_ip}: {data.get('type', 'unknown')}")

                        # Handle user text input
                        if data.get('type') == 'user_message':
                            await self._handle_user_message(websocket, data)

                        # Call external message handler if provided
                        elif self.message_handler:
                            await self.message_handler(websocket, data)

                    else:
                        # Binary message (not handled here - likely particle data echo)
                        logger.debug(f"Received binary message from {client_ip}: {len(message)} bytes")

                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {client_ip}")
                except Exception as e:
                    logger.error(f"Error handling message from {client_ip}: {e}")

        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"Client disconnected from {client_ip}: {e.code} {e.reason}")
        except Exception as e:
            logger.error(f"Error handling client {client_ip}: {e}")
            if websocket in self.client_info:
                self.client_info[websocket].error_count += 1
        finally:
            # Cleanup
            self.clients.discard(websocket)
            if websocket in self.client_info:
                del self.client_info[websocket]
            logger.info(f"Client removed ({len(self.clients)}/{self.max_connections} connected)")

    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"Starting WebSocket server on ws://{self.host}:{self.port}")
        self.loop = asyncio.get_event_loop()  # Capture the event loop
        self.server = await websockets.serve(self.handler, self.host, self.port)

    async def stop(self):
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket server stopped")

    async def _async_broadcast(self, message):
        """Internal async broadcast method."""
        if self.clients:
            # Send to all clients concurrently
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True  # Don't fail if one client errors
            )

    def broadcast(self, message):
        """Thread-safe broadcast method - can be called from any thread."""
        if self.loop and self.loop.is_running():
            # Schedule the coroutine in the WebSocket server's event loop
            asyncio.run_coroutine_threadsafe(self._async_broadcast(message), self.loop)
        else:
            logger.warning("WebSocket server loop not running, cannot broadcast")

    async def _handle_user_message(self, websocket, data: Dict):
        """
        Handle user text message from GUI.

        Args:
            websocket: Client websocket
            data: Message data with 'text' field
        """
        text = data.get('text', '').strip()
        if not text:
            return

        logger.info(f"User message: {text}")

        # Import here to avoid circular dependency
        try:
            # TODO: Integrate with SentientCore for actual command processing
            # For now, send a placeholder response
            response = {
                "type": "ai_response",
                "text": f"I received your message: '{text}'. Command processing integration is pending.",
                "timestamp": time.time()
            }

            await websocket.send(json.dumps(response))

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            error_response = {
                "type": "error",
                "message": "Failed to process your message",
                "timestamp": time.time()
            }
            await websocket.send(json.dumps(error_response))

    def send_personality_state(self, state: str, profile: Dict):
        """
        Send personality state update to all clients.

        Args:
            state: Personality state name
            profile: Cognitive profile parameters
        """
        message = {
            "type": "personality_state",
            "state": state,
            "profile": profile,
            "timestamp": time.time()
        }
        self.broadcast(json.dumps(message))

    def send_sensor_data(self, sensor_data: Dict):
        """
        Send sensor data update to all clients.

        Args:
            sensor_data: Dictionary of sensor readings
        """
        message = {
            "type": "sensor_data",
            "data": sensor_data,
            "timestamp": time.time()
        }
        self.broadcast(json.dumps(message))

# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    server = WebSocketServer()

    async def main():
        await server.start()
        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            await server.stop()

    asyncio.run(main())
