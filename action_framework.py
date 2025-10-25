#!/usr/bin/env python3
"""
Sentient Core - Action Framework
Manages and executes physical actions based on commands from the Mind.
CRITICAL UPDATE: Arbitrary shell execution removed for security.
"""

import logging
import time
from world_state import WorldState

class ActionFramework:
    """
    Executes actions on the Core.
    """

    def __init__(self, world_state: WorldState, voice_output, daemon_manager):
        self.logger = logging.getLogger("action_framework")
        self.world_state = world_state
        self.voice_output = voice_output
        self.daemon_manager = daemon_manager # To delegate actions to daemons
        self.actions = {
            "speak": self._speak,
            "conserve_power": self._conserve_power,
            "reboot_system": self._reboot_system,
            "engage_jammer": self._engage_jammer,
            "read_peripheral": self._read_peripheral,
            "write_peripheral": self._write_peripheral,
        }

    def execute_action(self, action_command: dict):
        """
        Execute a given action command.
        """
        action_name = action_command.get("action")
        payload = action_command.get("payload", {})

        if action_name in self.actions:
            self.logger.info(f"Executing action: {action_name} with payload: {payload}")
            try:
                self.actions[action_name](payload)
                self.world_state.update("decisions", {"last_action": action_name, "last_action_timestamp": time.time()})
            except Exception as e:
                self.logger.error(f"Error executing action {action_name}: {e}")
        else:
            self.logger.warning(f"Unknown or unauthorized action requested: {action_name}")

    def _speak(self, payload: dict):
        text = payload.get("text")
        if text:
            self.voice_output.speak(text)
        else:
            self.logger.warning("Speak action called without text payload.")

    def _conserve_power(self, payload: dict):
        self.logger.warning("Initiating power conservation mode across all daemons.")
        for daemon in self.daemon_manager.daemons:
            if hasattr(daemon, 'conserve_power'):
                daemon.conserve_power()
        self.world_state.update("system", {"power_mode": "conserve"})

    def _reboot_system(self, payload: dict):
        self.logger.critical("Mind requested system reboot. Initiating controlled shutdown.")
        # In a single-process system, this would trigger a system-wide shutdown flag
        self.world_state.update("system", {"status": "reboot_pending"})

    def _engage_jammer(self, payload: dict):
        target = payload.get("target")
        protocol = payload.get("protocol", "default")
        self.logger.critical(f"Mind requested jammer engagement: Target={target}, Protocol={protocol}")
        
        flipper_daemon = self.daemon_manager.get_daemon("flipper")
        if flipper_daemon and hasattr(flipper_daemon, 'engage_jammer'):
            flipper_daemon.engage_jammer(target, protocol)
        else:
            self.logger.error("Flipper Daemon not found or does not support jamming.")

    def _read_peripheral(self, payload: dict):
        name = payload.get("name")
        arduino_daemon = self.daemon_manager.get_daemon("arduino")
        if arduino_daemon and hasattr(arduino_daemon, 'execute_action'):
            arduino_daemon.execute_action({"action": "read", "name": name})
        else:
            self.logger.error("Arduino Daemon not found.")

    def _write_peripheral(self, payload: dict):
        name = payload.get("name")
        value = payload.get("value")
        arduino_daemon = self.daemon_manager.get_daemon("arduino")
        if arduino_daemon and hasattr(arduino_daemon, 'execute_action'):
            arduino_daemon.execute_action({"action": "write", "name": name, "value": value})
        else:
            self.logger.error("Arduino Daemon not found.")