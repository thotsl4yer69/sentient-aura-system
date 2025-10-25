#!/usr/bin/env python3
"""
Sentient Core - Arduino Daemon
Communicates with an Arduino board for sensor readings and peripheral control.
"""

import time
import logging
import serial
import os
from typing import Optional, Dict, Any, List
from daemon_base import BaseDaemon
from world_state import WorldState
from sensor_events import SensorEvent, ActionCommand
from hardware.serial_port_manager import get_serial_port_manager

class ArduinoDaemon(BaseDaemon):
    """
    Arduino communication and control daemon.
    """

    def __init__(self, world_state: WorldState, update_rate: float = 1.0, debug=False):
        """
        Initialize Arduino daemon.

        Args:
            world_state: Central world state
            update_rate: How often to read from the Arduino (in Hz)
            debug: Enable debug logging
        """
        super().__init__("arduino", world_state, update_rate)
        self.serial_port = None
        self.serial_conn = None
        self.peripherals = {}
        self.debug = debug

    def initialize(self) -> bool:
        """
        Initialize Arduino serial connection and discover peripherals.

        Returns:
            True if Arduino is connected and ready
        """
        self.logger.info("Initializing Arduino daemon...")

        # Check if Arduino is available
        capabilities = self.world_state.get("capabilities")
        if not capabilities or not capabilities.get("arduino"):
            self.logger.error("Arduino not found in hardware discovery.")
            return False

        # Try common Arduino ports
        self.serial_port = "/dev/ttyACM0"
        if not os.path.exists(self.serial_port):
            self.serial_port = "/dev/ttyUSB0"
            if not os.path.exists(self.serial_port):
                self.logger.error(f"Arduino port not found at /dev/ttyACM0 or /dev/ttyUSB0")
                return False

        try:
            self.logger.info(f"Attempting to connect to Arduino on {self.serial_port}")

            # Use SerialPortManager for exclusive access
            manager = get_serial_port_manager()
            if not manager.acquire(self.serial_port, owner="ArduinoDaemon", timeout=5.0):
                self.logger.error(f"Failed to acquire lock on {self.serial_port}")
                return False

            self.serial_conn = manager.open(self.serial_port, baudrate=115200, timeout=1)
            if not self.serial_conn:
                manager.release(self.serial_port)
                self.logger.error(f"Failed to open serial connection on {self.serial_port}")
                return False

            time.sleep(2)  # Wait for the Arduino to reset
            self.logger.info(f"✓ Arduino connected on {self.serial_port} (lock acquired)")
            self.discover_peripherals()
            self.world_state.update("arduino", {"status": "active", "port": self.serial_port, "peripherals": self.peripherals})
            return True
        except (serial.SerialException, TimeoutError) as e:
            self.logger.error(f"Failed to connect to Arduino on {self.serial_port}: {e}")
            # Ensure lock is released on error
            manager = get_serial_port_manager()
            manager.release(self.serial_port)
            return False

    def discover_peripherals(self):
        """
        Ask the Arduino to list its peripherals.
        """
        if not self.serial_conn:
            return

        self.logger.info("Discovering Arduino peripherals...")
        try:
            self.serial_conn.write(b"discover\n")
            self.logger.info("Sent 'discover' command to Arduino")
            time.sleep(2) # Give Arduino more time to respond
            raw_data = self.serial_conn.read_all().decode('utf-8')
            if self.debug:
                self.logger.info(f"Arduino raw response:\n---\n{raw_data}\n---")

            for line in raw_data.splitlines():
                line = line.strip()
                if line.startswith("PERIPHERAL:"):
                    try:
                        _, name, pin, p_type = line.split(':')
                        self.peripherals[name] = {"pin": int(pin), "type": p_type, "value": None}
                        self.logger.info(f"  > Discovered: {name} ({p_type} on pin {pin})")
                    except ValueError as e:
                        self.logger.error(f"Error parsing peripheral line: {line} - {e}")

            self.logger.info(f"✓ Discovered {len(self.peripherals)} peripherals")
            if not self.peripherals:
                self.logger.warning("No peripherals discovered. Check Arduino sketch and connection.")

        except serial.SerialException as e:
            self.logger.error(f"Error discovering peripherals: {e}")

    def update(self) -> None:
        """
        Main update cycle - read data from Arduino.
        """
        if not self.serial_conn:
            return

        try:
            # Request readings for all sensors
            for name, props in self.peripherals.items():
                if props["type"] == "sensor":
                    self.execute_action(ActionCommand(self.daemon_name, "read", {"name": name}))

            # Read any incoming data
            while self.serial_conn.in_waiting > 0:
                line = self.serial_conn.readline().decode('utf-8').rstrip()
                self.parse_arduino_message(line)

        except serial.SerialException as e:
            self.logger.error(f"Error reading from Arduino: {e}")
            self.cleanup()

    def parse_arduino_message(self, line):
        """
        Parse a message from the Arduino and update the world state.
        """
        self.logger.debug(f"Arduino <<< {line}")
        parts = line.split(':')
        if not parts or len(parts) < 2:
            return

        msg_type = parts[0]
        name = parts[1]

        if msg_type == "SENSOR_VALUE" and len(parts) >= 3:
            value = parts[2]
            if name in self.peripherals:
                self.peripherals[name]["value"] = value
                self.world_state.update_nested(f"arduino.peripherals.{name}.value", value)

        elif msg_type == "BUTTON_STATE" and len(parts) >= 3:
            value = parts[2]
            if name in self.peripherals:
                self.peripherals[name]["value"] = value
                self.world_state.update_nested(f"arduino.peripherals.{name}.value", value)

        elif msg_type == "WRITE_OK" and len(parts) >= 3:
            value = parts[2]
            if name in self.peripherals:
                self.peripherals[name]["value"] = value
                self.world_state.update_nested(f"arduino.peripherals.{name}.value", value)

    def execute_action(self, action: ActionCommand) -> Dict[str, Any]:
        """
        Execute an action command on the Arduino.
        """
        if not self.serial_conn:
            return {"success": False, "error": "Arduino not connected"}

        command = action.action
        params = action.parameters or {}
        name = params.get("name")

        if not name:
            return {"success": False, "error": "'name' parameter is required"}

        if command == "read":
            full_command = f"read:{name}\n"
        elif command == "write":
            value = params.get("value")
            if value is None:
                return {"success": False, "error": "'value' parameter is required for write"}
            full_command = f"write:{name}:{value}\n"
        else:
            return {"success": False, "error": f"Unknown command: {command}"}

        try:
            self.serial_conn.write(full_command.encode('utf-8'))
            self.logger.info(f"Sent to Arduino: {full_command.strip()}")
            return {"success": True, "command": command, "params": params}
        except serial.SerialException as e:
            self.logger.error(f"Error writing to Arduino: {e}")
            return {"success": False, "error": str(e)}

    def cleanup(self) -> None:
        """
        Clean up Arduino connection and release port lock.
        """
        self.logger.info("Shutting down Arduino daemon...")
        if self.serial_port:
            # SerialPortManager.release() will close connection AND release lock
            manager = get_serial_port_manager()
            manager.release(self.serial_port)
            self.logger.info(f"✓ Arduino serial connection closed and lock released on {self.serial_port}")
        self.serial_conn = None


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    ws = WorldState()
    # Manually add arduino capability for testing
    ws.update("capabilities", {"arduino": {"available": True, "address": "/dev/ttyACM0"}})
    
    daemon = ArduinoDaemon(ws, update_rate=1.0)

    if not daemon.initialize():
        print("✗ Initialization failed - check if Arduino is connected")
        sys.exit(1)

    print("\n✓ Daemon initialized")
    print("✓ Ready to send/receive data from Arduino...")
    print("\nPress Ctrl+C to stop\n")

    # Example of sending a command
    # test_action = ActionCommand("arduino", "led", {"state": 1})
    # daemon.execute_action(test_action)

    try:
        while True:
            daemon.update()
            time.sleep(daemon.update_interval)
    except KeyboardInterrupt:
        daemon.cleanup()