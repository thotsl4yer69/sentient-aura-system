#!/usr/bin/env python3
"""
Sentient Core - The Brain of the Aura System
Handles command parsing, state management, and personality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add parent directory to path for hardware imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import logging
import threading
import queue
import uuid
from typing import Dict, Optional, Callable

# Import sentient_aura config explicitly (not drone defense config)
from sentient_aura import config

logger = logging.getLogger("sentient_core")


class SentientCore:
    """The brain of the Sentient Aura system."""

    def __init__(self, listener=None, voice=None, gui=None, world_state=None, daemons=None):
        """
        Initialize the Sentient Core.

        Args:
            listener: ContinuousListener instance
            voice: VoicePiper instance
            gui: AuraInterface instance
            world_state: WorldState instance (shared with daemons)
            daemons: List of hardware daemons (FlipperDaemon, VisionDaemon, etc.)
        """
        logger.info("Initializing Sentient Core...")

        # Components
        self.listener = listener
        self.voice = voice
        self.gui = gui

        # Drone Defense System Integration
        self.world_state = world_state
        self.daemons = daemons or []
        self.daemon_dict = {d.daemon_name: d for d in self.daemons}

        # State machine
        self.state = config.STATE_IDLE
        self.previous_state = None

        # Hardware discovery (deprecated - now using world_state)
        self.hardware_discovery = None
        self.hardware_caps = {}

        # Command queue
        self.command_queue = queue.Queue()

        # Threading
        self.running = False
        self.brain_thread = None

        # Stats
        self.commands_processed = 0
        self.last_command_time = 0

        # Conversation history (for context)
        self.conversation_history = []

        # Phase 3: Closed-loop command tracking
        self.active_commands = {}  # command_id -> {intent, timestamp, status, result}
        self.command_history = []  # List of completed commands
        self.next_command_id = 0

        logger.info("✓ Sentient Core initialized")

    def _generate_command_id(self) -> str:
        """
        Generate a unique command ID.

        Returns:
            str: Unique command ID (e.g., "CMD_001", "CMD_002", etc.)
        """
        self.next_command_id += 1
        return f"CMD_{self.next_command_id:03d}"

    def _track_command(self, command_id: str, intent: str) -> None:
        """
        Start tracking a new command.

        Args:
            command_id: Unique command identifier
            intent: Command intent (scan, status, etc.)
        """
        self.active_commands[command_id] = {
            'intent': intent,
            'timestamp': time.time(),
            'status': 'initiated',
            'result': None
        }
        logger.debug(f"Command tracking started: {command_id} ({intent})")

    def _check_command_status(self, command_id: str) -> Optional[str]:
        """
        Check the status of a command from WorldState.

        Args:
            command_id: Command ID to check

        Returns:
            str: Status ('acknowledged', 'completed', 'failed', None)
        """
        if self.world_state is None:
            return None

        try:
            command_status = self.world_state.get('command_status')
            if command_status and command_id in command_status:
                return command_status[command_id].get('status')
        except Exception as e:
            logger.error(f"Error checking command status: {e}")

        return None

    def _complete_command(self, command_id: str, status: str, result: dict = None) -> None:
        """
        Mark a command as complete and move to history.

        Args:
            command_id: Command ID
            status: Final status ('completed', 'failed')
            result: Optional result data
        """
        if command_id in self.active_commands:
            command = self.active_commands[command_id]
            command['status'] = status
            command['result'] = result
            command['completion_time'] = time.time()

            # Move to history
            self.command_history.append(command)

            # Remove from active
            del self.active_commands[command_id]

            logger.info(f"Command {command_id} completed: {status}")

    def _get_hardware_status(self) -> Dict[str, bool]:
        """Query current hardware status from WorldState."""
        if self.world_state is None:
            # Fallback simulation mode
            return {
                'camera_rgb': config.SIMULATE_CAMERA,
                'flipper_zero': False,
                'pir_motion': False,
                'microphone_array': config.SIMULATE_MICROPHONE,
                'bme280_env': config.SIMULATE_SENSORS
            }

        # Read from WorldState capabilities
        try:
            capabilities = self.world_state.get('capabilities')
            if capabilities:
                return {
                    'camera_rgb': capabilities.get('vision', False),
                    'vision_daemon': capabilities.get('vision_daemon', False),
                    'flipper_zero': capabilities.get('rf_detection', False),
                    'pir_motion': capabilities.get('prototype_board', False),
                    'microphone_array': capabilities.get('audio', False),
                    'bme280_env': capabilities.get('environment', False),
                    'thermal_camera': capabilities.get('thermal_vision', False),
                    'depth_camera': capabilities.get('depth_vision', False),
                    'gps': capabilities.get('gps', False),
                    'lidar': capabilities.get('lidar', False)
                }
            else:
                # Fallback: check if daemons are running
                return {
                    'flipper_zero': 'flipper' in self.daemon_dict,
                    'vision_daemon': 'visiond' in self.daemon_dict,
                    'prototype_board': any('prototype' in d for d in self.daemon_dict.keys())
                }

        except Exception as e:
            logger.error(f"Error reading hardware status: {e}")
            return {}

    def _parse_command(self, text: str) -> tuple:
        """
        Parse user input into command intent.

        Args:
            text: User's spoken text

        Returns:
            tuple: (intent, confidence, entities)
        """
        text_lower = text.lower()

        # Check for each command pattern
        for intent, patterns in config.COMMANDS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    logger.debug(f"Matched intent: {intent} (pattern: '{pattern}')")
                    return (intent, 0.9, {'query': text})

        # No match found
        return ('unknown', 0.0, {'query': text})

    def _generate_response(self, intent: str, entities: dict) -> str:
        """
        Generate a personality-driven response.

        Args:
            intent: Command intent
            entities: Extracted entities from command

        Returns:
            str: Response text
        """
        # Acknowledgment patterns
        ack = random.choice(config.ACKNOWLEDGMENTS)

        if intent == 'status' or intent == 'health':
            # Get hardware status
            sensors = self._get_hardware_status()
            online = [name for name, available in sensors.items() if available]
            offline = [name for name, available in sensors.items() if not available]

            if len(online) == len(sensors):
                return "I'm feeling great! All my sensors are online and ready to go."
            elif len(online) > len(offline):
                return f"{ack} Most of my systems are up. I have {len(online)} sensors online."
            else:
                return f"I'm running, but some sensors are napping. {len(online)} of {len(sensors)} are online."

        elif intent == 'scan':
            # Check if Flipper is available
            if self.world_state and 'flipper' in self.daemon_dict:
                return f"{ack} Initiating RF spectrum scan. Searching for drone frequencies now."
            else:
                return "I would love to scan, but my Flipper Zero isn't connected right now."

        elif intent == 'monitor':
            return f"{ack} Entering monitoring mode. I'll alert you immediately if I detect any drone signatures."

        elif intent == 'alert':
            return "You got it! I'll alert you right away if anything comes up."

        elif intent == 'temperature':
            # Try to get temperature from BME280
            if config.USE_HARDWARE_DISCOVERY:
                return "Let me check the temperature for you. Give me a second."
            else:
                return "I don't have a temperature sensor connected right now. Sorry about that!"

        elif intent == 'threats':
            # Check actual threat status from WorldState
            if self.world_state:
                flipper_state = self.world_state.get('flipper')
                if flipper_state:
                    active_threats = flipper_state.get('active_threats', 0)
                    total_detections = flipper_state.get('total_detections', 0)

                    if active_threats > 0:
                        return f"Warning! I'm detecting {active_threats} active drone signal{'' if active_threats == 1 else 's'} right now!"
                    elif total_detections > 0:
                        return f"No active threats at the moment, but I've detected {total_detections} signals since startup."
                    else:
                        return "All clear! No drone signals detected. The airspace is clean."
                else:
                    return "I'm not currently monitoring for threats. My RF sensors aren't active."
            else:
                return "Everything looks clear from where I'm sitting. No threats detected."

        elif intent == 'help':
            return ("I can help you with sensor status, frequency scanning, monitoring, "
                    "and alerting. Just tell me what you need!")

        elif intent == 'test':
            return "All systems are operational! I can hear you perfectly."

        elif intent == 'unknown':
            # Friendly fallback
            responses = [
                "I'm not sure I caught that. Could you try asking differently?",
                "Hmm, I didn't quite understand. What can I help you with?",
                "That's a new one for me! Can you rephrase that?",
                "I'm still learning. Mind asking that another way?"
            ]
            return random.choice(responses)

        else:
            return "I'm working on it!"

    def _execute_command(self, intent: str, entities: dict):
        """
        Execute the command action - PHASE 2: Hardware integration.

        Args:
            intent: Command intent
            entities: Extracted entities
        """
        logger.info(f"Executing command: {intent}")

        # Update GUI to show we're executing
        self._update_gui_state(config.STATE_EXECUTING, f"Executing: {intent}")

        try:
            if intent == 'status':
                # Show sensor display with real hardware data
                sensors = self._get_hardware_status()
                if self.gui:
                    self.gui.state_queue.put({
                        'state': config.STATE_EXECUTING,
                        'text': 'Sensor Status',
                        'sensors': sensors,
                        'show_sensors': True
                    })
                time.sleep(0.5)  # Brief pause for visual effect

            elif intent == 'scan':
                # Execute RF scan via Flipper daemon
                result = self._execute_rf_scan()
                if result.get('success'):
                    logger.info(f"RF scan initiated: {result}")
                else:
                    logger.warning(f"RF scan failed: {result.get('error')}")

            elif intent == 'threats':
                # Check for active threats in WorldState
                self._check_threats()

            elif intent == 'temperature':
                # Read temperature from environment sensors
                self._read_temperature()

            elif intent == 'test':
                # Just a test response, no action needed
                pass

            # Add more command handlers as needed

        except Exception as e:
            logger.error(f"Command execution error: {e}")

    def _execute_rf_scan(self) -> dict:
        """
        Execute RF frequency scan via Flipper daemon with command tracking.

        Returns:
            dict: Result with success status, data, and command_id
        """
        if 'flipper' not in self.daemon_dict:
            return {'success': False, 'error': 'Flipper daemon not available'}

        try:
            from sensor_events import ActionCommand

            # Generate unique command ID
            command_id = self._generate_command_id()

            # Track command
            self._track_command(command_id, 'rf_scan')

            # Get Flipper daemon
            flipper = self.daemon_dict['flipper']

            # Create scan command with command ID
            scan_cmd = ActionCommand(
                target_daemon='flipper',
                action='scan',
                parameters={
                    'frequencies': ['2.4GHz', '5.8GHz', '433MHz', '915MHz'],
                    'command_id': command_id  # Include command ID for tracking
                }
            )

            # Execute action
            result = flipper.execute_action(scan_cmd)
            logger.info(f"RF scan initiated: {command_id}")

            # Check initial acknowledgment
            status = self._check_command_status(command_id)
            if status == 'acknowledged':
                logger.info(f"Command {command_id} acknowledged by Flipper daemon")

            # Add command_id to result
            result['command_id'] = command_id

            return result

        except Exception as e:
            logger.error(f"RF scan error: {e}")
            return {'success': False, 'error': str(e)}

    def _check_threats(self):
        """Check WorldState for active threats."""
        if self.world_state is None:
            return

        try:
            # Get Flipper state
            flipper_state = self.world_state.get('flipper')
            if flipper_state:
                active_threats = flipper_state.get('active_threats', 0)
                total_detections = flipper_state.get('total_detections', 0)

                logger.info(f"Threat status: {active_threats} active, {total_detections} total detections")

                if self.voice and active_threats > 0:
                    self.voice.speak(f"Warning! {active_threats} active drone signal{'' if active_threats == 1 else 's'} detected!", blocking=False)

        except Exception as e:
            logger.error(f"Threat check error: {e}")

    def _read_temperature(self):
        """Read temperature from environment sensors."""
        if self.world_state is None:
            return

        try:
            env = self.world_state.get('environment')
            if env:
                temp = env.get('temperature')
                if temp is not None:
                    logger.info(f"Current temperature: {temp}°C")
                    if self.voice:
                        self.voice.speak(f"The current temperature is {temp:.1f} degrees Celsius", blocking=False)
                else:
                    logger.info("Temperature sensor not available")

        except Exception as e:
            logger.error(f"Temperature read error: {e}")

    def _update_gui_state(self, state: str, text: str = "", **kwargs):
        """Update GUI state."""
        if self.gui:
            update = {
                'state': state,
                'text': text
            }
            update.update(kwargs)
            self.gui.state_queue.put(update)

    def _process_input(self, text: str):
        """
        Process a voice input through the full pipeline.

        Args:
            text: Transcribed text from listener
        """
        logger.info(f"Processing input: '{text}'")
        self.commands_processed += 1
        self.last_command_time = time.time()

        # Add to history
        self.conversation_history.append({
            'timestamp': time.time(),
            'user': text,
            'response': None
        })

        # Trim history
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]

        # LISTENING → PROCESSING
        self._set_state(config.STATE_PROCESSING)
        self._update_gui_state(config.STATE_PROCESSING, "Thinking...")

        # Parse command
        intent, confidence, entities = self._parse_command(text)
        logger.info(f"Intent: {intent} (confidence: {confidence})")

        # Generate response
        response = self._generate_response(intent, entities)
        logger.info(f"Response: '{response}'")

        # Update history
        self.conversation_history[-1]['response'] = response

        # PROCESSING → SPEAKING
        self._set_state(config.STATE_SPEAKING)
        self._update_gui_state(
            config.STATE_SPEAKING,
            "Speaking...",
            transcription=response
        )

        # Speak response
        if self.voice:
            self.voice.speak(response, blocking=True)

        # SPEAKING → EXECUTING (if command needs action)
        if intent in ['scan', 'status', 'monitor']:
            self._set_state(config.STATE_EXECUTING)
            self._execute_command(intent, entities)

        # EXECUTING → IDLE (back to listening)
        self._set_state(config.STATE_IDLE)
        self._update_gui_state(config.STATE_LISTENING, "Listening...")

    def _set_state(self, new_state: str):
        """Update the core's state."""
        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state

            if config.PRINT_STATE_CHANGES:
                logger.info(f"State: {self.previous_state} → {new_state}")

    def _brain_loop(self):
        """Main brain processing loop (runs in separate thread)."""
        logger.info("Brain loop started")

        # Set initial state
        self._set_state(config.STATE_LISTENING)
        self._update_gui_state(config.STATE_LISTENING, "Listening...")

        while self.running:
            try:
                # Check for voice input from listener
                if self.listener and self.listener.has_text():
                    text = self.listener.get_text(timeout=0.1)
                    if text:
                        self._process_input(text)

                # Check for manual commands from queue
                try:
                    command = self.command_queue.get_nowait()
                    self._process_input(command)
                except queue.Empty:
                    pass

                # Update GUI with Arduino peripherals
                if self.world_state and self.gui:
                    arduino_data = self.world_state.get('arduino')
                    if arduino_data and 'peripherals' in arduino_data:
                        self._update_gui_state('dummy_state', arduino_peripherals=arduino_data['peripherals'])

                # Small sleep to avoid busy waiting
                time.sleep(0.05)

            except Exception as e:
                logger.error(f"Brain loop error: {e}")
                time.sleep(1.0)

        logger.info("Brain loop stopped")

    def start(self):
        """Start the sentient core brain."""
        if self.running:
            logger.warning("Core already running")
            return

        logger.info("Starting Sentient Core brain...")
        self.running = True
        self.brain_thread = threading.Thread(target=self._brain_loop, daemon=True)
        self.brain_thread.start()
        logger.info("✓ Brain started")

    def stop(self):
        """Stop the sentient core."""
        if not self.running:
            return

        logger.info("Stopping Sentient Core...")
        self.running = False

        if self.brain_thread:
            self.brain_thread.join(timeout=2)

        logger.info("✓ Core stopped")

    def send_command(self, command: str):
        """
        Send a text command to the core (for testing/manual control).

        Args:
            command: Command text
        """
        self.command_queue.put(command)

    def get_stats(self):
        """Get core statistics."""
        return {
            'state': self.state,
            'running': self.running,
            'commands_processed': self.commands_processed,
            'last_command_time': self.last_command_time,
            'conversation_history_length': len(self.conversation_history)
        }


# Test function
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    print("=" * 60)
    print("Sentient Core Test")
    print("=" * 60)

    # Create core (without components for basic test)
    core = SentientCore()

    # Test command parsing
    test_commands = [
        "show me your sensors",
        "scan for frequencies",
        "how are you doing",
        "what's the temperature",
        "any threats detected",
        "this is a random phrase"
    ]

    print("\nTesting command parsing...\n")

    for cmd in test_commands:
        intent, confidence, entities = core._parse_command(cmd)
        response = core._generate_response(intent, entities)
        print(f"User: '{cmd}'")
        print(f"  → Intent: {intent} ({confidence:.1%})")
        print(f"  → Response: '{response}'")
        print()

    print("✓ Test complete")
