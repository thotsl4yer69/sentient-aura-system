#!/usr/bin/env python3
"""
Sentient Core v4 - Enhanced with API Integration
The brain of the Aura System with full internet connectivity.

This enhanced version integrates:
- LLM for intelligent conversation
- Web search for real-time information
- Weather API with sensor fusion
- Smart home control via Home Assistant
- PostgreSQL conversation memory
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import random
import logging
import threading
import queue
from typing import Dict, Optional

from sentient_aura import config

logger = logging.getLogger("sentient_core_enhanced")


class SentientCoreEnhanced:
    """
    Enhanced Sentient Core with API integration.

    Extends the original SentientCore with:
    - LLM-powered intelligent responses
    - Web search capabilities
    - Weather information
    - Smart home control
    - Conversation memory
    """

    def __init__(self, listener=None, voice=None, gui=None, world_state=None, daemons=None):
        """
        Initialize the Enhanced Sentient Core.

        Args:
            listener: ContinuousListener instance
            voice: VoicePiper instance
            gui: AuraInterface instance
            world_state: WorldState instance (shared with daemons)
            daemons: List of hardware daemons
        """
        logger.info("Initializing Enhanced Sentient Core with API Integration...")

        # Components
        self.listener = listener
        self.voice = voice
        self.gui = gui
        self.world_state = world_state
        self.daemons = daemons or []
        self.daemon_dict = {d.daemon_name: d for d in self.daemons}

        # State machine
        self.state = config.STATE_IDLE
        self.previous_state = None

        # Command queue
        self.command_queue = queue.Queue()

        # Threading
        self.running = False
        self.brain_thread = None

        # Stats
        self.commands_processed = 0
        self.last_command_time = 0

        # Conversation history (local cache)
        self.conversation_history = []

        # Command tracking
        self.active_commands = {}
        self.command_history = []
        self.next_command_id = 0

        # API Integration
        self.api_manager = None
        self._init_api_manager()

        logger.info("✓ Enhanced Sentient Core initialized")

    def _init_api_manager(self):
        """Initialize API Manager if enabled."""
        if not config.ENABLE_API_INTEGRATION:
            logger.info("API integration disabled in config")
            return

        try:
            from sentient_aura.api_manager import APIManager

            self.api_manager = APIManager(world_state=self.world_state)
            health = self.api_manager.health_check()

            logger.info(f"API Manager initialized:")
            logger.info(f"  LLM: {'✓' if health.llm_available else '✗'}")
            logger.info(f"  Search: {'✓' if health.search_available else '✗'}")
            logger.info(f"  Weather: {'✓' if health.weather_available else '✗'}")
            logger.info(f"  Home Assistant: {'✓' if health.homeassistant_available else '✗'}")
            logger.info(f"  Memory: {'✓' if health.memory_available else '✗'}")

        except Exception as e:
            logger.error(f"Failed to initialize API Manager: {e}")
            logger.warning("Running in offline mode")
            self.api_manager = None

    def _generate_command_id(self) -> str:
        """Generate unique command ID."""
        self.next_command_id += 1
        return f"CMD_{self.next_command_id:03d}"

    def _get_hardware_status(self) -> Dict[str, bool]:
        """Query current hardware status from WorldState."""
        if self.world_state is None:
            return {}

        try:
            capabilities = self.world_state.get('capabilities')
            if capabilities:
                return {
                    'camera_rgb': capabilities.get('vision', False),
                    'vision_daemon': capabilities.get('vision_daemon', False),
                    'flipper_zero': capabilities.get('rf_detection', False),
                    'prototype_board': capabilities.get('prototype_board', False),
                    'microphone': capabilities.get('audio', False),
                    'environment_sensors': capabilities.get('environment', False),
                }
            else:
                # Fallback: check active daemons
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

        # Enhanced keyword matching with more patterns
        enhanced_patterns = {
            'weather': ['weather', 'temperature', 'forecast', 'hot', 'cold', 'rain', 'sunny'],
            'search': ['search', 'look up', 'find information', 'tell me about', 'what is', 'who is'],
            'smart_home_on': ['turn on', 'switch on', 'activate', 'start', 'enable'],
            'smart_home_off': ['turn off', 'switch off', 'deactivate', 'stop', 'disable'],
            'smart_home_status': ['home status', 'smart home', 'devices', 'lights status'],
        }

        # Check enhanced patterns first
        for intent, patterns in enhanced_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    logger.debug(f"Matched enhanced intent: {intent} (pattern: '{pattern}')")
                    return (intent, 0.9, {'query': text})

        # Fall back to original command patterns
        for intent, patterns in config.COMMANDS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    logger.debug(f"Matched intent: {intent} (pattern: '{pattern}')")
                    return (intent, 0.9, {'query': text})

        # No match - use LLM for intent detection if available
        if config.USE_LLM_FOR_INTENT and self.api_manager and self.api_manager.llm:
            try:
                # Ask LLM to detect intent
                intent_query = f"What is the intent of this command? Respond with only one word: '{text}'"
                response = self.api_manager.chat(intent_query, stream=False)
                if response.is_success():
                    detected_intent = response.content.strip().lower()
                    logger.debug(f"LLM detected intent: {detected_intent}")
                    return (detected_intent, 0.7, {'query': text})
            except Exception as e:
                logger.debug(f"LLM intent detection failed: {e}")

        # Unknown intent
        return ('unknown', 0.0, {'query': text})

    def _generate_response(self, intent: str, entities: dict) -> str:
        """
        Generate response using LLM or template fallback.

        Args:
            intent: Command intent
            entities: Extracted entities

        Returns:
            str: Response text
        """
        query = entities.get('query', '')

        # Try LLM first if enabled and available
        if config.USE_LLM_FOR_RESPONSES and self.api_manager:
            try:
                # Build context-aware query
                context_parts = [query]

                # Add intent hint
                if intent != 'unknown':
                    context_parts.append(f"(This is a {intent} request)")

                # Add sensor data context
                if config.LLM_INJECT_SENSOR_CONTEXT and self.world_state:
                    env = self.world_state.get('environment')
                    if env and env.get('temperature'):
                        context_parts.append(f"Current temperature: {env['temperature']}°C")

                llm_query = " ".join(context_parts)

                # Get LLM response
                response = self.api_manager.chat(llm_query, stream=False)

                if response.is_success():
                    logger.info(f"LLM response generated (backend: {response.backend})")
                    return response.content

                elif config.LLM_FALLBACK_TO_TEMPLATES:
                    logger.warning("LLM failed, falling back to templates")
                else:
                    return "I'm having trouble thinking right now. Please try again."

            except Exception as e:
                logger.error(f"LLM response error: {e}")
                if not config.LLM_FALLBACK_TO_TEMPLATES:
                    return "I encountered an error processing your request."

        # If we get here without using LLM, check if fallbacks are allowed
        elif not config.LLM_FALLBACK_TO_TEMPLATES:
            # No LLM available and no fallbacks allowed - be honest
            return "I cannot respond without my cognitive capabilities. My LLM is currently unavailable."

        # Template-based responses (only if fallbacks explicitly allowed)
        return self._template_response(intent, entities)

    def _template_response(self, intent: str, entities: dict) -> str:
        """Generate template-based response (original behavior)."""
        ack = random.choice(config.ACKNOWLEDGMENTS)

        if intent == 'status' or intent == 'health':
            sensors = self._get_hardware_status()
            online = [name for name, available in sensors.items() if available]

            if len(online) == len(sensors):
                return "I'm feeling great! All my sensors are online and ready to go."
            elif len(online) > 0:
                return f"{ack} Most systems operational. {len(online)} sensors online."
            else:
                return "I'm running, but some sensors are offline."

        elif intent == 'weather':
            if self.api_manager and config.ENABLE_WEATHER_API:
                try:
                    weather_response = self.api_manager.get_weather()
                    if weather_response.is_success():
                        return self.api_manager.weather.summarize_weather(weather_response)
                except Exception as e:
                    logger.error(f"Weather API error: {e}")
            return "Weather information is currently unavailable."

        elif intent == 'search':
            if self.api_manager and config.ENABLE_WEB_SEARCH:
                query = entities.get('query', '').replace('search for', '').replace('search', '').strip()
                if query:
                    try:
                        search_response = self.api_manager.search(query, max_results=3)
                        if search_response.is_success():
                            return self.api_manager.search.summarize_results(search_response)
                    except Exception as e:
                        logger.error(f"Search error: {e}")
            return "Web search is currently unavailable."

        elif intent in ['smart_home_on', 'smart_home_off']:
            if self.api_manager and config.ENABLE_SMART_HOME_CONTROL:
                # Extract entity from query (simple pattern matching)
                query = entities.get('query', '').lower()
                # This is a simplified example - you'd want more robust entity extraction
                return f"{ack} I can help with smart home control. Please specify which device."
            return "Smart home control is currently unavailable."

        elif intent == 'smart_home_status':
            if self.api_manager:
                status = self.api_manager.get_smart_home_status()
                if status:
                    return status
            return "Smart home system is not available."

        elif intent == 'scan':
            if 'flipper' in self.daemon_dict:
                return f"{ack} Initiating RF spectrum scan now."
            return "RF scanning is not available. Flipper Zero is not connected."

        elif intent == 'help':
            capabilities = ["sensor status", "weather information", "web search"]
            if self.api_manager:
                if self.api_manager.homeassistant and self.api_manager.homeassistant.available:
                    capabilities.append("smart home control")
            return f"I can help you with: {', '.join(capabilities)}, and more!"

        elif intent == 'unknown':
            responses = [
                "I'm not sure I understood that. Could you try rephrasing?",
                "Hmm, I didn't quite catch that. What can I help you with?",
                "That's a new one for me! Can you ask that differently?",
            ]
            return random.choice(responses)

        else:
            return f"{ack} I'm working on it!"

    def _execute_command(self, intent: str, entities: dict):
        """
        Execute command action with API integration.

        Args:
            intent: Command intent
            entities: Extracted entities
        """
        logger.info(f"Executing command: {intent}")

        self._update_gui_state(config.STATE_EXECUTING, f"Executing: {intent}")

        try:
            if intent == 'status':
                sensors = self._get_hardware_status()
                if self.gui:
                    self.gui.state_queue.put({
                        'state': config.STATE_EXECUTING,
                        'text': 'Sensor Status',
                        'sensors': sensors,
                        'show_sensors': True
                    })
                time.sleep(0.5)

            elif intent == 'scan':
                self._execute_rf_scan()

            elif intent == 'weather':
                # Weather is handled in response generation
                pass

            elif intent == 'search':
                # Search is handled in response generation
                pass

            elif intent in ['smart_home_on', 'smart_home_off']:
                # Smart home control would be implemented here
                pass

        except Exception as e:
            logger.error(f"Command execution error: {e}")

    def _execute_rf_scan(self) -> dict:
        """Execute RF scan via Flipper daemon."""
        if 'flipper' not in self.daemon_dict:
            return {'success': False, 'error': 'Flipper daemon not available'}

        try:
            from sensor_events import ActionCommand

            command_id = self._generate_command_id()
            flipper = self.daemon_dict['flipper']

            scan_cmd = ActionCommand(
                target_daemon='flipper',
                action='scan',
                parameters={
                    'frequencies': ['2.4GHz', '5.8GHz', '433MHz', '915MHz'],
                    'command_id': command_id
                }
            )

            result = flipper.execute_action(scan_cmd)
            logger.info(f"RF scan initiated: {command_id}")

            result['command_id'] = command_id
            return result

        except Exception as e:
            logger.error(f"RF scan error: {e}")
            return {'success': False, 'error': str(e)}

    def _update_gui_state(self, state: str, text: str = "", **kwargs):
        """Update GUI state."""
        if self.gui:
            update = {'state': state, 'text': text}
            update.update(kwargs)
            self.gui.state_queue.put(update)

    def _process_input(self, text: str):
        """
        Process voice input through the enhanced pipeline.

        Args:
            text: Transcribed text from listener
        """
        logger.info(f"Processing input: '{text}'")
        self.commands_processed += 1
        self.last_command_time = time.time()

        # Add to local history
        self.conversation_history.append({
            'timestamp': time.time(),
            'user': text,
            'response': None
        })

        # Store in database if memory is enabled
        if self.api_manager and config.ENABLE_CONVERSATION_MEMORY:
            self.api_manager.remember_conversation("user", text)

        # LISTENING → PROCESSING
        self._set_state(config.STATE_PROCESSING)
        self._update_gui_state(config.STATE_PROCESSING, "Thinking...")

        # Parse command
        intent, confidence, entities = self._parse_command(text)
        logger.info(f"Intent: {intent} (confidence: {confidence})")

        # Generate response (may use LLM)
        response = self._generate_response(intent, entities)
        logger.info(f"Response: '{response[:100]}...'")

        # Update history
        self.conversation_history[-1]['response'] = response

        # Store assistant response in memory
        if self.api_manager and config.ENABLE_CONVERSATION_MEMORY:
            self.api_manager.remember_conversation("assistant", response, intent=intent)

        # PROCESSING → SPEAKING
        self._set_state(config.STATE_SPEAKING)
        self._update_gui_state(config.STATE_SPEAKING, "Speaking...", transcription=response)

        # Speak response
        if self.voice:
            self.voice.speak(response, blocking=True)

        # SPEAKING → EXECUTING (if command needs action)
        if intent in ['scan', 'status', 'smart_home_on', 'smart_home_off']:
            self._set_state(config.STATE_EXECUTING)
            self._execute_command(intent, entities)

        # EXECUTING → IDLE
        self._set_state(config.STATE_IDLE)
        self._update_gui_state(config.STATE_LISTENING, "Listening...")

        # Trim local history
        if len(self.conversation_history) > config.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-config.MAX_CONVERSATION_HISTORY:]

    def _set_state(self, new_state: str):
        """Update the core's state."""
        if new_state != self.state:
            self.previous_state = self.state
            self.state = new_state

            if config.PRINT_STATE_CHANGES:
                logger.info(f"State: {self.previous_state} → {new_state}")

    def _brain_loop(self):
        """Main brain processing loop."""
        logger.info("Brain loop started")

        self._set_state(config.STATE_LISTENING)
        self._update_gui_state(config.STATE_LISTENING, "Listening...")

        while self.running:
            try:
                # Check for voice input
                if self.listener and self.listener.has_text():
                    text = self.listener.get_text(timeout=0.1)
                    if text:
                        self._process_input(text)

                # Check for manual commands
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

                time.sleep(0.05)

            except Exception as e:
                logger.error(f"Brain loop error: {e}")
                time.sleep(1.0)

        logger.info("Brain loop stopped")

    def start(self):
        """Start the sentient core."""
        if self.running:
            logger.warning("Core already running")
            return

        logger.info("Starting Enhanced Sentient Core...")
        self.running = True
        self.brain_thread = threading.Thread(target=self._brain_loop, daemon=True)
        self.brain_thread.start()
        logger.info("✓ Enhanced Core started")

    def stop(self):
        """Stop the sentient core."""
        if not self.running:
            return

        logger.info("Stopping Enhanced Sentient Core...")
        self.running = False

        if self.brain_thread:
            self.brain_thread.join(timeout=2)

        # Shutdown API manager
        if self.api_manager:
            self.api_manager.shutdown()

        logger.info("✓ Enhanced Core stopped")

    def send_command(self, command: str):
        """Send a text command to the core."""
        self.command_queue.put(command)

    def get_stats(self):
        """Get core statistics."""
        stats = {
            'state': self.state,
            'running': self.running,
            'commands_processed': self.commands_processed,
            'last_command_time': self.last_command_time,
            'conversation_history_length': len(self.conversation_history),
        }

        if self.api_manager:
            stats['api_health'] = self.api_manager.health_check().to_dict()
            stats['api_stats'] = self.api_manager.get_detailed_stats()

        return stats


# Maintain backward compatibility
SentientCore = SentientCoreEnhanced
